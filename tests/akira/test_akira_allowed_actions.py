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

    # NOT allowed: BikePermission.EXPLODE
    assert allowed == {BikePermission.DRIVE, BikePermission.MODIFY}


def test_colonel_allowed_actions_on_any_bike(
    akira_authz: Cadurso, colonel: Character, kaneda_bike: Bike, tetsuo_bike: Bike
) -> None:
    """The Colonel can DRIVE any bike (authority), but cannot MODIFY or EXPLODE."""
    # NOT allowed: BikePermission.MODIFY, BikePermission.EXPLODE
    allowed_on_kaneda_bike = akira_authz.get_allowed_actions(colonel, kaneda_bike)
    assert allowed_on_kaneda_bike == {BikePermission.DRIVE}

    # NOT allowed: BikePermission.MODIFY, BikePermission.EXPLODE
    allowed_on_tetsuo_bike = akira_authz.get_allowed_actions(colonel, tetsuo_bike)
    assert allowed_on_tetsuo_bike == {BikePermission.DRIVE}


def test_tetsuo_actions_grow_with_psychic_power(
    akira_authz: Cadurso, tetsuo: Character, kaneda_bike: Bike
) -> None:
    """
    Tetsuo's allowed actions on bikes change as his psychic power grows.

    Edge case: Verifies that get_allowed_actions() re-evaluates rules on each call
    and does not cache results. This is critical for ABAC where permissions depend
    on mutable actor attributes.
    """
    # At initial psychic_level=8, Tetsuo cannot do anything on Kaneda's bike
    allowed_low_power = akira_authz.get_allowed_actions(tetsuo, kaneda_bike)
    assert allowed_low_power == set()

    # At psychic_level=90, Tetsuo gains the ability to EXPLODE bikes
    tetsuo.psychic_level = 90
    allowed_high_power = akira_authz.get_allowed_actions(tetsuo, kaneda_bike)
    assert allowed_high_power == {BikePermission.EXPLODE}


def test_tetsuo_allowed_actions_on_own_bike(
    akira_authz: Cadurso, tetsuo: Character, tetsuo_bike: Bike
) -> None:
    """Tetsuo can DRIVE and MODIFY his own bike."""
    allowed = akira_authz.get_allowed_actions(tetsuo, tetsuo_bike)

    # NOT allowed: BikePermission.EXPLODE (psychic_level too low)
    assert allowed == {BikePermission.DRIVE, BikePermission.MODIFY}


def test_colonel_full_facility_permissions(
    akira_authz: Cadurso,
    colonel: Character,
    olympic_stadium: MilitaryFacility,
    research_lab: MilitaryFacility,
) -> None:
    """
    The Colonel has all facility permissions on any facility.

    Edge case: Verifies that get_allowed_actions() finds ALL matching actions,
    not just the first one. The method must iterate through all rule storage keys
    and collect every action that passes evaluation.
    """
    allowed_stadium = akira_authz.get_allowed_actions(colonel, olympic_stadium)
    assert allowed_stadium == {
        FacilityPermission.ENTER,
        FacilityPermission.SHUTDOWN,
        FacilityPermission.LAUNCH_STRIKE,
    }

    allowed_lab = akira_authz.get_allowed_actions(colonel, research_lab)
    assert allowed_lab == {
        FacilityPermission.ENTER,
        FacilityPermission.SHUTDOWN,
        FacilityPermission.LAUNCH_STRIKE,
    }


def test_doctor_facility_permissions(
    akira_authz: Cadurso,
    doctor: Character,
    research_lab: MilitaryFacility,
    olympic_stadium: MilitaryFacility,
) -> None:
    """Dr. Onishi can only ENTER his own lab (as overseer), not the stadium."""
    # NOT allowed: FacilityPermission.SHUTDOWN, FacilityPermission.LAUNCH_STRIKE
    allowed_lab = akira_authz.get_allowed_actions(doctor, research_lab)
    assert allowed_lab == {FacilityPermission.ENTER}

    # Cannot do anything at the stadium (not overseer, not colonel, psychic_level=0 < security_level=10)
    allowed_stadium = akira_authz.get_allowed_actions(doctor, olympic_stadium)
    assert allowed_stadium == set()


def test_tetsuo_facility_access_by_psychic_power(
    akira_authz: Cadurso,
    tetsuo: Character,
    research_lab: MilitaryFacility,
    olympic_stadium: MilitaryFacility,
) -> None:
    """
    Tetsuo can infiltrate facilities when his psychic level exceeds security level.

    Edge case: Another test for dynamic attribute-based access control.
    Permissions change based on comparing actor.psychic_level vs resource.security_level.
    """
    # Initial psychic_level=8, lab security_level=8 - can enter lab
    # NOT allowed: FacilityPermission.SHUTDOWN, FacilityPermission.LAUNCH_STRIKE
    allowed_lab = akira_authz.get_allowed_actions(tetsuo, research_lab)
    assert allowed_lab == {FacilityPermission.ENTER}

    # Initial psychic_level=8, stadium security_level=10 - cannot enter stadium yet
    allowed_stadium = akira_authz.get_allowed_actions(tetsuo, olympic_stadium)
    assert allowed_stadium == set()

    # Boost psychic power - now can enter stadium
    # NOT allowed: FacilityPermission.SHUTDOWN, FacilityPermission.LAUNCH_STRIKE
    tetsuo.psychic_level = 50
    allowed_stadium_stronger = akira_authz.get_allowed_actions(tetsuo, olympic_stadium)
    assert allowed_stadium_stronger == {FacilityPermission.ENTER}


