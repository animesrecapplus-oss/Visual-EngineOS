from visual_engine.entities import build_human_face
from visual_engine.persistence import canonical_entity_record
from visual_engine.runtime import RuntimeGraph
from visual_engine.scene import CompositionPolicy, Frame, compose

def test_v03_vertical_slice():
    face=build_human_face("person_0001_face")
    graph=RuntimeGraph.from_component(face)
    placements=compose(["person_0001"], Frame(512,512), CompositionPolicy())
    record=canonical_entity_record("person_0001", "Human", 1234)
    assert len(graph.nodes) >= 20
    assert placements[0].position.x == 256
    assert record["seed"] == 1234
