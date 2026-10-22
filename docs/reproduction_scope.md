# Scope of this incremental reproduction update

This update covers frozen content-sensitivity grading, PTFa scoring, historical adaptive-authentication decisions and policy-relative ablations. It reuses the existing 5,500 requests and fixed 3,850/1,650 split. It adds no system-performance or predicate-coverage claim.

Figure-7 weighted costs, mandatory-predicate resolution, L_req(Q_t), Circom/Groth16 execution, TEE, blockchain, Gas and end-to-end measurements are outside this update's acceptance scope. The verifier records those unexecuted checks as NOT_VERIFIABLE with acceptance_scope=excluded. They are not required offline-policy failures and must not be described as independently validated.

The root LICENSE and CITATION.cff are preserved exactly from the recorded remote commit. Their provisional rights statement and author placeholders require manual confirmation, including permission to distribute the new code and static source excerpts. No DOI, publication date, volume, issue or pages have been invented.

Run the documented commands from the repository root. Input data are read only from processed_data/, never copied again under reproducibility/data/. The input manifest uses repository-relative paths and SHA-256 checks. New run outputs belong under reproducibility/reports/; nonempty targets are rejected.

Counts describe rule-reference agreement or policy-relative decision changes, not independent human-label generalization or externally validated security errors. Existing system functionality is not negated by the deliberately limited scope of this dataset update.
