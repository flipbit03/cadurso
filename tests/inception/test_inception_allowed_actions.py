"""Tests for get_allowed_actions / get_allowed_actions_async with Veto."""

import pytest

from cadurso import Cadurso

from .conftest import DreamLevel, DreamPermission, Dreamer, Totem, TotemPermission


class TestGetAllowedActions:
    """get_allowed_actions catches Veto per-action and excludes vetoed actions."""

    def test_team_member_on_normal_level(
        self, inception_universe: Cadurso, arthur: Dreamer, hotel_level: DreamLevel
    ) -> None:
        actions = inception_universe.get_allowed_actions(arthur, hotel_level)
        assert DreamPermission.NAVIGATE in actions
        assert DreamPermission.ARCHITECT in actions
        assert DreamPermission.KICK in actions

    def test_mark_on_shallow_level(
        self, inception_universe: Cadurso, fischer: Dreamer, city_level: DreamLevel
    ) -> None:
        actions = inception_universe.get_allowed_actions(fischer, city_level)
        assert DreamPermission.NAVIGATE in actions
        # Fischer can't do anything else
        assert DreamPermission.ARCHITECT not in actions
        assert DreamPermission.KICK not in actions
        assert DreamPermission.PLANT_IDEA not in actions

    def test_collapsed_level_vetoes_all_dream_actions(
        self, inception_universe: Cadurso, cobb: Dreamer, limbo: DreamLevel
    ) -> None:
        """Limbo is collapsed — all dream-level actions should be vetoed."""
        actions = inception_universe.get_allowed_actions(cobb, limbo)
        assert DreamPermission.NAVIGATE not in actions
        assert DreamPermission.ARCHITECT not in actions

    def test_extractor_on_deep_level(
        self, inception_universe: Cadurso, cobb: Dreamer, snow_fortress: DreamLevel
    ) -> None:
        actions = inception_universe.get_allowed_actions(cobb, snow_fortress)
        assert DreamPermission.NAVIGATE in actions
        assert DreamPermission.PLANT_IDEA in actions

    def test_extractor_on_shallow_level_plant_vetoed(
        self, inception_universe: Cadurso, cobb: Dreamer, city_level: DreamLevel
    ) -> None:
        """Cobb can navigate but not plant ideas on a shallow level (depth < 3)."""
        actions = inception_universe.get_allowed_actions(cobb, city_level)
        assert DreamPermission.NAVIGATE in actions
        assert DreamPermission.PLANT_IDEA not in actions

    def test_totem_owner_gets_inspect(
        self, inception_universe: Cadurso, cobb: Dreamer, cobbs_totem: Totem
    ) -> None:
        actions = inception_universe.get_allowed_actions(cobb, cobbs_totem)
        assert TotemPermission.INSPECT in actions

    def test_non_owner_totem_vetoed(
        self, inception_universe: Cadurso, arthur: Dreamer, cobbs_totem: Totem
    ) -> None:
        actions = inception_universe.get_allowed_actions(arthur, cobbs_totem)
        assert TotemPermission.INSPECT not in actions


class TestGetAllowedActionsAsync:
    """Async variant of get_allowed_actions with Veto."""

    @pytest.mark.asyncio
    async def test_async_team_member_on_normal_level(
        self, inception_universe: Cadurso, arthur: Dreamer, hotel_level: DreamLevel
    ) -> None:
        actions = await inception_universe.get_allowed_actions_async(arthur, hotel_level)
        assert DreamPermission.NAVIGATE in actions
        assert DreamPermission.ARCHITECT in actions

    @pytest.mark.asyncio
    async def test_async_collapsed_level_vetoes(
        self, inception_universe: Cadurso, cobb: Dreamer, limbo: DreamLevel
    ) -> None:
        actions = await inception_universe.get_allowed_actions_async(cobb, limbo)
        assert DreamPermission.NAVIGATE not in actions

    @pytest.mark.asyncio
    async def test_async_non_owner_totem_vetoed(
        self, inception_universe: Cadurso, arthur: Dreamer, cobbs_totem: Totem
    ) -> None:
        actions = await inception_universe.get_allowed_actions_async(arthur, cobbs_totem)
        assert TotemPermission.INSPECT not in actions
