# Component truth

`CMP-RUNTIME-STATE-POLICY-CONTRACT`.

## Identity

`FILE-SPC-001`: `src/visual_engine/runtime/state_policy_contract.py:1-37`.
`TST-SPC-001`: `tests/components/runtime/state_policy_contract/test_v172_state_policy_contract_truth.py:1-40`.

## Responsibility

Own the immutable `StateActivation` and `StateDecision` value contracts used by state-policy resolution; the historical `state_policy` module remains their compatibility facade and resolver owner.

## Non-responsibility

State collection, precedence resolution, conflict/group handling, requirement resolution, appearance, COLOR,
cache, fingerprints, persistence/database, geometry, visibility, occlusion and rendering.
