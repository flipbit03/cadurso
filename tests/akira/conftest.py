"""
A Cadurso-based authorization system set in the Akira (1988) universe, for testing.

The system is modelled as an ABAC-like system, where actors (e.g., Kaneda, Tetsuo) can perform actions on resources
based on attributes (e.g., psychic_level) and permissions (e.g., BikePermission.DRIVE).

The fixtures in this module represent the characters, locations, and permissions in the Akira universe.
"""

from dataclasses import dataclass
from enum import Enum, auto

import pytest

from cadurso import Cadurso

# ---------------------------------------------------------------------------
# Actors
# ---------------------------------------------------------------------------


@dataclass
class Character:
    """
    A main actor in Neo Tokyo, each with unique quirks and powers.

    :param id: A unique identifier for the character.
    :param name: The character's name (e.g., Kaneda, Tetsuo).
    :param psychic_level: Reflects how awakened (or dangerous) their psychic abilities are.
    :param admin: Some, like the Colonel, hold official authority in the city.
    """

    id: int
    name: str
    psychic_level: int = 0
    admin: bool = False

    def __hash__(self) -> int:
        return hash((self.id, self.name, self.psychic_level, self.admin))


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@dataclass
class Bike:
    """
    Iconic machines that roar across Neo Tokyo's neon streets.

    :param owner: The character who possesses or commandeered the bike.
    :param model: The bike’s model or design name.
    :param maximum_speed: The upper limit of its velocity on open roads.
    """

    owner: Character
    model: str
    maximum_speed: int

    def __hash__(self) -> int:
        return hash((self.owner, self.model, self.maximum_speed))


@dataclass
class MilitaryFacility:
    """
    Secure strongholds in the city, often concealing secrets best left alone.

    :param name: A descriptive identifier (e.g., 'Olympic Stadium - Akira Vault').
    :param security_level: The difficulty of breaking in without permission.
    :param overseer: The one officially in charge of the facility.
    """

    name: str
    security_level: int
    overseer: Character

    def __hash__(self) -> int:
        return hash((self.name, self.security_level, self.overseer))


@dataclass
class PsychicPower:
    """
    Specialized abilities discovered through questionable science.

    :param name: A label for the power (e.g., 'Telekinesis').
    :param min_required_level: The psychic_level necessary to wield it safely.
    :param discovered_by: The genius (or lunatic) who first stumbled upon this power.
    """

    name: str
    min_required_level: int
    discovered_by: Character | None

    def __hash__(self) -> int:
        return hash((self.name, self.min_required_level, self.discovered_by))


@dataclass
class Location:
    """
    A place in or around Neo Tokyo, which could be anything from an entire city
    to a seedy bar.

    :param name: The location's name (e.g., 'Neo Tokyo', 'Harukiya').
    :param population: Approximate count of souls that roam this location.
    """

    name: str
    population: int = 0

    def __hash__(self) -> int:
        return hash((self.name, self.population))


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------


class BikePermission(Enum):
    """Actions characters might try on bikes."""

    DRIVE = auto()
    MODIFY = auto()
    EXPLODE = auto()


class FacilityPermission(Enum):
    """Actions related to controlling or infiltrating a military facility."""

    ENTER = auto()
    SHUTDOWN = auto()
    LAUNCH_STRIKE = auto()


class PsychicPermission(Enum):
    """Actions related to tapping into psychic powers."""

    USE_POWER = auto()


class LocationPermission(Enum):
    """Actions that can be performed on or in a location."""

    DESTROY = auto()
    BRAWL = auto()


# ---------------------------------------------------------------------------
# FIXTURES: CHARACTERS
# ---------------------------------------------------------------------------


@pytest.fixture
def kaneda() -> Character:
    """Kaneda: a brash biker with a penchant for flashy heroics, no psychic talent."""
    return Character(id=1, name="Kaneda")


@pytest.fixture
def tetsuo() -> Character:
    """Tetsuo: begins with modest psychic_level=8, but he'll get stronger as the plot thickens."""
    return Character(id=2, name="Tetsuo", psychic_level=8)


