import pytest
from visual_engine.model import Component, Relation
from visual_engine.runtime import RuntimeGraph

def test_relation_requires_existing_nodes():
    root=Component("r","Root"); root.relations.append(Relation("r","TEST","missing"))
    with pytest.raises(ValueError): RuntimeGraph.from_component(root)

def test_descendants():
    r=Component("r","Root"); a=Component("a","A"); b=Component("b","B"); r.add_child(a); a.add_child(b)
    g=RuntimeGraph.from_component(r)
    assert {n.id for n in g.descendants_of("r")} == {"a","b"}


def test_nested_duplicate_ids_are_rejected_by_runtime_graph():
    from visual_engine.model import Component
    import pytest
    from visual_engine.runtime import RuntimeGraph
    root = Component("root", "root")
    a = Component("a", "branch")
    b = Component("b", "branch")
    a.add_child(Component("dup", "leaf"))
    b.add_child(Component("dup", "leaf"))
    root.add_child(a); root.add_child(b)
    with pytest.raises(ValueError, match="Duplicate component id"):
        RuntimeGraph.from_component(root)



def test_runtime_graph_detects_topology_mutation_and_requires_rebuild():
    root = Component("root", "Root")
    child = Component("child", "Child")
    root.add_child(child)
    graph = RuntimeGraph.from_component(root)
    root.add_child(Component("new", "New"))

    assert not graph.is_current()
    with pytest.raises(RuntimeError, match="RuntimeGraph is stale"):
        graph.children_of("root")

    rebuilt = graph.rebuild()
    assert rebuilt.is_current()
    assert {node.id for node in rebuilt.children_of("root")} == {"child", "new"}


def test_runtime_graph_indexes_are_read_only():
    root = Component("root", "Root")
    graph = RuntimeGraph.from_component(root)
    with pytest.raises(TypeError):
        graph.nodes["x"] = graph.nodes["root"]


def test_runtime_graph_rejects_repeated_component_object_without_recursing():
    root = Component("root", "Root")
    child = Component("child", "Child")
    root.add_child(child)
    # A malformed authoring tree can contain the same object twice if callers mutate
    # the public children list directly. Compilation must fail closed.
    root.children.append(child)
    with pytest.raises(ValueError, match="appears more than once"):
        RuntimeGraph.from_component(root)


def test_runtime_graph_rejects_manual_hierarchy_cycle_without_recursing():
    root = Component("root", "Root")
    child = Component("child", "Child")
    root.add_child(child)
    # Construct the malformed cycle directly to test the runtime boundary rather than
    # relying on Component.add_child(), which correctly rejects only self-parenting.
    child.children.append(root)
    with pytest.raises(ValueError, match="Cycle in component hierarchy"):
        RuntimeGraph.from_component(root)


def test_runtime_graph_rejects_parent_pointer_mismatch():
    root = Component("root", "Root")
    child = Component("child", "Child")
    root.children.append(child)  # bypass add_child deliberately
    with pytest.raises(ValueError, match="Parent link mismatch"):
        RuntimeGraph.from_component(root)
