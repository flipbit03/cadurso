import pytest

from cadurso import Cadurso
from tests.akira.conftest import (
    Character,
    Location,
    LocationPermission,
)


@pytest.mark.asyncio
async def test_tetsuo_destroy_neotokyo_only_when_ready_async(
    akira_authz: Cadurso, tetsuo: Character, neo_tokyo: Location
) -> None:
    """
    Wiping Neo Tokyo off the map isn't a casual feat.
    Tetsuo needs to hit a terrifying psychic_level=100 first.
    """
    assert (
        not await akira_authz.can(tetsuo)
        .do(LocationPermission.DESTROY)
        .on_async(neo_tokyo)
    )

    tetsuo.psychic_level = 100
    assert (
        await akira_authz.can(tetsuo).do(LocationPermission.DESTROY).on_async(neo_tokyo)
    )


# Sync version of the above
def test_tetsuo_destroy_neotokyo_only_when_ready_sync(
    akira_authz: Cadurso, tetsuo: Character, neo_tokyo: Location
) -> None:
    """
    Wiping Neo Tokyo off the map isn't a casual feat.
    Tetsuo needs to hit a terrifying psychic_level=100 first.
    """
    assert not akira_authz.can(tetsuo).do(LocationPermission.DESTROY).on(neo_tokyo)

    tetsuo.psychic_level = 100
    assert akira_authz.can(tetsuo).do(LocationPermission.DESTROY).on(neo_tokyo)


def test_colonel_cannot_destroy_locations(
    akira_authz: Cadurso, colonel: Character, neo_tokyo: Location, harukiya: Location
) -> None:
    """
    The Colonel maintains control, but an all-out personal annihilation
    of these places isn't within his scope.
    """
    assert not akira_authz.is_allowed(colonel, LocationPermission.DESTROY, neo_tokyo)
    assert not akira_authz.is_allowed(colonel, LocationPermission.DESTROY, harukiya)


def test_tetsuo_brawl_harukiya(
    akira_authz: Cadurso, tetsuo: Character, harukiya: Location
) -> None:
    """
    A bar fight at Harukiya is just Tetsuo's style,
    but only if he's sufficiently powered up (>=60).
    """
    assert not akira_authz.is_allowed(tetsuo, LocationPermission.BRAWL, harukiya)

    tetsuo.psychic_level = 60
    assert akira_authz.is_allowed(tetsuo, LocationPermission.BRAWL, harukiya)


def test_kaneda_brawl_anywhere(
    akira_authz: Cadurso, kaneda: Character, harukiya: Location, neo_tokyo: Location
) -> None:
    """
    Kaneda doesn't need psychic muscle to throw punches.
    If there's trouble, he'll be in the thick of it.
    """
    assert akira_authz.is_allowed(kaneda, LocationPermission.BRAWL, harukiya)
    assert akira_authz.is_allowed(kaneda, LocationPermission.BRAWL, neo_tokyo)
