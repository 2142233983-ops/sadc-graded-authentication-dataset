# Historical ablations

Source: `scripts/22_socc_phase2_policy_ablation.py`, policy_full:171-182, policy_without_ptfa:185-193, policy_without_output_scope:196-205, calls:538-539. Base-only mapping is `scripts/26_socc_phase2_base_only_control.py:26,369-373`; Fixed Strong is defined at 233-249.

Full is the conditional aggregation in policy_config.json. Base-only maps the base level after the original high floor. No-PTFa uses base and scope only. No-scope uses max(base,PTFa) with no scope argument; neither ablation recomputes task factors with changed requirements. Fixed Strong selects High authentication for each request.

The frozen experiment has 67 no-scope weakenings (Low/Low/masked: Medium->Low) and 22 strengthenings (Low/High/summary: Medium->High). These are outputs of a different scope-free fallback, not deletion of a monotone max input. They are not evidence of requested/final scope substitution or upstream predicate gating.

Any future predicate safety floor must be checked independently for Full and every claimed-safe variant. A nonbinding floor for Full does not guarantee unchanged ablation counts. This release reproduces the historical variant definitions and assigns no unknown safety floor.
