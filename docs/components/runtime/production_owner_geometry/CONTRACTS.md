# Contracts

`CON-POG-001`: input geometry is a `GeometryContract`; `owner_id` is a non-empty string.
`CON-POG-002`: at least one surface must identify `source_component_id == owner_id`.
`CON-POG-003`: all selected surfaces must expose one common integer `depth_layer` value.
`CON-POG-004`: selected surface `path_index` values must reference existing source paths and are rebased to a local deterministic index.
`CON-POG-005`: primitives are selected by `component_id`; no primitive/path is synthesized.
`CON-POG-006`: returned geometry is renderer-neutral and no input geometry is mutated.
`CON-POG-007`: the extraction preserves the pre-V1.62 production selection/rebasing semantics exactly.
