# Frozen policy rule provenance

The public policy is version after_07d-frozen-public-1. It uses original `scripts/08_apply_refined_best_params.py` functions at lines 68-271 and 280-629 for numeric components, exact high floor and claim-factor activation; the score application is at 831-848. Base parameters come from `outputs/refined_best_params.json:3-9`.

Final PTFa uses `outputs/ptfa_standalone_v2_best_params.json:3-10`, not the earlier PTFa block in refined_best_params. Original `08b_apply_ptfa_v2_final_params.py:290-311` computes the weighted clipped score and final levels. Its conditional aggregator is at 217-263 and proof mapping at 266-272.

All component fields, numeric tokens, exact high-floor conditions, keyword lists and if/elif order are public in policy_config.json. Original function excerpts are provided for review without executing the original project. In particular, an unknown content token maps to zero in the historical numeric map; diagnostic aliases are not silently added. Runtime mode selection is not proof generation or proof verification.

The complete 27-combination domain keeps the base lower bound but has one Base monotonicity counterexample: Low/High/masked -> High; Medium/High/masked -> Medium. Agg does not generally dominate PTFa. The package checks and discloses these properties instead of asserting global monotonicity.
