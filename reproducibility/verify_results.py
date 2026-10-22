"""One-command offline acceptance. Missing evidence remains NOT_VERIFIABLE."""
import argparse
import itertools
import json
import sys
sys.dont_write_bytecode = True
from policy_engine import (HERE, LEVELS, LABELS, read_csv, read_json, write_csv, write_json,
    load_bundle, output_directory, decisions, full_policy, no_scope_policy, mode_counts,
    base_transition, change_summary, ablations, compare_rows, score_level)


def run(output=None):
    out=output_directory(output,'verification')
    checks=[]

    def check(name,passed,details):
        checks.append(dict(check=name,status='PASS' if passed else 'FAIL',details=details))

    try:
        config,inputs,expected=load_bundle()
        check('frozen_hashes_and_configuration',True,'All input SHA-256/size checks and schema/weight/threshold checks passed.')
        check('parameter_source_values',
            config['sensitivity_weights']==expected['parameter_reference']['sensitivity_weights'] and
            config['sensitivity_thresholds']==expected['parameter_reference']['sensitivity_thresholds'] and
            config['ptfa_weights']==expected['parameter_reference']['ptfa_weights'] and
            config['ptfa_thresholds']==expected['parameter_reference']['ptfa_thresholds'],
            'Configuration compared with the unmodified source parameter JSON values recorded independently.')
        raw_base=read_json(HERE/'parameters/refined_best_params.json')['base_params']
        raw_ptfa=read_json(HERE/'parameters/ptfa_standalone_v2_best_params.json')['ptfa_params']
        check('original_parameter_json_agreement',
            [config['sensitivity_weights'][k] for k in ['A','Iv','Ha','Rl_content']]==[raw_base[k] for k in ['w_A','w_Iv','w_Ha','w_Rl']] and
            [config['ptfa_weights'][k] for k in config['ptfa_weights']]==[raw_ptfa[k] for k in ['ptf_w_role','ptf_w_relation','ptf_w_qualification','ptf_w_regulator','ptf_w_court']] and
            config['sensitivity_thresholds']==dict(low=raw_base['base_low_threshold'],high=raw_base['base_high_threshold']) and
            config['ptfa_thresholds']==dict(low=raw_ptfa['ptf_low_threshold'],high=raw_ptfa['ptf_high_threshold']),
            'Final PTFa uses V2 values, not the earlier refined PTFa block.')
        mapping=read_csv(HERE/'full_policy_mapping.csv')
        combinations={(r['L_base'],r['L_ptfa'],r['scope_stored']) for r in mapping}
        expected_combinations=set(itertools.product(LEVELS,LEVELS,config['historical_scopes']))
        check('complete_27_mapping',len(mapping)==27 and combinations==expected_combinations and all(
            full_policy(r['L_base'],r['L_ptfa'],r['scope_stored'],config)==r['auth_level'] for r in mapping),
            'Every enumerated legal type combination is checked against the source-derived reference mapping.')
        alias_checks=[]
        for row in mapping:
            alias_checks.append(full_policy(row['L_base'],row['L_ptfa'],row['scope_stored'],config)==
                full_policy(row['L_base'],row['L_ptfa'],row['scope_semantic'],config))
        check('scope_alias_equivalence',all(alias_checks),'Both names tested for every base/PTFa combination; unknown names are rejected.')
        try:
            full_policy('low','low','unsupported_scope',config)
            rejected=False
        except ValueError:
            rejected=True
        check('unknown_scope_rejected',rejected,'The valid domain is explicit, not the historical unknown-value fallback.')
        check('base_dominance',all(LEVELS[r['auth_level']]>=LEVELS[r['L_base']] for r in mapping),'Agg(a,b,c)>=a for all 27 combinations.')
        math=[]
        for dimension,domain in enumerate([list(LEVELS),list(LEVELS),config['historical_scopes']]):
            for combination in itertools.product(LEVELS,LEVELS,config['historical_scopes']):
                for next_value in domain[domain.index(combination[dimension])+1:]:
                    other=list(combination);other[dimension]=next_value
                    before=full_policy(*combination,config);after=full_policy(*other,config)
                    math.append(dict(dimension=['base','ptfa','output_risk'][dimension],before=str(combination),
                        after=str(tuple(other)),auth_before=before,auth_after=after,monotone=LEVELS[after]>=LEVELS[before]))
        violations={dim:sum(r['dimension']==dim and not r['monotone'] for r in math) for dim in ['base','ptfa','output_risk']}
        check('known_mathematical_properties',violations==expected['monotonicity_violations'],dict(
            observed_violations=violations,note='Base monotonicity is known to fail; this check preserves that fact rather than claiming monotonicity.'))
        write_csv(out/'monotonicity_checks.csv',math,list(math[0]))
        boundary_ok=all(score_level(t['low']-1e-8,t)=='low' and score_level(t['low'],t)=='medium' and score_level(t['high'],t)=='high'
                        for t in [config['sensitivity_thresholds'],config['ptfa_thresholds']])
        check('threshold_boundaries',boundary_ok,'Strict low comparison and inclusive high comparison.')
        full=inputs['full'];tune=inputs['tune'];test=inputs['test']
        full_ids={r['collision_index'] for r in full};tune_ids={r['collision_index'] for r in tune};test_ids={r['collision_index'] for r in test}
        split_ok=len(full)==expected['full_rows'] and len(tune)==expected['tune_rows'] and len(test)==expected['test_rows']
        split_ok=split_ok and len(full_ids)==len(full) and len(tune_ids)==len(tune) and not tune_ids&test_ids and tune_ids|test_ids==full_ids
        full_by_id={r['collision_index']:r for r in full}
        split_ok=split_ok and all(full_by_id[r['collision_index']]==r for r in tune+test)
        check('fixed_split',split_ok,'Full/tune/test identifiers, disjointness, row content and preserved split markers.')
        calculated,comparisons,differences=decisions(config,inputs)
        write_csv(out/'field_comparison.csv',comparisons,list(comparisons[0]))
        write_csv(out/'row_differences.csv',differences,['row_number','collision_index','target','field','actual','reference','absolute_error'])
        check('row_level_decisions_and_claims',not differences,dict(rows=len(calculated),difference_cells=len(differences),tolerance=config['float_tolerance']))
        # A deliberate in-memory reference error must be detected, without modifying any file.
        changed_reference=dict(inputs['final_test'][0])
        changed_reference['required_auth_level_final']='low' if calculated[0]['required_auth_level_final']!='low' else 'high'
        _,negative=compare_rows(calculated[:1],[changed_reference],['required_auth_level_final'],'negative_control',config['float_tolerance'])
        check('comparison_detects_reference_error',len(negative)==1,'An in-memory incorrect reference is detected; no frozen input is changed.')
        if differences:
            check('dependent_statistics_not_accepted',False,'Stop: row-level mismatch; no ablation acceptance.')
        else:
            a=[r['base_data_level_pred_refined'] for r in calculated];p=[r['required_auth_level_final'] for r in calculated]
            distributions=dict(Full=mode_counts(p,config),Base_only=mode_counts(a,config))
            check('proof_mode_distributions',distributions==expected['distributions'],distributions)
            changes=change_summary(a,p)
            matrix=base_transition(calculated)
            check('base_to_full_changes',changes==expected['base_to_full_changes'],changes)
            check('base_to_full_transition_matrix',matrix==expected['base_to_full_transition'],matrix)
            summaries,rows,transitions,reverse=ablations(calculated,inputs['test'],config)
            for summary in summaries:
                name=summary['policy']
                if name in expected['ablations']:
                    actual={k:summary[k] for k in expected['ablations'][name]}
                    check('ablation_'+name,actual==expected['ablations'][name],actual)
            reverse_condition=all(r['base']=='low' and r['ptfa']=='high' and r['scope_semantic']=='summary_view' and r['Full']=='medium' and r['variant']=='high' for r in reverse)
            check('reverse_scope_upgrade_conditions',len(reverse)==expected['reverse_scope_upgrades'] and reverse_condition,
                  dict(count=len(reverse),all_low_high_summary_medium_to_high=reverse_condition,
                       task_counts=dict(__import__('collections').Counter(r['access_task_type'] for r in reverse))))
            write_csv(out/'reverse_scope_upgrades.csv',reverse,list(rows[0]))
            write_csv(out/'policy_distribution_and_changes.csv',summaries,list(summaries[0]))
            write_csv(out/'base_to_full_transition.csv',matrix,list(matrix[0]))
        for name,reason in [
            ('weighted_constraint_reduction','Excluded from this decision-policy update; not independently validated here.'),
            ('weighted_proof_cost_reduction','Excluded from this decision-policy update; not independently validated here.'),
            ('weighted_bundle_size_reduction','Excluded from this decision-policy update; not independently validated here.'),
            ('predicate_floor_coverage','Excluded from this decision-policy update; no per-request L_req is assigned.')]:
            checks.append(dict(check=name,status='NOT_VERIFIABLE',acceptance_scope='excluded',details=reason))
        for name,reason in [
            ('citation_author_confirmation','PUBLICATION_BLOCKER: the existing CITATION.cff is preserved; author and release metadata require manual confirmation.'),
            ('license_and_source_rights_confirmation','PUBLICATION_BLOCKER: the existing LICENSE is preserved; derived-data/code/source-excerpt redistribution rights require manual confirmation.')]:
            checks.append(dict(check=name,status='NOT_VERIFIABLE',acceptance_scope='manual_publication_review',details=reason))
    except (ValueError,KeyError,OSError,IndexError) as exc:
        checks.append(dict(check='execution_or_input_gate',status='FAIL',details=str(exc)))
    failures=[r for r in checks if r['status']=='FAIL']
    unknown=[r for r in checks if r['status']=='NOT_VERIFIABLE']
    result=dict(status='FAIL' if failures else 'PASS',
        release_status='NOT_READY_FOR_PUBLICATION' if failures else 'NEEDS_AUTHOR_REVIEW',
        scope='Frozen offline historical decision-policy reproduction only.',
        complete_paper_evidence='OUTSIDE_THIS_UPDATE_SCOPE',
        offline_decision_acceptance='FAIL' if failures else 'PASS',
        counts={status:sum(r['status']==status for r in checks) for status in ['PASS','FAIL','NOT_VERIFIABLE']},checks=checks)
    write_json(out/'verification_summary.json',result)
    lines=['# Verification summary','', 'Release status: '+result['release_status'],
           '',result['scope'],'','Complete paper evidence: '+result['complete_paper_evidence'],'',
           '| Check | Status | Details |','|---|---|---|']
    for item in checks:
        detail=json.dumps(item['details'],ensure_ascii=False) if isinstance(item['details'],(dict,list)) else str(item['details'])
        lines.append('| '+item['check']+' | '+item['status']+' | '+detail.replace('|',' / ')+' |')
    with (out/'verification_summary.md').open('x',encoding='utf-8') as stream:
        stream.write('\n'.join(lines)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 1 if failures else 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir')
    args=parser.parse_args()
    raise SystemExit(run(args.output_dir))
