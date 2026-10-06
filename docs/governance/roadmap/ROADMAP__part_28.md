# Roadmap — V1.72 and next frontier

## V1.72 — State policy value-contract extraction

Fresh V1.71 audit re-tested the known `resolve_component_contract` seam and kept it rejected because static compatibility ownership creates a cycle. A separate independent boundary was proven in `runtime.state_policy`: immutable `StateActivation` and `StateDecision` values have a distinct contract responsibility and are consumed through the existing compatibility/public surface.

Canonical owner: `runtime/state_policy_contract.py:1-37`. `state_policy.py` remains the resolver owner and compatibility facade.

Preserved: state collection, precedence/conflict/requirement resolution, public identities, resolution-context behaviour and production render behaviour.

## V1.73 rule

Start from the fresh certified V1.72 checkpoint. Perform another read-only responsibility/consumer/contract/impact audit. Do not assume another state, appearance, resolver, cache, COLOR, persistence or renderer seam without proof.
