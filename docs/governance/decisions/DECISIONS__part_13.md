# Decision register — V1.77

`D-175` — Select `CMP-RUNTIME-PLACEMENT-CONTRACT` because immutable placement vocabulary/intent/result contracts are independently bounded and consumed by multiple real runtime paths.

`D-176` — Make `runtime/placement_contract.py` the sole runtime owner of extracted placement value types while preserving `runtime.placement` compatibility identities.

`D-177` — Keep placement solving and geometry materialization in `runtime/placement.py`.

`D-178` — Keep `CoverageIntent` as an explicit dependency because it is an existing field of `PlacementIntent`; do not duplicate that contract.

`D-179` — Repoint `placement_constraints_contract` TYPE_CHECKING to the canonical placement contract owner to preserve dependency direction.

`D-180` — Require behavior identity and production visual identity evidence before certification.
