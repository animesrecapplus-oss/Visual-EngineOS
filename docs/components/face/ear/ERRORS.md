# Errors — CMP-FACE-EAR

- `ERR-FE-001`: first implementation attempted `depth_layer=-1`; existing renderer contract rejected negative depth. Corrected to depth `0` plus explicit ear paint priority.
- `ERR-FE-002`: first test assumed the synthetic surface name `head:head`; actual production ownership is `face:head:head`. Test corrected to the real emitted owner.
- `ERR-FE-003`: during V1.80 editing, an import was temporarily placed before the module docstring; corrected before validation. No shipped tree contained the transient ordering error.
- `ERR-FE-004`: the V1.56 dossier described finite parameter blocking only through the generic `Parameter` constructor. V1.80 closes the malformed-Component bypass explicitly at the leaf generator.
