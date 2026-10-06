# Errors

`ERR-PHER-001`: first behavior comparison used a four-case sequence different from the certified V1.63 identity sequence and falsely reported cache-stat divergence.
Resolution: rerun both exact V1.63 and V1.64 checkpoints with the same five-case sequence; SVG/result/cache identity then matched.

`ERR-PHER-002`: first full-regression attempt correctly blocked on two certification conditions: superseded `artifacts/current/v1.63/` remained during the run and two governance part files exceeded the 150-line documentation budget after appending V1.64.
Resolution: purge the superseded artifact tree and split V1.64 status/roadmap into bounded part files before rerunning the affected test groups.

No unresolved implementation or certification error remains at the final gate.
