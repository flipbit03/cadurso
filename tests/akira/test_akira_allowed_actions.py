"""
Tests for the get_allowed_actions() API in the Akira universe.

These tests verify that the allowed actions API correctly returns all actions
an actor can perform on a resource, using the ABAC-style Akira authorization system.
"""

import pytest

from cadurso import Cadurso

from .conftest import (
    Bike,
    BikePermission,
    Character,
    FacilityPermission,
    Location,
    LocationPermission,
    MilitaryFacility,
    PsychicPermission,
    PsychicPower,
)


def test_kaneda_allowed_actions_on_own_bike(
    akira_authz: Cadurso, kaneda: Character, kaneda_bike: Bike
) -> None:
    """Kaneda can DRIVE and MODIFY his own bike, but not EXPLODE it."""
    allowed = akira_authz.get_allowed_actions(kaneda, kaneda_bike)

    assert BikePermission.DRIVE in allowed
    assert BikePermission.MODIFY in allowed
    assert BikePermission.EXPLODE not in allowed


def test_colonel_allowed_actions_on_any_bike(
    akira_authz: Cadurso, colonel: Character, kaneda_bike: Bike, tetsuo_bike: Bike
) -> None:
    """The Colonel can DRIVE any bike (authority), but cannot MODIFY or EXPLODE."""
    allowed_on_kaneda_bike = akira_authz.get_allowed_actions(colonel, kaneda_bike)
    assert BikePermission.DRIVE in allowed_on_kaneda_bike
    assert BikePermission.MODIFY not in allowed_on_kaneda_bike
    assert BikePermission.EXPLODE not in allowed_on_kaneda_bike

    allowed_on_tetsuo_bike = akira_authz.get_allowed_actions(colonel, tetsuo_bike)
    assert BikePermission.DRIVE in allowed_on_tetsuo_bike
    assert BikePermission.MODIFY not in allowed_on_tetsuo_bike


def test_tetsuo_actions_grow_with_psychic_power(
    akira_authz: Cadurso, tetsuo: Character, kaneda_bike: Bike
) -> None:
    """Tetsuo's allowed actions on bikes change as his psychic power grows."""
    # At initial psychic_level=8, Tetsuo can only drive his own bike
    # He shouldn't be able to EXPLODE any bike yet
    allowed_low_power = akira_authz.get_allowed_actions(tetsuo, kaneda_bike)
    assert BikePermission.EXPLODE not in allowed_low_power

    # At psychic_level=90, Tetsuo gains the ability to EXPLODE bikes
    tetsuo.psychic_level = 90
    allowed_high_power = akira_authz.get_allowed_actions(tetsuo, kaneda_bike)
    assert BikePermission.EXPLODE in allowed_high_power


def test_tetsuo_allowed_actions_on_own_bike(
    akira_authz: Cadurso, tetsuo: Character, tetsuo_bike: Bike
) -> None:
    """Tetsuo can DRIVE and MODIFY his own bike."""
    allowed = akira_authz.get_allowed_actions(tetsuo, tetsuo_bike)

    assert BikePermission.DRIVE in allowed
    assert BikePermission.MODIFY in allowed


def test_colonel_full_facility_permissions(
    akira_authz: Cadurso,
    colonel: Character,
    olympic_stadium: MilitaryFacility,
    research_lab: MilitaryFacility,
) -> None:
    """The Colonel has all facility permissions on any facility."""
    allowed_stadium = akira_authz.get_allowed_actions(colonel, olympic_stadium)
    assert FacilityPermission.ENTER in allowed_stadium
    assert FacilityPermission.SHUTDOWN in allowed_stadium
    assert FacilityPermission.LAUNCH_STRIKE in allowed_stadium

    allowed_lab = akira_authz.get_allowed_actions(colonel, research_lab)
    assert FacilityPermission.ENTER in allowed_lab
    assert FacilityPermission.SHUTDOWN in allowed_lab
    assert FacilityPermission.LAUNCH_STRIKE in allowed_lab


def test_doctor_facility_permissions(
    akira_authz: Cadurso,
    doctor: Character,
    research_lab: MilitaryFacility,
    olympic_stadium: MilitaryFacility,
) -> None:
    """Dr. Onishi can only ENTER his own lab (as overseer), not the stadium."""
    # Can enter his own lab (overseer), but cannot shutdown or launch strikes
    allowed_lab = akira_authz.get_allowed_actions(doctor, research_lab)
    assert FacilityPermission.ENTER in allowed_lab
    assert FacilityPermission.SHUTDOWN not in allowed_lab
    assert FacilityPermission.LAUNCH_STRIKE not in allowed_lab

    # Cannot do anything at the stadium (not overseer, not colonel, psychic_level=0 < security_level=10)
    allowed_stadium = akira_authz.get_allowed_actions(doctor, olympic_stadium)
    assert allowed_stadium == set()


