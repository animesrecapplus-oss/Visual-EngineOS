# Errors

`ERR-PVS-001`: first implementation re-resolved the root inside the new adapter, which would have added a cache hit and changed
observable cache statistics. Corrected by injecting `resolution.visual` from the session.

`ERR-PVS-002`: initial hostile test used the cache statistics object as a callable and referenced a non-existent visual property.
Corrected against the actual `ResolutionCacheStats` property and `ResolvedVisualContract` contract before certification.

No unresolved implementation error remains at the certification gate.
