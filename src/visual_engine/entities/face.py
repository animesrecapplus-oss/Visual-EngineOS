from visual_engine.components.common.meta import AppearanceLayer, Anchor, Component, Constraint, ConstraintKind, Parameter, StateLayer
from visual_engine.components.common.visual_contract import ContourContract, VisualContract, VisualOverrides

def build_human_face(face_id: str = "face") -> Component:
    face = Component(face_id, "HumanFace")
    for name, value, lo, hi in (("width",1.0,0.5,2.0),("height",1.2,0.6,2.4),("symmetry",0.95,0.0,1.0),("skin_tone",0.65,0.0,1.0)):
        face.set_parameter(Parameter(name, value, lo, hi))
    face.add_constraint(Constraint("exactly_two_eyes", ConstraintKind.HARD, "count(children.kind=Eye)==2"))
    face.add_constraint(Constraint("exactly_one_nose", ConstraintKind.HARD, "count(children.kind=Nose)==1"))
    face.add_constraint(Constraint("exactly_one_mouth", ConstraintKind.HARD, "count(children.kind=Mouth)==1"))
    face.add_constraint(Constraint("exactly_one_hair", ConstraintKind.HARD, "count(children.kind=Hair)==1"))
    face.add_constraint(Constraint("eye_symmetry", ConstraintKind.SOFT, "mirror_distance(left_eye,right_eye)<=tolerance", 0.5))
    face.add_constraint(Constraint("golden_ratio_prior", ConstraintKind.AESTHETIC, "height/width≈1.618", 0.1))
    face.add_appearance(AppearanceLayer("skin", {"color_space":"linear-srgb","base_color":[0.65,0.42,0.30,1.0]}))
    # The generic resolver consumes VisualContract; keep this authored presentation
    # explicit instead of making the renderer infer color from legacy appearance layers.
    face.visual = VisualContract(fill_color="#d9a77d", contour=ContourContract(color="#6b4030", width=2.5))
    for state in ("dirt","blood","wetness","damage"): face.add_state(StateLayer(state, enabled=False))
    for side, x in (("left",-0.28),("right",0.28)):
        eye = build_eye(f"{side}_eye", x)
        face.add_child(eye)
    nose = Component("nose", "Nose", anchors={"center": Anchor("center", 0, 0, 0)})
    # The generic resolver already has an explicit field-level inheritance
    # contract. Use it here instead of copying the face skin color into a second
    # authority; the nose therefore follows future face-level visual changes.
    nose.visual_overrides = VisualOverrides()
    nose.set_parameter(Parameter("width", 0.12, 0.04, 0.30))
    nose.set_parameter(Parameter("height", 0.20, 0.10, 0.60))
    face.add_child(nose)
    mouth = Component("mouth", "Mouth", anchors={"center": Anchor("center", 0, 0.32, 0)})
    mouth.visual = VisualContract(fill_color="#5b1f24", contour=ContourContract(color="#3a1418", width=1.5))
    mouth.set_parameter(Parameter("width", 0.28, 0.08, 0.70))
    mouth.set_parameter(Parameter("height", 0.08, 0.02, 0.20))
    mouth.add_constraint(Constraint("positive_size", ConstraintKind.HARD, "width>0 and height>0"))
    face.add_child(mouth)
    for ear_id, x in (("left_ear", -0.54), ("right_ear", 0.54)):
        ear = Component(ear_id, "Ear", anchors={"center": Anchor("center", x, 0.0, 0)})
        ear.visual = VisualContract(fill_color="#d9a77d", contour=ContourContract(color="#6b4030", width=2.0))
        ear.set_parameter(Parameter("width", 0.22, 0.10, 0.50))
        ear.set_parameter(Parameter("height", 0.34, 0.16, 0.70))
        ear.add_constraint(Constraint("positive_size", ConstraintKind.HARD, "width>0 and height>0"))
        face.add_child(ear)
    hair = Component("hair", "Hair", anchors={"center": Anchor("center", 0, -0.38, 0)})
    hair.visual = VisualContract(fill_color="#3b241c", contour=ContourContract(color="#21140f", width=2.0))
    hair.set_parameter(Parameter("width", 1.08, 0.60, 1.50))
    hair.set_parameter(Parameter("height", 0.68, 0.20, 1.20))
    hair.set_parameter(Parameter("hairline_depth", 0.10, 0.04, 0.20))
    hair.set_parameter(Parameter("strand_density", 0.65, 0.0, 1.0))
    hair.add_constraint(Constraint("positive_size", ConstraintKind.HARD, "width>0 and height>0"))
    face.add_child(hair)
    return face

