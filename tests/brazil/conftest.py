"""
A Cadurso-based authorization system set in the Brazil (1985) universe.

The system is modelled as an RBAC-like system, where actors (e.g., Sam Lowry, Jill Layton) have roles
(e.g., BUREAUCRAT, CITIZEN). Each role has a set of permissions (e.g., READ_FORM, INSPECT, ENTER_DEPARTMENT), as encoded
in the rules of the Cadurso instance.

The fixtures in this module represent the characters, locations, and permissions in the Brazil universe.
"""

from dataclasses import dataclass, field
from enum import Enum, auto

import pytest

from cadurso import Cadurso


class Role(Enum):
    CITIZEN = auto()
    BUREAUCRAT = auto()
    SECURITY = auto()
    ENGINEER = auto()
    MINISTER = auto()
    REBEL = auto()
    TORTURER = auto()
    DREAMER = auto()


class PaperworkPermission(Enum):
    READ_FORM = auto()
    SUBMIT_FORM = auto()
    ARCHIVE_FORM = auto()


class DuctPermission(Enum):
    INSPECT = auto()
    REPAIR = auto()
    DESTROY = auto()


class BuildingPermission(Enum):
    ENTER_DEPARTMENT = auto()
    ARREST_SUSPECTS = auto()
    APPROVE_BUDGET = auto()


class DreamPermission(Enum):
    """
    Dream-like actions.
    Keep in mind: Characters in Brazil have no psychic powers.
    """

    DAYDREAM = auto()


class TorturePermission(Enum):
    """Reflects interrogation or torture practices."""

    INTERROGATE = auto()


@dataclass
class OfficialForm:
    """An official piece of paperwork in Brazil's bureaucracy."""

    form_number: str
    contents: str

    def __hash__(self) -> int:
        return hash((self.form_number, self.contents))


@dataclass
class DuctSystem:
    """The duct system that plagues the city."""

    location: str
    malfunction_severity: int

    def __hash__(self) -> int:
        return hash((self.location, self.malfunction_severity))


@dataclass
class GovernmentBuilding:
    """A structure belonging to a certain department."""

    name: str
    department: str

    def __hash__(self) -> int:
        return hash((self.name, self.department))


@dataclass
class InterrogationChamber:
    """A specialized room for 'information retrieval'."""

    chamber_id: str
    security_clearance_needed: int

    def __hash__(self) -> int:
        return hash((self.chamber_id, self.security_clearance_needed))


@dataclass
class Character:
    """
    A person in Brazil's bureaucracy who may have multiple roles.
    Also, some characters might be packing official forms in their pockets.

    Also, while a Character is an Actor, it can also be a Resource (e.g., for MindPermission.DAYDREAM).
    """

    name: str
    description: str
    roles: list[Role] = field(default_factory=list)
    pocket_contents: list[OfficialForm] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash((self.name, self.description, self.roles, self.pocket_contents))


@pytest.fixture
def form_27b_6() -> OfficialForm:
    """
    The dreaded 'Form 27B/6' that ENGINEERS must have to be allowed to repair ducts.
    """
    return OfficialForm(form_number="27B/6", contents="Request for Duct Maintenance")


@pytest.fixture
def sample_duct() -> DuctSystem:
    """A typical duct that might require maintenance or sabotage."""
    return DuctSystem(location="Somewhere in the city", malfunction_severity=50)


@pytest.fixture
def torture_room() -> InterrogationChamber:
    """A place where torturers carry out interrogations."""
    return InterrogationChamber(chamber_id="Chamber #13", security_clearance_needed=9)


@pytest.fixture
def central_services_office() -> GovernmentBuilding:
    """Central Services HQ for official duct matters."""
    return GovernmentBuilding(name="Central Services HQ", department="Central Services")


@pytest.fixture
def information_retrieval_center() -> GovernmentBuilding:
    """Information Retrieval Dept, where questionable 'interviews' occur."""
    return GovernmentBuilding(
        name="Information Retrieval Dept", department="Info Retrieval"
    )


# ------------------ Character Fixtures ------------------
@pytest.fixture
def sam_lowry() -> Character:
    return Character(
        name="Sam Lowry",
        description="A low-level bureaucrat with dreams of heroism",
        roles=[Role.BUREAUCRAT, Role.DREAMER],
    )


@pytest.fixture
def jill_layton() -> Character:
    return Character(
        name="Jill Layton",
        description="A truck driver who gets caught up in the bureaucracy",
        roles=[Role.CITIZEN],
    )


@pytest.fixture
def harry_tuttle() -> Character:
    return Character(
        name="Harry Tuttle",
        description="A rogue who enjoys repairing the odd duct",
        roles=[Role.REBEL],
    )


@pytest.fixture
def mr_kurtzmann() -> Character:
    return Character(
        name="Mr. Kurtzmann",
        description="A lazy bureaucrat who pretends to work and care about forms",
        roles=[Role.BUREAUCRAT],
    )


@pytest.fixture
def chief_minister() -> Character:
    return Character(
        name="Chief Minister",
        description="The head of the Ministry of Information",
        roles=[Role.BUREAUCRAT, Role.MINISTER],
    )


@pytest.fixture
def jack_lint() -> Character:
    return Character(
        name="Jack Lint",
        description="A high-ranking bureaucrat with a dark side",
        roles=[Role.BUREAUCRAT, Role.TORTURER],
    )


@pytest.fixture
def spoor() -> Character:
    return Character(
        name="Spoor",
        description="A duct-repair engineer with a short temper",
        roles=[Role.ENGINEER],
        pocket_contents=[],
    )


