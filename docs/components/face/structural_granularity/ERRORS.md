# Errors — CMP-FACE-STRUCTURAL-GRANULARITY-AUDIT

`ERR-FSG-001`: V1.78 treated silhouette/detail paths as a visual hair improvement without first establishing Hair's missing sub-granularities. V1.79 records this as a boundary error, not as proof of full Hair anatomy.
`ERR-FSG-002`: Nose is a real production micro-component but had no dedicated face/nose truth dossier at V1.78. V1.79 closes the documentation gap only; source ownership remains unchanged.
`ERR-FSG-003`: Head is represented by an embedded `HEAD` surface rather than a standalone component. It is therefore not promoted to a fake child component.
`ERR-FSG-004`: one monolithic V1.79 `pytest -q` invocation exceeded the execution window after approximately 74% progress. The complete 150-file suite was then executed in deterministic batches; all 1164 collected tests were completed with 1163 PASS, 1 expected PostgreSQL skip and 0 failures.
