"""Reproduce historical policy-relative ablations after an exact Full recheck."""
import argparse
import sys
sys.dont_write_bytecode = True
from policy_engine import load_bundle, output_directory, decisions, ablations, write_csv, write_json


def run(output=None):
    config,inputs,_=load_bundle()
    out=output_directory(output,'ablations')
    calculated,comparison,differences=decisions(config,inputs)
    write_csv(out/'full_recheck.csv',comparison,list(comparison[0]))
    write_csv(out/'row_differences.csv',differences,
              ['row_number','collision_index','target','field','actual','reference','absolute_error'])
    if differences:
        write_json(out/'ablation_summary.json',dict(status='FAIL',reason='Full differs; ablations not evaluated'))
        return 1
    summaries,rows,matrices,reverse=ablations(calculated,inputs['test'],config)
    for filename,data in [('policy_distribution_and_changes.csv',summaries),('all_policy_decisions.csv',rows),
                          ('transition_matrices.csv',matrices),('reverse_scope_upgrades.csv',reverse)]:
        write_csv(out/filename,data,list(data[0]))
    changed=[r for r in rows if r['direction']!='unchanged']
    write_csv(out/'changed_cases.csv',changed,list(rows[0]))
    result=dict(status='PASS',policies=summaries,reverse_scope_upgrades=len(reverse),
                interpretation='Policy-relative changes under fixed rules, not independent ground-truth errors.')
    write_json(out/'ablation_summary.json',result)
    print(result)
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir')
    args=parser.parse_args()
    try:
        raise SystemExit(run(args.output_dir))
    except (ValueError,KeyError,OSError) as exc:
        print('FAIL: '+str(exc),file=sys.stderr)
        raise SystemExit(1)