@pytest.fixture
def dowser() -> Character:
    return Character(
        name="Dowser",
        description="Another duct-repair engineer, but with a more laid-back attitude. Tags along with Spoor",
        roles=[Role.ENGINEER],
        pocket_contents=[],
    )


@pytest.fixture
def brazil_authz(form_27b_6: OfficialForm) -> Cadurso:
    """
    A Cadurso router enforcing that ENGINEERS must have the exact `form_27b_6`
    instance in their pocket to perform duct REPAIR. REBELS are exempt.
    """
    brazil_universe = Cadurso()

    # PAPERWORK RULES
    @brazil_universe.add_rule(PaperworkPermission.READ_FORM)
    def bureaucrat_or_minister_reads(actor: Character, _form: OfficialForm) -> bool:
        """Only a BUREAUCRAT or MINISTER may read official forms."""
        return (Role.BUREAUCRAT in actor.roles) or (Role.MINISTER in actor.roles)

    @brazil_universe.add_rule(PaperworkPermission.SUBMIT_FORM)
    def citizen_submits_form(actor: Character, _form: OfficialForm) -> bool:
        """A CITIZEN may submit forms."""
        return Role.CITIZEN in actor.roles

    @brazil_universe.add_rule(PaperworkPermission.SUBMIT_FORM)
    def bureaucrat_submits_form(actor: Character, _form: OfficialForm) -> bool:
        """A BUREAUCRAT or MINISTER can also handle form submissions."""
        return (Role.BUREAUCRAT in actor.roles) or (Role.MINISTER in actor.roles)

    @brazil_universe.add_rule(PaperworkPermission.ARCHIVE_FORM)
    def only_minister_archives(actor: Character, _form: OfficialForm) -> bool:
        """Only a MINISTER can archive forms."""
        return Role.MINISTER in actor.roles

    # DUCT RULES
    @brazil_universe.add_rule(DuctPermission.INSPECT)
    def engineer_inspects_duct(actor: Character, _duct: DuctSystem) -> bool:
        """ENGINEERs are allowed to INSPECT duct systems."""
        return Role.ENGINEER in actor.roles

    @brazil_universe.add_rule(DuctPermission.INSPECT)
    def rebel_inspects_duct(actor: Character, _duct: DuctSystem) -> bool:
        """REBELS may also INSPECT duct systems off the record."""
        return Role.REBEL in actor.roles

    @brazil_universe.add_rule(DuctPermission.INSPECT)
    def bureaucrat_inspects_duct(actor: Character, _duct: DuctSystem) -> bool:
        """BUREAUCRATs want to keep an eye on everything, so they can INSPECT ducts as well."""
        return Role.BUREAUCRAT in actor.roles

    @brazil_universe.add_rule(DuctPermission.REPAIR)
    def engineer_with_form_27b6(actor: Character, _duct: DuctSystem) -> bool:
        """
        ENGINEERs may REPAIR a duct, but only if they are carrying the form 27B/6
        in their pocket.
        """
        if Role.ENGINEER not in actor.roles:
            return False

        # I can't allow repairs if you don't present me with the proper paperwork --Sam Lowry
        return form_27b_6 in actor.pocket_contents

    @brazil_universe.add_rule(DuctPermission.REPAIR)
    def rebel_repairs_duct(actor: Character, _duct: DuctSystem) -> bool:
        """REBELS, like Tuttle, can fix any duct they want."""
        return Role.REBEL in actor.roles

    @brazil_universe.add_rule(DuctPermission.DESTROY)
    def rebel_destroys_duct(actor: Character, _duct: DuctSystem) -> bool:
        """A REBEL may sabotage any duct they wish."""
        return Role.REBEL in actor.roles

    # BUILDING RULES
    @brazil_universe.add_rule(BuildingPermission.ENTER_DEPARTMENT)
    def bureaucrat_enters_dept(actor: Character, _bld: GovernmentBuilding) -> bool:
        """A BUREAUCRAT or MINISTER can ENTER a government department."""
        return (Role.BUREAUCRAT in actor.roles) or (Role.MINISTER in actor.roles)

    @brazil_universe.add_rule(BuildingPermission.ENTER_DEPARTMENT)
    def security_enters_dept(actor: Character, _bld: GovernmentBuilding) -> bool:
        """SECURITY forces can also ENTER a department."""
        return Role.SECURITY in actor.roles

    @brazil_universe.add_rule(BuildingPermission.ARREST_SUSPECTS)
    def only_security_arrests(actor: Character, _bld: GovernmentBuilding) -> bool:
        """Only SECURITY is entrusted with ARREST_SUSPECTS."""
        return Role.SECURITY in actor.roles

    @brazil_universe.add_rule(BuildingPermission.APPROVE_BUDGET)
    def only_minister_approves(actor: Character, _bld: GovernmentBuilding) -> bool:
        """Only a MINISTER can APPROVE_BUDGET in a building."""
        return Role.MINISTER in actor.roles

    # MIND RULES
    @brazil_universe.add_rule(DreamPermission.DAYDREAM)
    def dreamer_can_daydream(actor: Character, other_actor: Character) -> bool:
        """
        A DREAMER can daydream, but only in their own mind (actor == resource).
        It wouldn't make sense to operate on someone else's mind in Brazil, as no one has psychic powers.
        """
        return (actor == other_actor) and (Role.DREAMER in actor.roles)

    # TORTURE RULES
    @brazil_universe.add_rule(TorturePermission.INTERROGATE)
    def torturer_can_interrogate(
        actor: Character, _chamber: InterrogationChamber
    ) -> bool:
        """Only those with the TORTURER role can do INTERROGATE actions."""
        return Role.TORTURER in actor.roles

    # Freeze the Cadurso instance to prevent further rule additions
    brazil_universe.freeze()

    return brazil_universe