def test_kei_no_bike_permissions(
    akira_authz: Cadurso, kei: Character, kaneda_bike: Bike
) -> None:
    """
    Kei has no permissions on bikes she doesn't own.

    Edge case: Verifies that get_allowed_actions() correctly returns an empty set
    when no rules match, rather than erroring or returning unexpected values.
    """
    allowed = akira_authz.get_allowed_actions(kei, kaneda_bike)

    assert allowed == set()


def test_doctor_psychic_power_permissions(
    akira_authz: Cadurso, doctor: Character, telekinesis: PsychicPower
) -> None:
    """Dr. Onishi can use powers he discovered, regardless of psychic level."""
    allowed = akira_authz.get_allowed_actions(doctor, telekinesis)

    assert allowed == {PsychicPermission.USE_POWER}


def test_tetsuo_psychic_power_permissions(
    akira_authz: Cadurso, tetsuo: Character, telekinesis: PsychicPower
) -> None:
    """
    Tetsuo can use psychic powers when his level meets the requirement.

    Edge case: Tests dynamic attribute evaluation where the permission threshold
    is defined on the resource (power.min_required_level), not the actor.
    """
    # Initial psychic_level=8, telekinesis requires 50
    allowed_weak = akira_authz.get_allowed_actions(tetsuo, telekinesis)
    assert allowed_weak == set()

    # Boost to required level
    tetsuo.psychic_level = 50
    allowed_strong = akira_authz.get_allowed_actions(tetsuo, telekinesis)
    assert allowed_strong == {PsychicPermission.USE_POWER}


def test_kaneda_brawl_anywhere(
    akira_authz: Cadurso,
    kaneda: Character,
    harukiya: Location,
    neo_tokyo: Location,
) -> None:
    """Kaneda can brawl in any location."""
    # NOT allowed: LocationPermission.DESTROY
    allowed_harukiya = akira_authz.get_allowed_actions(kaneda, harukiya)
    assert allowed_harukiya == {LocationPermission.BRAWL}

    # NOT allowed: LocationPermission.DESTROY
    allowed_neo_tokyo = akira_authz.get_allowed_actions(kaneda, neo_tokyo)
    assert allowed_neo_tokyo == {LocationPermission.BRAWL}


def test_fluent_api_consistency(
    akira_authz: Cadurso, kaneda: Character, kaneda_bike: Bike
) -> None:
    """
    The fluent API returns the same result as the direct method.

    Edge case: Ensures can(actor).allowed_actions_on(resource) is functionally
    equivalent to get_allowed_actions(actor, resource). Both code paths must
    produce identical results.
    """
    direct_result = akira_authz.get_allowed_actions(kaneda, kaneda_bike)
    fluent_result = akira_authz.can(kaneda).allowed_actions_on(kaneda_bike)

    assert direct_result == fluent_result


@pytest.mark.asyncio
async def test_fluent_api_async_consistency(
    akira_authz: Cadurso, tetsuo: Character, neo_tokyo: Location
) -> None:
    """
    The async fluent API returns the same result as the direct async method.

    Edge case: Ensures can(actor).allowed_actions_on_async(resource) is functionally
    equivalent to get_allowed_actions_async(actor, resource).
    """
    tetsuo.psychic_level = 100

    direct_result = await akira_authz.get_allowed_actions_async(tetsuo, neo_tokyo)
    fluent_result = await akira_authz.can(tetsuo).allowed_actions_on_async(neo_tokyo)

    assert direct_result == fluent_result


def test_sync_api_evaluates_async_rules(
    akira_authz: Cadurso, tetsuo: Character, neo_tokyo: Location
) -> None:
    """
    The sync get_allowed_actions() correctly evaluates async rules via asyncio.run().

    Edge case: The LocationPermission.DESTROY rule is defined with 'async def'.
    The sync API must detect this and use asyncio.run() to evaluate it.
    This ensures users can call the sync API even when some rules are async.
    """
    # At low power, Tetsuo cannot destroy Neo Tokyo
    allowed_weak = akira_authz.get_allowed_actions(tetsuo, neo_tokyo)
    assert allowed_weak == set()

    # At full meltdown (psychic_level=100), Tetsuo can destroy Neo Tokyo
    tetsuo.psychic_level = 100
    allowed_meltdown = akira_authz.get_allowed_actions(tetsuo, neo_tokyo)
    assert allowed_meltdown == {LocationPermission.DESTROY}


@pytest.mark.asyncio
async def test_async_api_evaluates_async_rules(
    akira_authz: Cadurso, tetsuo: Character, neo_tokyo: Location
) -> None:
    """
    The async get_allowed_actions_async() correctly awaits async rules.

    Edge case: The LocationPermission.DESTROY rule is defined with 'async def'.
    The async API must properly await these coroutines. This is the recommended
    approach when already in an async context (e.g., FastAPI).
    """
    # At low power, Tetsuo cannot destroy Neo Tokyo
    allowed_weak = await akira_authz.get_allowed_actions_async(tetsuo, neo_tokyo)
    assert allowed_weak == set()

    # At full meltdown (psychic_level=100), Tetsuo can destroy Neo Tokyo
    tetsuo.psychic_level = 100
    allowed_meltdown = await akira_authz.get_allowed_actions_async(tetsuo, neo_tokyo)
    assert allowed_meltdown == {LocationPermission.DESTROY}
