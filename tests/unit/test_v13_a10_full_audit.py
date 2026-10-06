"""Independent V1.3 A10 structural-audit checks.

These tests intentionally inspect architecture boundaries rather than exercising a
single feature. They are designed to catch regressions where an older verifier can
still pass while the repository quietly develops duplicate ownership or drift.
"""

from __future__ import annotations

import ast
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "visual_engine"


def _module_name(path: Path) -> str:
    rel = path.relative_to(ROOT / "src").with_suffix("")
    parts = rel.parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _internal_top_level_edges() -> dict[str, set[str]]:
    """Build only top-level import edges; local compatibility imports are intentional seams."""
    modules = {_module_name(p) for p in SRC.rglob("*.py")}
    edges = {m: set() for m in modules}
    for path in SRC.rglob("*.py"):
        module = _module_name(path)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module]
            for target in names:
                if not target.startswith("visual_engine"):
                    continue
                candidate = target
                while candidate not in modules and "." in candidate:
                    candidate = candidate.rsplit(".", 1)[0]
                if candidate in modules:
                    edges[module].add(candidate)
    return edges


def test_top_level_runtime_import_graph_is_acyclic() -> None:
    edges = _internal_top_level_edges()
    state: dict[str, int] = {}

    def visit(node: str, stack: tuple[str, ...]) -> None:
        state[node] = 1
        for target in edges[node]:
            if state.get(target) == 1:
                cycle = " -> ".join((*stack, target))
                raise AssertionError(f"top-level import cycle: {cycle}")
            if state.get(target, 0) == 0:
                visit(target, (*stack, target))
        state[node] = 2

    for module in edges:
        if state.get(module, 0) == 0:
            visit(module, (module,))


def test_internal_source_uses_canonical_component_ownership() -> None:
    """The model package remains a compatibility facade, never an internal owner."""
    offenders: list[str] = []
    for path in SRC.rglob("*.py"):
        if "/model/" in path.as_posix():
            continue
        text = path.read_text(encoding="utf-8")
        if "visual_engine.model" in text:
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"internal source imports compatibility model facade: {offenders}"


def test_model_modules_are_compatibility_facades() -> None:
    for name in ("meta.py", "geometry_contract.py", "visual_contract.py"):
        path = SRC / ".." / "visual_engine" / "model" / name
        text = path.resolve().read_text(encoding="utf-8").strip().splitlines()
        assert len(text) <= 2, f"legacy model facade unexpectedly owns implementation: {name}"
        assert "components.common" in "\n".join(text)


def test_version_policy_has_one_executable_source_of_truth() -> None:
    policy = (SRC / "runtime" / "version_policy.py").read_text(encoding="utf-8")
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    engine = re.search(r'ENGINE_VERSION\s*=\s*"([^"]+)"', policy)
    package = re.search(r'^version\s*=\s*"([^"]+)"', project, re.MULTILINE)
    assert engine and package
    assert engine.group(1) == package.group(1)


def test_migration_ledger_is_contiguous_and_unique() -> None:
    migration_dir = ROOT / "db" / "migrations"
    ids = []
    for path in migration_dir.glob("*.sql"):
        match = re.match(r"(\d{3})_", path.name)
        assert match, f"migration has no ordered numeric prefix: {path.name}"
        ids.append(int(match.group(1)))
    ids = sorted(ids)
    assert ids == sorted(set(ids))
    assert ids == list(range(1, len(ids) + 1))
