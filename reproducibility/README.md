# Reproducing authentication decisions and ablations

This directory adds reproducibility to the existing SADC semi-synthetic STATS19 dataset repository. All commands below run from the **repository root** with Python 3.10+ and the standard library only. No installation, external repository, original local project, internal audit folder, TEE, blockchain or proof generation is required.

```sh
python -B reproducibility/reproduce_decisions.py
python -B reproducibility/reproduce_ablations.py
python -B reproducibility/verify_results.py
```

Default outputs are reproducibility/reports/decisions, /ablations and /verification. If one already exists and is nonempty, select a fresh directory:

```sh
python -B reproducibility/verify_results.py --output-dir reproducibility/reports/my_verification
```

No input or existing result is overwritten. An input hash mismatch, missing field, changed row order or row-level result mismatch is a FAIL. Missing or intentionally excluded evidence is NOT_VERIFIABLE, never PASS. A nonzero exit code signals an executed failure. Publication readiness separately remains NEEDS_AUTHOR_REVIEW while the preserved citation/license placeholders need confirmation.

## Inputs reused without duplicates

The existing processed_data/accident_capsule_dataset_full.csv (5,500), accident_capsule_tune.csv (3,850), accident_capsule_test.csv (1,650) and accident_capsule_classified_test_final.csv (1,650) are reused in place and hash-checked. The only additional data CSV is processed_data/accident_capsule_classified_test_refined.csv, copied byte-for-byte from the frozen intermediate.

All sensitivity components and five PTFa claim factors are recomputed from the test's content/access fields. Refined factors and final output fields are comparison references only, not calculation inputs. Full/tune are inspected to verify the immutable split; no tuning or dataset generation occurs. See input_manifest.json for all input hashes and parameters/ for the original two parameter JSONs.

## Frozen rules

policy_config.json contains numeric mappings, exact high-floor triggers, the original case-sensitive keyword activations and their if/elif order, conditional aggregation and all controls. Original function/line/hash references and static excerpts are provided in provenance/.

- Sensitivity: 0.225 A + 0.200 Iv + 0.400 Ha + 0.175 Rl_content; score < 0.300 => Low, score >= 0.775 => High, otherwise Medium, then the historical high floor.
- High floor: fatal=1; raw-EDR flag=1; full_trip; EDR raw/raw_edr; raw_video; raw_radar; injury_detail; liability_detail. Historical naming limitations are preserved, not silently repaired.
- PTFa: min(1, 0.15 role + 0.20 relation + 0.20 qualification + 0.35 regulator + 0.35 court); thresholds 0.25 and 0.45 with the same comparisons. Weights are not normalized by their sum.
- Scope aliases explicitly come from original script 22: aggregate -> summary_view, masked_record -> masked_record, raw_evidence -> raw_record. The adapter is checked on every combination; it is not inferred from similar names.
- Full: the ordered conditional rules below, **not** max(Base, PTFa, L_out).

| Base | PTFa | Scope | Auth |
|---|---|---|---|
| High | Any | Any valid scope | High |
| Medium | Any | raw_record | High |
| Medium | Any | summary_view/masked_record | Medium |
| Low | Low | summary_view | Low |
| Low | Low | masked_record/raw_record | Medium |
| Low | Medium | Any valid scope | Medium |
| Low | High | summary_view | Medium |
| Low | High | masked_record/raw_record | High |

Low/Medium/High auth maps to Basic/Medium/Strong proof mode. full_policy_mapping.csv lists all 27 combinations and original source lines. Agg >= Base holds; global Base monotonicity does not: Low/High/masked -> High but Medium/High/masked -> Medium. This known property is disclosed rather than modified.

Base-only maps the base level after the historical high floor directly to proof mode. w/o L_ptfa uses base and scope only: High->High; Medium+raw->High and other Medium->Medium; Low+summary->Low and other Low->Medium. w/o L_out uses max(Base,PTFa) with no scope input. Fixed Strong always selects Strong. No variant computes from manual/reference labels or historical final auth outputs.

## Acceptance references

Expected statistics are stored separately in expected_results.json and never used to compute decisions:

| Result | Expected |
|---|---|
| Full Basic/Medium/Strong | 365/721/564 |
| Base-only Basic/Medium/Strong | 652/548/450 |
| Full vs Base-only upgrades/downgrades | 390/0 |
| Basic->Medium, Basic->Strong, Medium->Strong | 276, 11, 103 |
| w/o L_ptfa weaker/stronger vs Full | 188/0 |
| w/o L_out weaker/stronger vs Full | 67/22 |

Rates divide by all 1,650 requests. The verifier compares 16 final fields and five refined factors (float tolerance 1e-12; categories exact), split contents, source parameters, threshold boundaries, all 27 mappings/aliases and transition counts. The ablation script exports every request ID/row and each policy output.

All 22 no-scope reverse upgrades must independently satisfy Low Base, High PTFa and summary_view, with Full=Medium and no-scope=High. They arise from the historical scope-free max fallback, not a requested/final-scope replacement or an upstream predicate-gating bypass. These are policy-relative changes, not external ground-truth errors.

## Evidence boundary

The root dataset caveats continue to apply: content/access fields are semi-synthetic, example DID/hash values are not real credentials, and rule-reference labels are not independent human annotations. ML baseline scores do not establish independent generalization.

Figure-7 costs and L_req(Q_t) are **outside this update** and are not independently verified. No artificial cost data or per-row predicate floor is generated. The limited classification release does not imply the full SADC prototype lacks coverage checks. The new material does not claim to reproduce every protocol or performance experiment in the paper.

See ../docs/reproduction_scope.md and reports/reference_verification_summary.json for scope and latest isolated acceptance. The root LICENSE and CITATION.cff are preserved pending manual confirmation.
