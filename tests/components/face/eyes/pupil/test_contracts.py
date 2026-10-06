import pytest  # TST-PUPIL-001: pytest supplies deterministic failure assertions.
from visual_engine.components.face.eyes.pupil.effects import PupilGlowSpec, PupilSmokeSpec  # TST-PUPIL-003: effect contracts are under test.
from visual_engine.components.face.eyes.pupil.spec import PupilSpec  # TST-PUPIL-001: pupil value contract is under test.


def test_pupil_spec_accepts_nominal_values():  # TST-PUPIL-001: nominal construction remains valid.
    value = PupilSpec(x=0.1, y=-0.2, scale=0.8, scale_x=1.2, scale_y=0.9, opacity=0.7)  # TST-PUPIL-001: exercise representative finite state.
    assert value.opacity == 0.7  # TST-PUPIL-001: preserve the authored value.


def test_pupil_effect_specs_accept_nominal_values():  # TST-PUPIL-003: effect bounds accept valid inputs.
    glow = PupilGlowSpec(enabled=True, intensity=1.0, core_intensity=0.5)  # TST-PUPIL-003: exercise upper valid intensity.
    smoke = PupilSmokeSpec(enabled=True, opacity=0.5, wisps=2)  # TST-PUPIL-003: exercise valid smoke state.
    assert glow.intensity == 1.0 and smoke.wisps == 2  # TST-PUPIL-003: verify authored values survive construction.


def test_pupil_spec_is_immutable():  # TST-PUPIL-005: frozen dataclass is part of the contract.
    value = PupilSpec()  # TST-PUPIL-005: construct a valid immutable value.
    with pytest.raises((AttributeError, TypeError)):  # TST-PUPIL-005: mutation must be rejected.
        value.scale = 2.0  # TST-PUPIL-005: attempt forbidden mutation.
