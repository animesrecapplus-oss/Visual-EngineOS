# Current status — V1.72

## V1.72 — State policy value-contract extraction

Fresh V1.71 audit kept `resolve_component_contract` rejected after the compatibility-cycle proof. The selected micro-component is `CMP-RUNTIME-STATE-POLICY-CONTRACT`: immutable `StateActivation` and `StateDecision` value contracts inside `runtime.state_policy`.

Canonical owner: `src/visual_engine/runtime/state_policy_contract.py:1-37`.
Compatibility/resolver facade: `src/visual_engine/runtime/state_policy.py:1-142`.

The resolver algorithms remain in `state_policy`; existing public and production imports remain identity-compatible. No direct consumer was invented: the canonical contract is reached through the real `state_policy` facade used by the existing runtime consumers.

Production five-case SVG/camera/visibility identity versus V1.71: PASS. Visual QA: PASS and manually inspected.

Benchmark is measurement only; no optimization claim. No COLOR, database, persistence, cache-policy, fingerprint or renderer semantic change.

Status: `V1.72 / STATE POLICY VALUE-CONTRACT EXTRACTION / BEHAVIOR IDENTITY PASS / CERTIFIED`.
