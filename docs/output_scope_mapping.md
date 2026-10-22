# Output scope compatibility

Original frozen CSVs and 08b use aggregate, masked_record and raw_evidence. Original script 22 explicitly maps aggregate->summary_view, masked_record->masked_record, and raw_evidence->raw_record at lines 30-36; it accepts current names as aliases too.

This is the evidence for the adapter. Its behavior is tested over all 27 combinations against the historical-token reference mapping. The raw 08b function is not assumed to understand current names without adaptation. Invalid scope names are rejected by this public implementation, outside the declared valid domain, rather than accepted through the old default branch.

The original code has one output_scope column and no distinct requested/final-scope resolver. Output categories condition authentication decisions; physical masking and actual output projection are outside this release. In particular raw_record is not an unconditional numeric High lower bound: Low base plus Low/Medium PTFa can select Medium.
