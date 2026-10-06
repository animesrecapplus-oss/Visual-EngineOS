from visual_engine.components.face.eyes.appearance.spec import EyeAppearance  # REL-PUPIL-RENDER: aggregate consumer boundary.
from visual_engine.components.face.eyes.pupil.spec import PupilSpec  # REL-PUPIL-RENDER: pupil input boundary.


def test_pupil_enters_eye_appearance_through_declared_spec():  # TST-PUPIL-006: verify the real aggregate consumer.
    pupil = PupilSpec(x=0.12, y=-0.04)  # TST-PUPIL-006: create a validated pupil value.
    appearance = EyeAppearance(pupils=(pupil,))  # TST-PUPIL-006: consume it through the real parent contract.
    assert appearance.pupils[0] is pupil  # TST-PUPIL-006: parent retains the value without rewriting it.


def test_lash_shadow_has_lash_owner_but_legacy_public_identity():  # REL-PUPIL-LASH: the pilot proves ownership correction without API break.
    from visual_engine.components.face.eyes.lashes.effects import LashShadowSpec  # REL-PUPIL-LASH: canonical sibling owner.
    from visual_engine.geometry import LashShadowSpec as LegacyLashShadowSpec  # REL-PUPIL-LASH: historical public API remains valid.
    assert LegacyLashShadowSpec is LashShadowSpec  # REL-PUPIL-LASH: one implementation owner survives compatibility export.
