import ast
from pathlib import Path

from tools.audit_v154_domain_input_factory import run
from tools.validate_v154_domain_input_factory_truth import validate


def test_v154_component_gate_passes():
    result = validate()
    assert result["ok"], result


def test_v154_owner_is_acyclic_and_unique():
    result = run()
    assert result["selected_new_owner"] == "visual_engine.runtime.domain_input_factory"
    assert not any("domain_input_factory" in member for cycle in result["strongly_connected_cycles"] for member in cycle)
    assert result["exact_duplicate_function_groups"] == []


def test_v154_owner_does_not_import_legacy_facade():
    owner = Path(__file__).resolve().parents[2] / "src/visual_engine/runtime/domain_input_factory.py"
    tree = ast.parse(owner.read_text(encoding="utf-8"))
    assert not any(isinstance(n, ast.ImportFrom) and n.module == "visual_engine.runtime.domain_resolution" for n in ast.walk(tree))
