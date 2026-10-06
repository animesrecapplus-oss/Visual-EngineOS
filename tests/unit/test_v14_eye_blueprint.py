from __future__ import annotations

import json
from tools.eye_blueprint_loader import load_blueprint
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_v14_blueprint_has_unique_atomic_ids_and_full_lifecycle():
    data = load_blueprint()
    tasks = data["tasks"]
    assert len(tasks) == len({t["id"] for t in tasks})
    assert data["lifecycle"] == ["DEVELOP", "TEST", "ARTIFACT", "VISUALIZE", "CORRECT", "VALIDATE", "ACCEPT"]
    assert len(tasks) >= 100
    for task in tasks:
        assert all(task[k].strip() for k in ("develop", "test", "artifact", "visual", "validation", "correction", "acceptance"))

def test_v14_blueprint_covers_requested_eye_axes():
    data = load_blueprint()
    ids = {t["id"] for t in data["tasks"]}
    required = {
        "PUP.shape", "PUP.size", "PUP.orientation", "PUP.deformation", "PUP.position", "PUP.exposure_limit",
        "PUP.iris_relation", "PUP.lid_relation", "PUP.occlusion", "PUP.reflection_space", "PUP.style", "PUP.expression", "PUP.light",
        "IRI.base", "IRI.shape", "IRI.limbal_ring", "IRI.crypts", "IRI.fibres", "IRI.radial_structure", "IRI.pigmentation",
        "IRI.rings", "IRI.microstructure", "IRI.variation", "IRI.asymmetry", "IRI.transmission", "IRI.style",
        "LAS.implantation", "LAS.density", "LAS.groups", "LAS.length", "LAS.curvature", "LAS.direction", "LAS.root", "LAS.taper",
        "LAS.clusters", "LAS.asymmetry", "LAS.lid_follow", "LAS.occlusion", "LAS.shadow", "LAS.anime", "LAS.realistic",
        "BRW.morphology", "BRW.implantation", "BRW.individual_hairs", "BRW.density", "BRW.global_shape", "BRW.thickness",
        "BRW.ends", "BRW.asymmetry", "BRW.deformation", "BRW.expression", "BRW.forehead_relation", "BRW.skin_relation",
        "HIL.pupil_art", "COL.lighting_response", "COL.material_response", "EXP.vocabulary", "EXP.intensity", "CAM.lod",
        "PRM.parameter_mapping", "PRM.provenance", "VAR.default_contract", "VAR.uniqueness", "RND.visual_regression",
    }
    assert required <= ids
