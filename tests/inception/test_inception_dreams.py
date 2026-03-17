"""Tests verifying normal True/False behavior is preserved without any Veto involvement."""

from cadurso import Cadurso

from .conftest import DreamLevel, DreamPermission, Dreamer, Totem, TotemPermission


class TestDreamNavigation:
    """Navigation rules without Veto — normal boolean flow."""

    def test_team_member_navigates(
        self, inception_universe: Cadurso, arthur: Dreamer, hotel_level: DreamLevel
    ) -> None:
        assert inception_universe.is_allowed(arthur, DreamPermission.NAVIGATE, hotel_level)

    def test_architect_navigates(
        self, inception_universe: Cadurso, ariadne: Dreamer, snow_fortress: DreamLevel
    ) -> None:
        assert inception_universe.is_allowed(ariadne, DreamPermission.NAVIGATE, snow_fortress)

    def test_forger_navigates(
        self, inception_universe: Cadurso, eames: Dreamer, city_level: DreamLevel
    ) -> None:
        assert inception_universe.is_allowed(eames, DreamPermission.NAVIGATE, city_level)

    def test_mark_cannot_navigate_deep_levels(
        self, inception_universe: Cadurso, fischer: Dreamer, snow_fortress: DreamLevel
    ) -> None:
        assert not inception_universe.is_allowed(fischer, DreamPermission.NAVIGATE, snow_fortress)

    def test_mark_navigates_shallow_levels(
        self, inception_universe: Cadurso, fischer: Dreamer, city_level: DreamLevel
    ) -> None:
        assert inception_universe.is_allowed(fischer, DreamPermission.NAVIGATE, city_level)

    def test_projection_cannot_navigate(
        self, inception_universe: Cadurso, mal: Dreamer, city_level: DreamLevel
    ) -> None:
        assert not inception_universe.is_allowed(mal, DreamPermission.NAVIGATE, city_level)


class TestArchitecting:
    """Only the architect of a level can reshape it (non-collapsed levels)."""

    def test_architect_reshapes_own_level(
        self, inception_universe: Cadurso, ariadne: Dreamer, snow_fortress: DreamLevel
    ) -> None:
        assert inception_universe.is_allowed(ariadne, DreamPermission.ARCHITECT, snow_fortress)

    def test_non_architect_cannot_reshape(
        self, inception_universe: Cadurso, eames: Dreamer, snow_fortress: DreamLevel
    ) -> None:
        assert not inception_universe.is_allowed(eames, DreamPermission.ARCHITECT, snow_fortress)

    def test_arthur_reshapes_hotel(
        self, inception_universe: Cadurso, arthur: Dreamer, hotel_level: DreamLevel
    ) -> None:
        assert inception_universe.is_allowed(arthur, DreamPermission.ARCHITECT, hotel_level)


class TestKicks:
    """Kick permissions — no Veto involved here."""

    def test_point_man_can_kick(
        self, inception_universe: Cadurso, arthur: Dreamer, hotel_level: DreamLevel
    ) -> None:
        assert inception_universe.is_allowed(arthur, DreamPermission.KICK, hotel_level)

    def test_anyone_can_kick_in_shallow(
        self, inception_universe: Cadurso, eames: Dreamer, city_level: DreamLevel
    ) -> None:
        assert inception_universe.is_allowed(eames, DreamPermission.KICK, city_level)

    def test_non_point_man_cannot_kick_deep(
        self, inception_universe: Cadurso, eames: Dreamer, snow_fortress: DreamLevel
    ) -> None:
        assert not inception_universe.is_allowed(eames, DreamPermission.KICK, snow_fortress)

    def test_mark_cannot_kick(
        self, inception_universe: Cadurso, fischer: Dreamer, city_level: DreamLevel
    ) -> None:
        assert not inception_universe.is_allowed(fischer, DreamPermission.KICK, city_level)


class TestTotems:
    """Totem inspection — owner allowed, everyone else vetoed."""

    def test_owner_inspects_own_totem(
        self, inception_universe: Cadurso, cobb: Dreamer, cobbs_totem: Totem
    ) -> None:
        assert inception_universe.is_allowed(cobb, TotemPermission.INSPECT, cobbs_totem)

    def test_arthur_inspects_own_totem(
        self, inception_universe: Cadurso, arthur: Dreamer, arthurs_totem: Totem
    ) -> None:
        assert inception_universe.is_allowed(arthur, TotemPermission.INSPECT, arthurs_totem)
