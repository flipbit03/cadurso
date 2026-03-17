"""Tests for is_allowed_async with Veto and AuthorizationDecision."""

import pytest

from cadurso import Cadurso

from .conftest import Dreamer, DreamLevel, DreamPermission, Totem, TotemPermission


@pytest.mark.asyncio
async def test_async_allowed(
    inception_universe: Cadurso, arthur: Dreamer, city_level: DreamLevel
) -> None:
    decision = await inception_universe.is_allowed_async(
        arthur, DreamPermission.NAVIGATE, city_level
    )
    assert decision
    assert decision.allowed is True
    assert decision.reason is None


@pytest.mark.asyncio
async def test_async_denied_no_veto(
    inception_universe: Cadurso, mal: Dreamer, city_level: DreamLevel
) -> None:
    decision = await inception_universe.is_allowed_async(
        mal, DreamPermission.NAVIGATE, city_level
    )
    assert not decision
    assert decision.reason is None


@pytest.mark.asyncio
async def test_async_veto_with_reason(
    inception_universe: Cadurso, cobb: Dreamer, limbo: DreamLevel
) -> None:
    decision = await inception_universe.is_allowed_async(
        cobb, DreamPermission.NAVIGATE, limbo
    )
    assert not decision
    assert decision.reason == "dream level has collapsed"


@pytest.mark.asyncio
async def test_async_totem_veto(
    inception_universe: Cadurso, eames: Dreamer, cobbs_totem: Totem
) -> None:
    decision = await inception_universe.is_allowed_async(
        eames, TotemPermission.INSPECT, cobbs_totem
    )
    assert not decision
    assert decision.reason == "never let someone else touch your totem"
