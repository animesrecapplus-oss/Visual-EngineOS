from __future__ import annotations

import tomllib
from pathlib import Path

from visual_engine import __version__
from visual_engine.persistence.schema import SCHEMA_VERSION, canonical_entity_record
from visual_engine.runtime import ENGINE_VERSION, RESOLUTION_VERSION, SCHEMA_VERSION as RUNTIME_SCHEMA_VERSION, CURRENT_VERSION_POLICY
from visual_engine.runtime.version_policy import (
    CURRENT_VERSION_POLICY,
    ENGINE_VERSION,
    RESOLUTION_VERSION,
    SCHEMA_VERSION as POLICY_SCHEMA_VERSION,
)
from visual_engine.runtime.versioning import VersionStamp

ROOT = Path(__file__).resolve().parents[2]


def test_current_policy_is_the_version_stamp_source_of_truth():
    assert (CURRENT_VERSION_POLICY.engine, CURRENT_VERSION_POLICY.schema, CURRENT_VERSION_POLICY.resolution) == (
        VersionStamp().engine, VersionStamp().schema, VersionStamp().resolution
    )
    assert CURRENT_VERSION_POLICY.engine == ENGINE_VERSION
    assert CURRENT_VERSION_POLICY.schema == SCHEMA_VERSION == POLICY_SCHEMA_VERSION
    assert CURRENT_VERSION_POLICY.resolution == RESOLUTION_VERSION


def test_package_and_pyproject_engine_versions_cannot_drift():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert __version__ == ENGINE_VERSION
    assert project["project"]["version"] == ENGINE_VERSION


def test_entity_record_has_independent_engine_and_schema_versions():
    record = canonical_entity_record("person_0001", "Human", 42)
    assert record["engine_version"] == ENGINE_VERSION
    assert record["schema_version"] == SCHEMA_VERSION
    assert record["engine_version"] != record["schema_version"]


def test_explicit_historical_version_stamp_remains_supported():
    historical = VersionStamp(engine="1.3.0", schema="1", resolution="7")
    assert historical != VersionStamp()
    assert historical.engine == "1.3.0"
    assert historical.schema == "1"
    assert historical.resolution == "7"


def test_runtime_public_exports_match_policy():
    assert ENGINE_VERSION == CURRENT_VERSION_POLICY.engine
    assert RUNTIME_SCHEMA_VERSION == CURRENT_VERSION_POLICY.schema
    assert RESOLUTION_VERSION == CURRENT_VERSION_POLICY.resolution