def test_tetsuo_facility_access_by_psychic_power(
    akira_authz: Cadurso,
    tetsuo: Character,
    research_lab: MilitaryFacility,
    olympic_stadium: MilitaryFacility,
) -> None:
    """Tetsuo can infiltrate facilities when his psychic level exceeds security level."""
    # Initial psychic_level=8, lab security_level=8 - can enter lab
    allowed_lab = akira_authz.get_allowed_actions(tetsuo, research_lab)
    assert FacilityPermission.ENTER in allowed_lab

    # Initial psychic_level=8, stadium security_level=10 - cannot enter stadium yet
    allowed_stadium = akira_authz.get_allowed_actions(tetsuo, olympic_stadium)
    assert FacilityPermission.ENTER not in allowed_stadium

    # Boost psychic power - now can enter stadium
    tetsuo.psychic_level = 50
    allowed_stadium_stronger = akira_authz.get_allowed_actions(tetsuo, olympic_stadium)
    assert FacilityPermission.ENTER in allowed_stadium_stronger


def test_kei_no_bike_permissions(
    akira_authz: Cadurso, kei: Character, kaneda_bike: Bike
) -> None:
    """Kei has no permissions on bikes she doesn't own."""
    allowed = akira_authz.get_allowed_actions(kei, kaneda_bike)

    assert allowed == set()


def test_doctor_psychic_power_permissions(
    akira_authz: Cadurso, doctor: Character, telekinesis: PsychicPower
) -> None:
    """Dr. Onishi can use powers he discovered, regardless of psychic level."""
    allowed = akira_authz.get_allowed_actions(doctor, telekinesis)

    # Discovered by doctor, so can use it
    assert PsychicPermission.USE_POWER in allowed


def test_tetsuo_psychic_power_permissions(
    akira_authz: Cadurso, tetsuo: Character, telekinesis: PsychicPower
) -> None:
    """Tetsuo can use psychic powers when his level meets the requirement."""
    # Initial psychic_level=8, telekinesis requires 50
    allowed_weak = akira_authz.get_allowed_actions(tetsuo, telekinesis)
    assert PsychicPermission.USE_POWER not in allowed_weak

    # Boost to required level
    tetsuo.psychic_level = 50
    allowed_strong = akira_authz.get_allowed_actions(tetsuo, telekinesis)
    assert PsychicPermission.USE_POWER in allowed_strong


def test_kaneda_brawl_anywhere(
    akira_authz: Cadurso,
    kaneda: Character,
    harukiya: Location,
    neo_tokyo: Location,
) -> None:
    """Kaneda can brawl in any location."""
    allowed_harukiya = akira_authz.get_allowed_actions(kaneda, harukiya)
    assert LocationPermission.BRAWL in allowed_harukiya

    allowed_neo_tokyo = akira_authz.get_allowed_actions(kaneda, neo_tokyo)
    assert LocationPermission.BRAWL in allowed_neo_tokyo


def test_fluent_api_consistency(
    akira_authz: Cadurso, kaneda: Character, kaneda_bike: Bike
) -> None:
    """The fluent API returns the same result as the direct method."""
    direct_result = akira_authz.get_allowed_actions(kaneda, kaneda_bike)
    fluent_result = akira_authz.can(kaneda).allowed_actions_on(kaneda_bike)

    assert direct_result == fluent_result


@pytest.mark.asyncio
async def test_tetsuo_location_actions_async(
    akira_authz: Cadurso, tetsuo: Character, neo_tokyo: Location
) -> None:
    """Test async variant with the DESTROY location rule (which is async)."""
    # At low power, Tetsuo cannot destroy Neo Tokyo
    allowed_weak = await akira_authz.get_allowed_actions_async(tetsuo, neo_tokyo)
    assert LocationPermission.DESTROY not in allowed_weak

    # At full meltdown (psychic_level=100), Tetsuo can destroy Neo Tokyo
    tetsuo.psychic_level = 100
    allowed_meltdown = await akira_authz.get_allowed_actions_async(tetsuo, neo_tokyo)
    assert LocationPermission.DESTROY in allowed_meltdown


@pytest.mark.asyncio
async def test_fluent_api_async_consistency(
    akira_authz: Cadurso, tetsuo: Character, neo_tokyo: Location
) -> None:
    """The async fluent API returns the same result as the direct async method."""
    tetsuo.psychic_level = 100

    direct_result = await akira_authz.get_allowed_actions_async(tetsuo, neo_tokyo)
    fluent_result = await akira_authz.can(tetsuo).allowed_actions_on_async(neo_tokyo)

    assert direct_result == fluent_result
