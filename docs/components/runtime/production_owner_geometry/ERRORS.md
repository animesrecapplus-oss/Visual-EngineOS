# Errors

`ERR-POG-001`: initial comparison script attempted to call `ResolutionCacheStats` as a function; corrected to the actual property before evidence was recorded.
`ERR-POG-002`: initial visual QA copy wrote V1.62 evidence under the V1.61 directory; corrected before certification and old V1.61 evidence will be purged from the working tree.
`ERR-POG-003`: no unresolved implementation error remains at certification.

`ERR-POG-004`: full regression artifact-policy test initially failed because V1.61 and V1.62 current directories coexisted. V1.61 was removed as required before rerunning the affected groups.
