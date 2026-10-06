# Errors

`ERR-PAIR-001`: first V1.59 implementation computed full attribution for Head/Ear without a real consumer.
Resolution: `include_attribution=False` for Head/Ear; Hair/Ear remains attribution-complete.

`ERR-PAIR-002`: a V1.58 compatibility hostile test initially received the kind error before the distinct-owner error.
Resolution: same-ID validation restored before kind validation in the Hair/Ear adapter.