def build_eye(eye_id: str, x: float = 0.0) -> Component:
    eye = Component(eye_id, "Eye", anchors={"center":Anchor("center",x,0,0)})
    for name, value, lo, hi in (("width",0.22,0.05,1.0),("height",0.12,0.03,0.8),("iris_ratio",0.52,0.1,0.9),("pupil_ratio",0.38,0.05,0.8),("opening",1.0,0.0,1.0),("asymmetry",0.0,-1.0,1.0)):
        eye.set_parameter(Parameter(name,value,lo,hi))
    eye.add_constraint(Constraint("positive_size", ConstraintKind.HARD, "width>0 and height>0"))
    eye.add_constraint(Constraint("mandatory_upper_eyelid", ConstraintKind.HARD, "exists(child.kind=UpperEyelid)"))
    eye.add_constraint(Constraint("mandatory_lower_eyelid", ConstraintKind.HARD, "exists(child.kind=LowerEyelid)"))
    eye.add_constraint(Constraint("eyebrow_superior_region", ConstraintKind.HARD, "eyebrow.y < upper_eyelid.top"))
    eye.add_child(Component(f"{eye_id}__eyeball", "Eyeball"))
    for kind, name in (("Sclera","sclera"),("Conjunctiva","conjunctiva"),("Cornea","cornea"),("Iris","iris"),("Pupil","pupil"),("LimbalRing","limbal_ring")):
        child = Component(f"{eye_id}__{name}", kind)
        eye.find(f"{eye_id}__eyeball").add_child(child)  # type: ignore[union-attr]
    for kind, name in (("UpperEyelid","upper_eyelid"),("LowerEyelid","lower_eyelid"),("UpperEyelidFold","upper_eyelid_fold"),("LowerEyelidFold","lower_eyelid_fold"),("InnerCanthus","inner_canthus"),("OuterCanthus","outer_canthus"),("UpperEyelashes","upper_eyelashes"),("LowerEyelashes","lower_eyelashes"),("Eyebrow","eyebrow")):
        eye.add_child(Component(f"{eye_id}__{name}", kind))
    eye.add_child(Component(f"{eye_id}__tear_system", "TearSystem"))
    eye.find(f"{eye_id}__tear_system").add_child(Component(f"{eye_id}__tear_film", "TearFilm"))  # type: ignore[union-attr]
    eye.add_child(Component(f"{eye_id}__eye_socket", "EyeSocket"))
    eye.add_appearance(AppearanceLayer("contour", {"color":"#000000", "width":"component_relative"}))
    eye.add_appearance(AppearanceLayer("sclera", {"base_color":[1.0,1.0,1.0,1]}))
    eye.add_appearance(AppearanceLayer("conjunctiva", {"base_color":[1.0,1.0,1.0,1]}))
    eye.add_appearance(AppearanceLayer("iris", {"base_color":[0.15,0.35,0.55,1],"pattern":"procedural"}))
    eye.add_appearance(AppearanceLayer("corneal_reflection", {"type":"specular","strength":0.35}))
    for state in ("normal","irritated","covered","damaged","closed","wide_open"): eye.add_state(StateLayer(state, enabled=(state=="normal")))
    return eye
