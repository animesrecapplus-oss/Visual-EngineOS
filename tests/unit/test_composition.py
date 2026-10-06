from visual_engine.scene import CompositionPolicy, Frame, LayoutStrategy, compose

def test_single_entity_is_centered():
    p=compose(["e1"], Frame(1000,1000), CompositionPolicy())
    assert p[0].position.x == 500 and p[0].position.y == 500

def test_many_entities_have_deterministic_grid():
    policy=CompositionPolicy(strategy=LayoutStrategy.GRID)
    a=compose([f"e{i}" for i in range(30)], Frame(1920,1080), policy)
    b=compose([f"e{i}" for i in range(30)], Frame(1920,1080), policy)
    assert a == b
    assert len(a)==30


def test_multiple_eye_placement_covers_frame_without_duplicates():
    from visual_engine.scene import EyePlacementRequest, solve_eye_positions
    pts = solve_eye_positions(Frame(800, 500), EyePlacementRequest(count=4, eye_width=80, eye_height=50))
    assert len({(p.x, p.y) for p in pts}) == 4
    assert all(0 <= p.x <= 800 and 0 <= p.y <= 500 for p in pts)


def test_eye_placement_respects_forbidden_region():
    from visual_engine.scene import EyePlacementRequest, RectRegion, solve_eye_positions
    forbidden = (RectRegion(350, 200, 100, 100),)
    pts = solve_eye_positions(Frame(800, 500), EyePlacementRequest(count=3, eye_width=70, eye_height=45), forbidden=forbidden)
    assert all(not forbidden[0].contains(p, margin=35) for p in pts)
