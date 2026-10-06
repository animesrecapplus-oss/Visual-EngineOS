# Decision register — V1.76

`D-170` — Select `CMP-RUNTIME-PLACEMENT-CONSTRAINT-CONTRACT` because immutable constraint contracts are independently bounded and consumed by relation compilation.

`D-171` — Make `runtime/placement_constraints_contract.py` the canonical owner while preserving historical `runtime.placement_constraints` identities.

`D-172` — Keep geometry validation and constrained placement resolution in `runtime/placement_constraints.py`.

`D-173` — Use TYPE_CHECKING for `PlacementSolution` to keep the contract owner independent of the runtime placement algorithm.

`D-174` — Require final benchmark and production visual identity evidence before certification.
