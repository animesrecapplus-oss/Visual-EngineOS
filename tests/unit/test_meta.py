import pytest
from visual_engine.model import Component, Constraint, ConstraintKind, Parameter

def test_parameter_range_and_finite():
    assert Parameter("x", 0.5, 0, 1).value == 0.5
    with pytest.raises(ValueError): Parameter("x", 2, 0, 1)
    with pytest.raises(ValueError): Parameter("x", float("nan"))

def test_component_walk_find_and_duplicate_guard():
    root=Component("root","Root"); child=Component("child","Child"); root.add_child(child)
    assert [c.id for c in root.walk()] == ["root","child"]
    assert root.find("child") is child
    with pytest.raises(ValueError): root.add_child(Component("child","Other"))

def test_constraint_kinds_are_explicit():
    c=Constraint("ratio", ConstraintKind.AESTHETIC, "a/b≈1.618")
    assert c.kind is ConstraintKind.AESTHETIC
