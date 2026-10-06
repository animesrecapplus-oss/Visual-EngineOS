# Errors — CMP-FACE-HAIR

`ERR-FH-001`: early V1.57 design required explicit finite checks; corrected before certification.

`ERR-FH-002`: historical tests initially depended on the old default generator; compatibility calls were made explicit.

`ERR-FH-003`: V1.58 first Hair/Ear adapter saw no semantic occlusion because Hair and Ear were coplanar. Corrected by the dedicated Hair depth micro-component.

`ERR-FH-004`: path-only Hair geometry was initially passed to the primitive-only visibility kernel. Corrected by using the established semantic-region boundary.

No unresolved Hair-specific error is promoted to PASS.
