# Errors

`ERR-HEO2-001`: first implementation labelled a coplanar relation `FRONT` because the generic visibility kernel hard-coded the region result depth.
Resolution: generic visibility now preserves the nearest actual depth relation at `visibility.py:254-259`.
`ERR-HEO2-002`: first benchmark version computed unnecessary attribution and showed a large measured cost.
Resolution: Head/Ear uses `include_attribution=False`; no attribution consumer was found.
