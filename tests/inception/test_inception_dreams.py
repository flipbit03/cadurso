"""Tests verifying normal True/False behavior is preserved without any Veto involvement."""

from cadurso import Cadurso

from .conftest import Dreamer, DreamLevel, DreamPermission, Totem, TotemPermission

# ---------------------------------------------------------------------------
# Dream Navigation
# ---------------------------------------------------------------------------


def test_team_member_navigates(
    inception_universe: Cadurso, arthur: Dreamer, hotel_level: DreamLevel
) -> None:
    assert inception_universe.is_allowed(arthur, DreamPermission.NAVIGATE, hotel_level)


def test_architect_navigates(
    inception_universe: Cadurso, ariadne: Dreamer, snow_fortress: DreamLevel
) -> None:
    assert inception_universe.is_allowed(
        ariadne, DreamPermission.NAVIGATE, snow_fortress
    )


def test_forger_navigates(
    inception_universe: Cadurso, eames: Dreamer, city_level: DreamLevel
) -> None:
    assert inception_universe.is_allowed(eames, DreamPermission.NAVIGATE, city_level)


def test_mark_cannot_navigate_deep_levels(
    inception_universe: Cadurso, fischer: Dreamer, snow_fortress: DreamLevel
) -> None:
    assert not inception_universe.is_allowed(
        fischer, DreamPermission.NAVIGATE, snow_fortress
    )


def test_mark_navigates_shallow_levels(
    inception_universe: Cadurso, fischer: Dreamer, city_level: DreamLevel
) -> None:
    assert inception_universe.is_allowed(fischer, DreamPermission.NAVIGATE, city_level)


def test_projection_cannot_navigate(
    inception_universe: Cadurso, mal: Dreamer, city_level: DreamLevel
) -> None:
    assert not inception_universe.is_allowed(mal, DreamPermission.NAVIGATE, city_level)


# ---------------------------------------------------------------------------
# Architecting
# ---------------------------------------------------------------------------


def test_architect_reshapes_own_level(
    inception_universe: Cadurso, ariadne: Dreamer, snow_fortress: DreamLevel
) -> None:
    assert inception_universe.is_allowed(
        ariadne, DreamPermission.ARCHITECT, snow_fortress
    )


def test_non_architect_cannot_reshape(
    inception_universe: Cadurso, eames: Dreamer, snow_fortress: DreamLevel
) -> None:
    assert not inception_universe.is_allowed(
        eames, DreamPermission.ARCHITECT, snow_fortress
    )


def test_arthur_reshapes_hotel(
    inception_universe: Cadurso, arthur: Dreamer, hotel_level: DreamLevel
) -> None:
    assert inception_universe.is_allowed(arthur, DreamPermission.ARCHITECT, hotel_level)


# ---------------------------------------------------------------------------
# Kicks
# ---------------------------------------------------------------------------


def test_point_man_can_kick(
    inception_universe: Cadurso, arthur: Dreamer, hotel_level: DreamLevel
) -> None:
    assert inception_universe.is_allowed(arthur, DreamPermission.KICK, hotel_level)


def test_anyone_can_kick_in_shallow(
    inception_universe: Cadurso, eames: Dreamer, city_level: DreamLevel
) -> None:
    assert inception_universe.is_allowed(eames, DreamPermission.KICK, city_level)


def test_non_point_man_cannot_kick_deep(
    inception_universe: Cadurso, eames: Dreamer, snow_fortress: DreamLevel
) -> None:
    assert not inception_universe.is_allowed(eames, DreamPermission.KICK, snow_fortress)


def test_mark_cannot_kick(
    inception_universe: Cadurso, fischer: Dreamer, city_level: DreamLevel
) -> None:
    assert not inception_universe.is_allowed(fischer, DreamPermission.KICK, city_level)


# ---------------------------------------------------------------------------
# Totems
# ---------------------------------------------------------------------------


def test_owner_inspects_own_totem(
    inception_universe: Cadurso, cobb: Dreamer, cobbs_totem: Totem
) -> None:
    assert inception_universe.is_allowed(cobb, TotemPermission.INSPECT, cobbs_totem)


def test_arthur_inspects_own_totem(
    inception_universe: Cadurso, arthur: Dreamer, arthurs_totem: Totem
) -> None:
    assert inception_universe.is_allowed(arthur, TotemPermission.INSPECT, arthurs_totem)