@pytest.fixture
def kei() -> Character:
    """Kei: resourceful resistance member, not reliant on psychic powers."""
    return Character(id=3, name="Kei")


@pytest.fixture
def colonel() -> Character:
    """Colonel Shikishima: an authoritarian figure, with admin-level privileges."""
    return Character(id=4, name="Colonel Shikishima", admin=True)


@pytest.fixture
def doctor() -> Character:
    """Dr. Onishi: the researcher whose experiments blur ethical lines."""
    return Character(id=5, name="Dr. Onishi")


# ---------------------------------------------------------------------------
# FIXTURES: RESOURCES
# ---------------------------------------------------------------------------


@pytest.fixture
def kaneda_bike(kaneda: Character) -> Bike:
    """Kaneda's iconic red bike, revered for both style and speed."""
    return Bike(owner=kaneda, model="Red High-Tech Bike", maximum_speed=300)


@pytest.fixture
def tetsuo_bike(tetsuo: Character) -> Bike:
    """Tetsuo's customized ride, rumored to handle more aggressively."""
    return Bike(owner=tetsuo, model="Modified Red Bike", maximum_speed=320)


@pytest.fixture
def olympic_stadium(colonel: Character) -> MilitaryFacility:
    """A high-security stadium rumored to be the resting place of Akira."""
    return MilitaryFacility(
        name="Olympic Stadium - Akira Vault", security_level=10, overseer=colonel
    )


@pytest.fixture
def research_lab(doctor: Character) -> MilitaryFacility:
    """A secret laboratory overseen by the Doctor, brimming with psychic oddities."""
    return MilitaryFacility(
        name="Secret Research Lab", security_level=8, overseer=doctor
    )


@pytest.fixture
def telekinesis(doctor: Character) -> PsychicPower:
    """A classic power discovered by Dr. Onishi, requires decent psychic potential."""
    return PsychicPower(name="Telekinesis", min_required_level=50, discovered_by=doctor)


@pytest.fixture
def neo_tokyo() -> Location:
    """Neo Tokyo: the sprawling metropolis teetering on the brink of catastrophe."""
    return Location(name="Neo Tokyo", population=10_000_000)


@pytest.fixture
def harukiya() -> Location:
    """Harukiya: a bar where scuffles are as common as drinks."""
    return Location(name="Harukiya", population=50)


# ---------------------------------------------------------------------------
# Main fixture which defines the authorization rules
# ---------------------------------------------------------------------------


