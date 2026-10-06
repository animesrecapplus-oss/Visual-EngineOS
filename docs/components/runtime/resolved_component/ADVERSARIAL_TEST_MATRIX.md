# Adversarial test matrix

`ADV-RCMP-001`: mutation attempt → frozen dataclass must reject ordinary field mutation.

`ADV-RCMP-002`: undeclared attribute attempt → slot-based result must reject dynamic attributes.

`ADV-RCMP-003`: duplicate construction → equal input values must produce equal immutable value envelopes.

`ADV-RCMP-004`: compatibility identity → facade and public imports must be the exact canonical Python objects.

`ADV-RCMP-005`: legacy facade dependency → owner must not import `runtime.contract`.

`ADV-RCMP-006`: stale cache / wrong fingerprint / NaN / ∞ / occlusion / visibility → these are upstream semantic
concerns and must not be reimplemented by this owner; production and historical hostile suites remain responsible.

`ADV-RCMP-007`: cycle/duplicate → graph and duplicate-function audits must remain clean.
