from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class ProfileKey:
    family: str
    name: str
    version: int


class CompiledProfileCache:
    """Process-local hot cache for immutable, DB-authored profiles.

    PostgreSQL is the source of truth. Rendering never queries the database.
    A profile is loaded/validated/compiled once, then reused by key.
    """

    def __init__(self) -> None:
        self._values: dict[ProfileKey, Any] = {}
        self._lock = RLock()

    def get_or_compile(self, key: ProfileKey, loader: Callable[[], Any]) -> Any:
        value = self._values.get(key)
        if value is not None:
            return value
        with self._lock:
            value = self._values.get(key)
            if value is None:
                value = loader()
                self._values[key] = value
            return value

    def invalidate(self, *, family: str | None = None, name: str | None = None) -> int:
        with self._lock:
            keys = [k for k in self._values if
                    (family is None or k.family == family) and
                    (name is None or k.name == name)]
            for key in keys:
                del self._values[key]
            return len(keys)

    def clear(self) -> None:
        with self._lock:
            self._values.clear()