@pytest.fixture
def akira_authz(
    colonel: Character,
    tetsuo: Character,
    kaneda: Character,
    doctor: Character,
    neo_tokyo: Location,
    harukiya: Location,
) -> Cadurso:
    """
    Defines the rule set for who can do what in Neo Tokyo's chaotic environment.

    This fixture demonstrates, in a practical way, how one could use Cadurso to implement an authorization system
    for a given universe or application domain.
    """

    ########################################################
    # First, create the Cadurso instance, which will hold all the rules
    ########################################################
    akira_universe = Cadurso()

    ########################################################
    # Next, add rules for each permission type
    ########################################################

    # The rules are defined as functions that take the actor and resource as arguments, and return a boolean
    # if they are allowed to perform the action on the resource.

    ########################################################
    # Bikes
    ########################################################
    @akira_universe.add_rule(BikePermission.DRIVE)
    def bike_owner_can_drive_own_bike(actor: Character, resource: Bike) -> bool:
        """The owner of the ride obviously has the right to take it for a spin."""
        return actor == resource.owner

    @akira_universe.add_rule(BikePermission.DRIVE)
    def colonel_can_drive_any_bike(actor: Character, _resource: Bike) -> bool:
        """Colonel Shikishima has the authority to commandeer rides at will."""
        return actor == colonel

    @akira_universe.add_rule(BikePermission.MODIFY)
    def bike_owner_can_modify_own_bike(actor: Character, resource: Bike) -> bool:
        """Only the rightful owner can tinker with the bike's wiring and parts."""
        return actor == resource.owner

    @akira_universe.add_rule(BikePermission.EXPLODE)
    def tetsuo_can_explode_any_bike_if_strong(
        actor: Character, _resource: Bike
    ) -> bool:
        """Tetsuo throws a tantrum fierce enough to trash any bike, if he's strong enough."""
        return actor == tetsuo and actor.psychic_level >= 80

    ########################################################
    # Military Facilities
    ########################################################
    @akira_universe.add_rule(FacilityPermission.ENTER)
    def facility_overseer_can_enter_own_facility(
        actor: Character, facility: MilitaryFacility
    ) -> bool:
        """The military facility overseer has a universal pass to their domain."""
        return actor == facility.overseer

    @akira_universe.add_rule(FacilityPermission.ENTER)
    def colonel_can_enter_any_facility(
        actor: Character, _facility: MilitaryFacility
    ) -> bool:
        """The Colonel's badge opens doors, whether politely or forcibly."""
        return actor == colonel

    @akira_universe.add_rule(FacilityPermission.ENTER)
    def psychic_can_infiltrate_facility_if_strong(
        actor: Character, facility: MilitaryFacility
    ) -> bool:
        """Sufficient psychic prowess can overwhelm most security measures."""
        return actor.psychic_level >= facility.security_level

    @akira_universe.add_rule(FacilityPermission.SHUTDOWN)
    def colonel_can_shutdown_any_facility(
        actor: Character, _facility: MilitaryFacility
    ) -> bool:
        """When the Colonel decides it's over, it's over."""
        return actor == colonel

    @akira_universe.add_rule(FacilityPermission.LAUNCH_STRIKE)
    def colonel_can_launch_strike_any_facility(
        actor: Character, _facility: MilitaryFacility
    ) -> bool:
        """Only the Colonel can unleash a city-wide crackdown or militaristic response."""
        return actor == colonel

    ########################################################
    # Psychic Powers
    ########################################################
    @akira_universe.add_rule(PsychicPermission.USE_POWER)
    def must_meet_min_level_to_use(actor: Character, power: PsychicPower) -> bool:
        """Tapping into psychic abilities recklessly can be fatal if under-prepared."""
        return actor.psychic_level >= power.min_required_level

    @akira_universe.add_rule(PsychicPermission.USE_POWER)
    def discovered_by_always_can_use(actor: Character, power: PsychicPower) -> bool:
        """The one who discovered the power keeps some privileges—often dangerously so."""
        return actor == power.discovered_by

    ########################################################
    # Physical Locations
    ########################################################

    # This rule is async to demonstrate that Cadurso support for async functions
    @akira_universe.add_rule(LocationPermission.DESTROY)
    async def tetsuo_can_destroy_neotokyo_if_melting_down(
        actor: Character, location: Location
    ) -> bool:
        """Tetsuo at full meltdown (psychic_level=100) might topple Neo Tokyo."""
        return actor == tetsuo and actor.psychic_level >= 100 and location == neo_tokyo

    @akira_universe.add_rule(LocationPermission.DESTROY)
    def colonel_refuses_to_destroy_any_location(
        actor: Character, location: Location
    ) -> bool:
        """The Colonel won't personally obliterate major locations on a whim."""
        return actor == colonel and False

    @akira_universe.add_rule(LocationPermission.BRAWL)
    def tetsuo_can_brawl_in_harukiya_if_strong(
        actor: Character, location: Location
    ) -> bool:
        """Tetsuo often picks fights in Harukiya, if he's at least psychic_level=60."""
        return actor == tetsuo and location == harukiya and actor.psychic_level >= 60

    @akira_universe.add_rule(LocationPermission.BRAWL)
    def kaneda_can_brawl_anywhere(actor: Character, _location: Location) -> bool:
        """Kaneda's fists do the talking, no matter the locale."""
        return actor == kaneda

    ########################################################
    # After defining all the rules, call .freeze() to prevent further rule additions
    ########################################################
    akira_universe.freeze()

    # That's it! The authorization system is now ready to be used in your system.

    return akira_universe
