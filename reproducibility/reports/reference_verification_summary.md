# Verification summary

Release status: NEEDS_AUTHOR_REVIEW

Frozen offline historical decision-policy reproduction only.

Complete paper evidence: OUTSIDE_THIS_UPDATE_SCOPE

| Check | Status | Details |
|---|---|---|
| frozen_hashes_and_configuration | PASS | All input SHA-256/size checks and schema/weight/threshold checks passed. |
| parameter_source_values | PASS | Configuration compared with the unmodified source parameter JSON values recorded independently. |
| original_parameter_json_agreement | PASS | Final PTFa uses V2 values, not the earlier refined PTFa block. |
| complete_27_mapping | PASS | Every enumerated legal type combination is checked against the source-derived reference mapping. |
| scope_alias_equivalence | PASS | Both names tested for every base/PTFa combination; unknown names are rejected. |
| unknown_scope_rejected | PASS | The valid domain is explicit, not the historical unknown-value fallback. |
| base_dominance | PASS | Agg(a,b,c)>=a for all 27 combinations. |
| known_mathematical_properties | PASS | {"observed_violations": {"base": 1, "ptfa": 0, "output_risk": 0}, "note": "Base monotonicity is known to fail; this check preserves that fact rather than claiming monotonicity."} |
| threshold_boundaries | PASS | Strict low comparison and inclusive high comparison. |
| fixed_split | PASS | Full/tune/test identifiers, disjointness, row content and preserved split markers. |
| row_level_decisions_and_claims | PASS | {"rows": 1650, "difference_cells": 0, "tolerance": 1e-12} |
| comparison_detects_reference_error | PASS | An in-memory incorrect reference is detected; no frozen input is changed. |
| proof_mode_distributions | PASS | {"Full": {"basic": 365, "medium": 721, "strong": 564}, "Base_only": {"basic": 652, "medium": 548, "strong": 450}} |
| base_to_full_changes | PASS | {"upgraded": 390, "downgraded": 0, "unchanged": 1260} |
| base_to_full_transition_matrix | PASS | [{"from_level": "low", "to_level": "low", "count": 365}, {"from_level": "low", "to_level": "medium", "count": 276}, {"from_level": "low", "to_level": "high", "count": 11}, {"from_level": "medium", "to_level": "low", "count": 0}, {"from_level": "medium", "to_level": "medium", "count": 445}, {"from_level": "medium", "to_level": "high", "count": 103}, {"from_level": "high", "to_level": "low", "count": 0}, {"from_level": "high", "to_level": "medium", "count": 0}, {"from_level": "high", "to_level": "high", "count": 450}] |
| ablation_w/o L_ptfa | PASS | {"weaker_than_full": 188, "stronger_than_full": 0} |
| ablation_w/o L_out | PASS | {"weaker_than_full": 67, "stronger_than_full": 22} |
| reverse_scope_upgrade_conditions | PASS | {"count": 22, "all_low_high_summary_medium_to_high": true, "task_counts": {"law_enforcement_review": 22}} |
| weighted_constraint_reduction | NOT_VERIFIABLE | Excluded from this decision-policy update; not independently validated here. |
| weighted_proof_cost_reduction | NOT_VERIFIABLE | Excluded from this decision-policy update; not independently validated here. |
| weighted_bundle_size_reduction | NOT_VERIFIABLE | Excluded from this decision-policy update; not independently validated here. |
| predicate_floor_coverage | NOT_VERIFIABLE | Excluded from this decision-policy update; no per-request L_req is assigned. |
| citation_author_confirmation | NOT_VERIFIABLE | PUBLICATION_BLOCKER: the existing CITATION.cff is preserved; author and release metadata require manual confirmation. |
| license_and_source_rights_confirmation | NOT_VERIFIABLE | PUBLICATION_BLOCKER: the existing LICENSE is preserved; derived-data/code/source-excerpt redistribution rights require manual confirmation. |
