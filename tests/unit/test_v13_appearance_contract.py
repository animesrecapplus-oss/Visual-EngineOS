from visual_engine.components.common.visual_contract import ContourContract, MaterialContract
from visual_engine.components.common.meta import AppearanceLayer
from visual_engine.runtime.appearance_contract import (
    AppearanceContribution, AppearanceDomain, build_appearance_input, resolve_appearance_contract,
)


def test_appearance_contract_preserves_domains_without_guessing():
    data = build_appearance_input(
        "eye",
        base_color="#AABBCC",
        contour=ContourContract(),
        material=MaterialContract(name="wet", roughness=0.2, transmission=0.1),
        opacity=0.8,
        visibility=0.9,
        active_states=("wet",),
        appearance_layers=(AppearanceLayer("iris", {"pattern": "procedural"}),),
        contributions=(AppearanceContribution("c1", AppearanceDomain.REFLECTION, "cornea", (("strength", 0.5),)),),
    )
    result = resolve_appearance_contract(data)
    assert result.base_color == "#aabbcc"
    assert result.material.name == "wet"
    assert result.contributions[0].domain is AppearanceDomain.REFLECTION
    assert AppearanceDomain.COLOR in result.unresolved_domains
    assert abs(result.effective_visibility - 0.72) < 1e-12
    assert result.layer_resolution_digest == ""


def test_contribution_ids_are_unique():
    try:
        build_appearance_input(
            "x", base_color="#ffffff", contour=ContourContract(), material=MaterialContract(),
            opacity=1, visibility=1,
            contributions=(
                AppearanceContribution("same", AppearanceDomain.BASE, "a"),
                AppearanceContribution("same", AppearanceDomain.BASE, "b"),
            ),
        )
    except ValueError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("duplicate contribution IDs must fail closed")
