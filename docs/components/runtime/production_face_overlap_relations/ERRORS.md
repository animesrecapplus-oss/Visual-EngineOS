# Errors

`ERR-FPOR-001`: first hostile test supplied an invalid owner geometry object. The canonical visibility
leaf attempted region access before validating its injected contract and raised `AttributeError`.
The new adapter was corrected to validate `GeometryContract` and finite numeric depth at its own boundary.

`ERR-FPOR-002`: no production behavior discrepancy remained after correction; the focused suite was rerun
and passed 9/9.

No error was converted into PASS without rerunning the affected tests.
