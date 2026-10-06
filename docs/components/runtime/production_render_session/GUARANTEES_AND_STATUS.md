# Guarantees and status

Guarantees:
- one canonical session owner;
- compatibility/public identity preserved;
- session-owned caches clear on close while injected caches survive;
- stale graph fails closed and refresh remains explicit;
- production request delegation remains unchanged;
- no COLOR/database/persistence/fingerprint/renderer semantics changed.

Status: `CERTIFIED` only after all applicable V1.71 gates and ZIP integrity checks pass.
