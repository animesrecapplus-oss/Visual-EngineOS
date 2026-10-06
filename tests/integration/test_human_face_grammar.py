from visual_engine.entities import build_human_face
from visual_engine.runtime import RuntimeGraph

def find_kind(component, kind):
    return next(c for c in component.walk() if c.kind == kind)

def test_human_face_grammar_is_recursive_and_indexable():
    face=build_human_face()
    graph=RuntimeGraph.from_component(face)
    eyes=[n for n in graph.nodes.values() if n.kind=="Eye"]
    assert len(eyes)==2
    assert find_kind(graph.get("left_eye").component, "Cornea").kind == "Cornea"
    assert find_kind(graph.get("right_eye").component, "Iris").kind == "Iris"
    assert find_kind(graph.get("left_eye").component, "TearFilm").kind == "TearFilm"
