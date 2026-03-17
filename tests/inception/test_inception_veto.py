"""Tests exercising the Veto mechanism and AuthorizationDecision in the Inception universe."""

import pytest

from cadurso import Cadurso
from cadurso.exceptions import Veto

from .conftest import Dreamer, DreamLevel, DreamPermission, Role, Totem, TotemPermission

# ---------------------------------------------------------------------------
# Veto with reason
# ---------------------------------------------------------------------------


def test_collapsed_level_vetoes_navigation(
    inception_universe: Cadurso, cobb: Dreamer, limbo: DreamLevel
) -> None:
    decision = inception_universe.is_allowed(cobb, DreamPermission.NAVIGATE, limbo)
    assert not decision
    assert decision.reason == "dream level has collapsed"


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


# ---------------------------------------------------------------------------
# Veto without reason
# ---------------------------------------------------------------------------


def test_veto_without_reason() -> None:
    """A Veto with no argument gives reason=None."""
    c = Cadurso()

    @c.add_rule("act")
    def always_vetoed(actor: Dreamer, resource: DreamLevel) -> bool:
        raise Veto()

    c.freeze()

    dreamer = Dreamer(id=99, name="Test", role=Role.EXTRACTOR)
    level = DreamLevel(name="Test", depth=1, architect=dreamer)
    decision = c.is_allowed(dreamer, "act", level)
    assert not decision
    assert decision.reason is None


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


# ---------------------------------------------------------------------------
# Non-Veto exceptions propagate normally
# ---------------------------------------------------------------------------


def test_non_veto_exception_propagates() -> None:
    """Non-Veto exceptions in rules are not caught — they propagate to the caller."""
    c = Cadurso()

    @c.add_rule("act")
    def broken_rule(actor: Dreamer, resource: DreamLevel) -> bool:
        raise RuntimeError("something went wrong")

    c.freeze()

    dreamer = Dreamer(id=99, name="Test", role=Role.EXTRACTOR)
    level = DreamLevel(name="Test", depth=1, architect=dreamer)

    with pytest.raises(RuntimeError, match="something went wrong"):
        c.is_allowed(dreamer, "act", level)
