"""Tests exercising the Veto mechanism in the Inception universe."""

from cadurso import Cadurso

from .conftest import Dreamer, DreamLevel, DreamPermission, Totem, TotemPermission

# ---------------------------------------------------------------------------
# Veto with reason
# ---------------------------------------------------------------------------


def test_collapsed_level_vetoes_navigation(
    inception_universe: Cadurso, cobb: Dreamer, limbo: DreamLevel
) -> None:
    decision = inception_universe.is_allowed(cobb, DreamPermission.NAVIGATE, limbo)
    assert not decision
    assert decision.reason == "dream level has collapsed"

    # can().do().on() carries the same veto reason
    can_cobb_navigate_limbo = (
        inception_universe.can(cobb).do(DreamPermission.NAVIGATE).on(limbo)
    )
    assert not can_cobb_navigate_limbo
    assert can_cobb_navigate_limbo.reason == "dream level has collapsed"


def test_collapsed_level_vetoes_architecting(
    inception_universe: Cadurso, cobb: Dreamer, limbo: DreamLevel
) -> None:
    decision = inception_universe.is_allowed(cobb, DreamPermission.ARCHITECT, limbo)
    assert not decision
    assert decision.reason == "dream level has collapsed — cannot reshape"


def test_shallow_level_vetoes_inception(
    inception_universe: Cadurso, cobb: Dreamer, city_level: DreamLevel
) -> None:
    decision = inception_universe.is_allowed(
        cobb, DreamPermission.PLANT_IDEA, city_level
    )
    assert not decision
    assert decision.reason == "dream is not deep enough for inception"


def test_totem_veto_reason_when_not_owner(
    inception_universe: Cadurso, eames: Dreamer, cobbs_totem: Totem
) -> None:
    decision = inception_universe.is_allowed(
        eames, TotemPermission.INSPECT, cobbs_totem
    )
    assert not decision
    assert decision.reason == "never let someone else touch your totem"

    # can().do().on() carries the same veto reason
    can_eames_inspect_cobbs_totem = (
        inception_universe.can(eames).do(TotemPermission.INSPECT).on(cobbs_totem)
    )
    assert not can_eames_inspect_cobbs_totem
    assert (
        can_eames_inspect_cobbs_totem.reason
        == "never let someone else touch your totem"
    )


# ---------------------------------------------------------------------------
# Veto overrides True
# ---------------------------------------------------------------------------


def test_veto_overrides_allow_regardless_of_order(
    inception_universe: Cadurso, cobb: Dreamer, limbo: DreamLevel
) -> None:
    """Cobb is a team member (navigate rule returns True), but limbo is collapsed (Veto).
    Regardless of which rule runs first, the result must be denied."""
    decision = inception_universe.is_allowed(cobb, DreamPermission.NAVIGATE, limbo)
    assert not decision
    assert decision.reason == "dream level has collapsed"


def test_cobb_can_plant_idea_deep_but_not_shallow(
    inception_universe: Cadurso,
    cobb: Dreamer,
    snow_fortress: DreamLevel,
    hotel_level: DreamLevel,
) -> None:
    """Cobb is an extractor (allowed), snow fortress is deep enough (no veto)."""
    deep = inception_universe.is_allowed(
        cobb, DreamPermission.PLANT_IDEA, snow_fortress
    )
    assert deep
    assert deep.allowed is True

    # Hotel is depth 2 — too shallow, Veto fires.
    shallow = inception_universe.is_allowed(
        cobb, DreamPermission.PLANT_IDEA, hotel_level
    )
    assert not shallow
    assert shallow.reason == "dream is not deep enough for inception"
