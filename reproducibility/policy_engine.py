"""Independent, standard-library implementation of frozen after_07d rules."""
import csv
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
LEVELS = {'low': 1, 'medium': 2, 'high': 3}
LABELS = {v: k for k, v in LEVELS.items()}
FLOAT_FIELDS = ['A', 'Iv', 'Ha', 'Rl_content', 'base_score_refined',
                'role_claim', 'relation_claim', 'qualification_claim', 'regulator_claim',
                'court_claim', 'PTFa_final']
EXACT_FIELDS = ['base_high_floor_applied_refined', 'base_data_level_pred_refined',
                'PTFa_level_final', 'required_auth_level_final', 'proof_mode_final']


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def read_json(path):
    with Path(path).open(encoding='utf-8-sig') as stream:
        return json.load(stream)


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def write_json(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def write_csv(path, records, fields):
    with Path(path).open('x', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def output_directory(value, default):
    path = Path(value) if value else HERE / 'reports' / default
    path = path.resolve()
    reports = (HERE / 'reports').resolve()
    data = (PACKAGE / 'processed_data').resolve()
    if path == HERE or path == PACKAGE or path == data or data in path.parents or (HERE in path.parents and reports not in path.parents):
        raise ValueError('Output must not be the package root or an input/code directory')
    if path.exists() and any(path.iterdir()):
        raise ValueError('Output directory is nonempty; refusing overwrite')
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_config(config):
    required = ['config_version', 'sensitivity_weights', 'sensitivity_thresholds',
                'high_sensitivity_override', 'ptfa_weights', 'ptfa_thresholds',
                'output_scope_aliases', 'output_scope_semantics', 'conditional_aggregation_rules',
                'level_to_proof_mode', 'base_only_rule', 'without_ptfa_rule',
                'without_output_scope_rule', 'fixed_strong_rule', 'original_source_references',
                'level_numeric_mapping', 'sensitivity_components', 'ptfa_activation_rules']
    missing = sorted(set(required) - config.keys())
    if missing:
        raise ValueError('Missing configuration keys: ' + ', '.join(missing))
    weights = config['sensitivity_weights']
    if set(weights) != {'A', 'Iv', 'Ha', 'Rl_content'}:
        raise ValueError('Invalid sensitivity component names')
    for weights_to_check in [weights, config['ptfa_weights']]:
        if any(not math.isfinite(v) or v < 0 for v in weights_to_check.values()):
            raise ValueError('Invalid weight')
    if abs(sum(weights.values()) - 1.) > 1e-12:
        raise ValueError('Sensitivity weights must sum to one')
    if set(config['ptfa_weights']) != set(FLOAT_FIELDS[5:10]):
        raise ValueError('PTFa requires the five original claim factors')
    # PTFa weights intentionally sum to 1.25; the original formula clips at 1.
    for thresholds in [config['sensitivity_thresholds'], config['ptfa_thresholds']]:
        if not 0 <= thresholds['low'] < thresholds['high'] <= 1:
            raise ValueError('Invalid thresholds')
    if config['base_only_rule']['operation'] != 'identity_base_level':
        raise ValueError('Unsupported Base-only operation')
    if config['without_output_scope_rule']['operation'] != 'max_base_ptfa':
        raise ValueError('Unsupported no-scope operation')
    if config['fixed_strong_rule']['level'] != 'high':
        raise ValueError('Invalid Fixed Strong definition')
    if config['predicate_floor']['status'] != 'NOT_VERIFIABLE':
        raise ValueError('This release does not implement an unevidenced predicate floor')


def load_bundle():
    manifest = read_json(HERE / 'input_manifest.json')
    for record in manifest['files']:
        relative = Path(record['path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Invalid manifest path')
        path = PACKAGE / relative
        if path.stat().st_size != record['size_bytes'] or sha(path) != record['sha256']:
            raise ValueError('Frozen input hash mismatch: ' + relative.as_posix())
    config = read_json(HERE / 'policy_config.json')
    validate_config(config)
    paths = config['input_files']
    inputs = {name: read_csv(PACKAGE / rel) for name, rel in paths.items()}
    expected = read_json(HERE / 'expected_results.json')
    for name in ['test', 'refined_test', 'final_test']:
        if len(inputs[name]) != expected['test_rows']:
            raise ValueError('Frozen test row count mismatch: ' + name)
    ids = [r['collision_index'] for r in inputs['test']]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate test identifiers')
    for name in ['refined_test', 'final_test']:
        if [r['collision_index'] for r in inputs[name]] != ids:
            raise ValueError('Frozen row-order mismatch: ' + name)
    return config, inputs, expected


def condition_matches(condition, variables):
    kind = condition['kind']
    if kind == 'all':
        return all(condition_matches(item, variables) for item in condition['items'])
    if kind == 'any':
        return any(condition_matches(item, variables) for item in condition['items'])
    if kind == 'not':
        return not condition_matches(condition['item'], variables)
    if kind == 'always':
        return True
    value = variables[condition['field']]
    if kind == 'contains_any':
        return any(keyword in str(value) for keyword in condition['keywords'])
    if kind == 'numeric_equals':
        return str(value) != '' and float(value) == condition['value']
    if kind == 'equals':
        return value == condition['value']
    if kind == 'in':
        return value in condition['values']
    raise ValueError('Unknown condition kind: ' + kind)


def activate_claims(row, config):
    variables = dict(row)
    for key, field in config['ptfa_text_inputs'].items():
        variables[key] = row[field]
    variables['all_text'] = '|'.join(variables[key] for key in config['ptfa_join_order'])
    claims = {field: 0. for field in config['ptfa_weights']}

    def apply(rule):
        if condition_matches(rule['when'], variables):
            for assignment in rule['then']:
                target = assignment['target']
                claims[target] = max(claims[target], assignment['value'])
        else:
            for alternative in rule.get('else', []):
                apply(alternative)

    for rule in config['ptfa_activation_rules']:
        apply(rule)
    return claims


def numeric_component(row, spec, config):
    values = []
    if spec.get('severity'):
        values.append(config['severity_mapping'].get(row['collision_severity'], config['severity_default']))
    for field in spec.get('mapped_fields', []):
        values.append(config['level_numeric_mapping'].get(row[field], 0.))
    for flag in spec.get('flags', []):
        values.append(flag['score'] if float(row[flag['field']]) == flag['equals'] else 0.)
    return max(values)


def score_level(score, thresholds):
    return 'low' if score < thresholds['low'] else ('high' if score >= thresholds['high'] else 'medium')


def canonical_scope(scope, config):
    scope = str(scope).strip()
    if scope not in config['output_scope_aliases']:
        raise ValueError('Unknown output scope: ' + scope)
    return config['output_scope_aliases'][scope]


def apply_ordered_rules(rules, variables):
    result = rules['default']
    for rule in rules['ordered_assignments']:
        if condition_matches(rule['when'], variables):
            result = rule['level']
    return result


def full_policy(base, ptfa, scope, config):
    variables = dict(base=base, ptfa=ptfa, scope=canonical_scope(scope, config))
    return apply_ordered_rules(config['conditional_aggregation_rules'], variables)


def no_ptfa_policy(base, scope, config):
    # There is deliberately no PTFa argument or PTFa lookup.
    return apply_ordered_rules(config['without_ptfa_rule'], dict(base=base, scope=canonical_scope(scope, config)))


def no_scope_policy(base, ptfa, config):
    # There is deliberately no scope argument or scope lookup.
    if config['without_output_scope_rule']['operation'] != 'max_base_ptfa':
        raise ValueError('Unsupported no-scope rule')
    return LABELS[max(LEVELS[base], LEVELS[ptfa])]


def recompute_request(row, config):
    result = {'collision_index': row['collision_index']}
    for name, spec in config['sensitivity_components'].items():
        result[name] = numeric_component(row, spec, config)
    result['base_score_refined'] = sum(config['sensitivity_weights'][name] * result[name]
                                       for name in ['A', 'Iv', 'Ha', 'Rl_content'])
    base = score_level(result['base_score_refined'], config['sensitivity_thresholds'])
    triggered = any(condition_matches(item['when'], row) for item in config['high_sensitivity_override']['conditions'])
    result['base_high_floor_applied_refined'] = int(triggered)
    result['base_data_level_pred_refined'] = 'high' if triggered else base
    result.update(activate_claims(row, config))
    result['PTFa_final'] = min(1., sum(config['ptfa_weights'][key] * result[key] for key in config['ptfa_weights']))
    result['PTFa_level_final'] = score_level(result['PTFa_final'], config['ptfa_thresholds'])
    result['required_auth_level_final'] = full_policy(result['base_data_level_pred_refined'],
        result['PTFa_level_final'], row['output_scope'], config)
    result['proof_mode_final'] = config['level_to_proof_mode'][result['required_auth_level_final']]
    return result


def compare_rows(calculated, reference, fields, target, tolerance):
    summary = []; differences = []
    for field in fields:
        count = 0; max_error = 0.
        for i, (new, old) in enumerate(zip(calculated, reference), 1):
            if field in FLOAT_FIELDS:
                error = abs(float(new[field]) - float(old[field]))
                max_error = max(max_error, error)
                equal = math.isfinite(error) and error <= tolerance
            elif field == 'base_high_floor_applied_refined':
                error = None
                equal = int(new[field]) == int(old[field])
            else:
                error = None
                equal = str(new[field]) == str(old[field])
            if not equal:
                count += 1
                differences.append(dict(row_number=i, collision_index=new['collision_index'], target=target,
                    field=field, actual=new[field], reference=old[field], absolute_error=error))
        summary.append(dict(target=target, field=field, row_count=len(calculated), difference_rows=count,
                            tolerance=tolerance if field in FLOAT_FIELDS else 0, max_absolute_error=max_error if field in FLOAT_FIELDS else None))
    return summary, differences


def decisions(config, inputs):
    calculated = [recompute_request(row, config) for row in inputs['test']]
    summary, differences = compare_rows(calculated, inputs['final_test'], FLOAT_FIELDS + EXACT_FIELDS,
                                        'frozen_final', config['float_tolerance'])
    claim_summary, claim_diff = compare_rows(calculated, inputs['refined_test'], list(config['ptfa_weights']),
                                            'frozen_refined_claims', config['float_tolerance'])
    return calculated, summary + claim_summary, differences + claim_diff


def mode_counts(level_values, config):
    counter = Counter(config['level_to_proof_mode'][x] for x in level_values)
    return {mode: counter[mode] for mode in ['basic', 'medium', 'strong']}


def transition_matrix(source, destination):
    counts = Counter(zip(source, destination))
    return [dict(from_level=a, to_level=b, count=counts[(a,b)]) for a in LEVELS for b in LEVELS]


def base_transition(calculated):
    return transition_matrix([r['base_data_level_pred_refined'] for r in calculated],
                             [r['required_auth_level_final'] for r in calculated])


def change_summary(source, destination):
    return dict(upgraded=sum(LEVELS[b] > LEVELS[a] for a,b in zip(source,destination)),
                downgraded=sum(LEVELS[b] < LEVELS[a] for a,b in zip(source,destination)),
                unchanged=sum(a == b for a,b in zip(source,destination)))


def ablations(calculated, test, config):
    variants = {name: [] for name in ['Full', 'Base-only', 'w/o L_ptfa', 'w/o L_out', 'Fixed Strong']}
    for row, request in zip(calculated, test):
        a, b = row['base_data_level_pred_refined'], row['PTFa_level_final']
        values = {'Full': row['required_auth_level_final'], 'Base-only': a,
                  'w/o L_ptfa': no_ptfa_policy(a, request['output_scope'], config),
                  'w/o L_out': no_scope_policy(a, b, config), 'Fixed Strong': config['fixed_strong_rule']['level']}
        for name, value in values.items():
            variants[name].append(value)
    full = variants['Full']; summaries=[]; all_rows=[]; transitions=[]; reverse=[]
    for name, levels in variants.items():
        change = change_summary(full, levels)
        summaries.append(dict(policy=name, total_rows=len(levels), **mode_counts(levels,config),
            weaker_than_full=change['downgraded'], stronger_than_full=change['upgraded'],
            unchanged=change['unchanged'], weaker_rate=change['downgraded']/len(levels), stronger_rate=change['upgraded']/len(levels)))
        for item in transition_matrix(full, levels):
            transitions.append(dict(policy=name, direction='Full_to_variant', **item))
        for i,(row,request,actual,baseline) in enumerate(zip(calculated,test,levels,full),1):
            direction = 'weaker' if LEVELS[actual]<LEVELS[baseline] else ('stronger' if LEVELS[actual]>LEVELS[baseline] else 'unchanged')
            item=dict(row_number=i,collision_index=row['collision_index'],policy=name,
                      base=row['base_data_level_pred_refined'],ptfa=row['PTFa_level_final'],
                      scope_stored=request['output_scope'],scope_semantic=canonical_scope(request['output_scope'],config),
                      access_task_type=request['access_task_type'],Full=baseline,variant=actual,direction=direction)
            all_rows.append(item)
            if name=='w/o L_out' and direction=='stronger':
                reverse.append(item)
    return summaries, all_rows, transitions, reverse
