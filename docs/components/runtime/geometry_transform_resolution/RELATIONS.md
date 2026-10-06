# Relations

`REL-GTR-001`: `geometry_transform → geometry_transform_resolution` — compatibility/adapter dependency.
`REL-GTR-002`: `eyes.reference.transform → geometry_transform_resolution` — real eye transform consumer.
`REL-GTR-003`: `runtime.__init__ → geometry_transform` — preserved public API route.
`REL-GTR-004`: `geometry_transform_resolution → RuntimeGraph` — parent-chain input.
`REL-GTR-005`: `geometry_transform_resolution → geometry_contract_transform.Matrix3` — shared matrix type only.
`REL-GTR-006`: `geometry_transform → geometry_contract_transform` — geometry-contract transformation remains separate.
