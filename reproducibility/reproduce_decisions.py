"""Recompute frozen after_07d decisions; compare every row before reporting success."""
import argparse
import sys
sys.dont_write_bytecode = True
from policy_engine import (load_bundle, output_directory, decisions, write_csv, write_json,
                           mode_counts, base_transition, change_summary)


def run(output=None):
    config, inputs, _ = load_bundle()
    out = output_directory(output, 'decisions')
    calculated, comparison, differences = decisions(config, inputs)
    write_csv(out/'field_comparison.csv',comparison,list(comparison[0]))
    write_csv(out/'row_differences.csv',differences,
              ['row_number','collision_index','target','field','actual','reference','absolute_error'])
    write_csv(out/'replayed_test_final.csv',calculated,list(calculated[0]))
    matrix = base_transition(calculated)
    write_csv(out/'base_to_full_transition.csv',matrix,list(matrix[0]))
    base=[r['base_data_level_pred_refined'] for r in calculated]
    full=[r['required_auth_level_final'] for r in calculated]
    result=dict(status='FAIL' if differences else 'PASS',rows=len(calculated),difference_cells=len(differences),
                Full=mode_counts(full,config),Base_only=mode_counts(base,config),
                Full_relative_to_Base_only=change_summary(base,full))
    write_json(out/'decision_summary.json',result)
    print(result)
    return 1 if differences else 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir')
    args=parser.parse_args()
    try:
        raise SystemExit(run(args.output_dir))
    except (ValueError,KeyError,OSError) as exc:
        print('FAIL: '+str(exc),file=sys.stderr)
        raise SystemExit(1)
