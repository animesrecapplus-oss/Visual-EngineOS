from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _run_a8(out: Path) -> dict:
    env = os.environ.copy()
    env["A8_E2E_OUT"] = str(out)
    env["PYTHONPATH"] = str(Path(__file__).parents[2] / "src")
    result = subprocess.run(
        [sys.executable, "tools/verify_a8_e2e.py"],
        cwd=Path(__file__).parents[2],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    import json
    return json.loads(result.stdout)


def test_a8_e2e_runs_twice_deterministically(tmp_path):
    first = _run_a8(tmp_path / "one")
    second = _run_a8(tmp_path / "two")
    assert first["status"] == second["status"] == "PASS"
    assert first["generated_geometry_hash"] == second["generated_geometry_hash"]
    assert first["generated_cache_identity"] == second["generated_cache_identity"]
    assert first["resolution_fingerprint"] == second["resolution_fingerprint"]
    assert first["base_resolution_digest"] == second["base_resolution_digest"]
    assert first["camera_geometry_hash"] == second["camera_geometry_hash"]
    assert first["svg_sha256"] == second["svg_sha256"]
    assert first["serialized_sha256"] == second["serialized_sha256"]


def test_a8_evidence_is_well_formed_and_clean(tmp_path):
    _run_a8(tmp_path / "run")
    files = sorted((tmp_path / "run").iterdir())
    assert [p.name for p in files] == [
        "REPORT.json", "a8_face_camera.svg", "a8_serialized_components.json"
    ]
    svg = (tmp_path / "run" / "a8_face_camera.svg").read_text(encoding="utf-8")
    assert svg.startswith("<svg ")
    assert "NaN" not in svg and "Infinity" not in svg


def test_a8_source_declares_stale_graph_and_fail_closed_renderer_guards():
    source = (Path(__file__).parents[2] / "tools" / "verify_a8_e2e.py").read_text(encoding="utf-8")
    assert "shutil.rmtree(OUT)" in source
    assert "assert not graph.is_current()" in source
    assert "A8 evidence renderer does not silently approximate geometry masks" in source
    assert "A8 evidence renderer does not support primitive" in source
    assert "UNVERIFIED" in source
