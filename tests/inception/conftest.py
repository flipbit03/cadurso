"""
A Cadurso-based authorization system set in the Inception (2010) universe, for testing.

This test universe exercises the Veto mechanism and AuthorizationDecision class.

Actors are dreamers who navigate layered dream worlds. Resources are dream levels and totems.
The Veto mechanism models "kicks" — forceful ejections that override any permission a dreamer
might otherwise have within a dream level.
"""

from dataclasses import dataclass, field
from enum import Enum, auto

import pytest

from cadurso import AuthorizationDecision, Cadurso, Veto

# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------


class Role(Enum):
    EXTRACTOR = auto()
    """Specialists who steal secrets from within dreams."""

    POINT_MAN = auto()
    """Manages logistics and coordinates kicks across dream levels."""

    ARCHITECT = auto()
    """Designs the dream world's layout and mazes."""

    FORGER = auto()
    """Masters of disguise — can impersonate anyone within a dream."""

    MARK = auto()
    """The target of extraction or inception."""

    PROJECTION = auto()
    """A subconscious manifestation, not a real dreamer."""


# ---------------------------------------------------------------------------
# Actors
# ---------------------------------------------------------------------------


@dataclass
class Dreamer:
    """
    A person who enters shared dreams, each with specific skills and states.

    :param id: A unique identifier for the dreamer.
    :param name: The dreamer's name.
    :param role: Their specialty in the dream heist.
    :param sedated: Whether they are under heavy sedation (prevents being kicked).
    :param kicked: Whether they've been "kicked" out of the dream.
    """

    id: int
    name: str
    role: Role
    sedated: bool = False
    kicked: bool = False

    def __hash__(self) -> int:
        return hash(self.id)


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@dataclass
class DreamLevel:
    """
    A layer of the shared dream, each deeper than the last.

    :param name: A descriptive name for this dream level.
    :param depth: How many layers deep (1 = shallowest).
    :param architect: The dreamer who designed this level.
    :param collapsed: Whether the level has become unstable.
    """

    name: str
    depth: int
    architect: Dreamer
    collapsed: bool = False

    def __hash__(self) -> int:
        return hash((self.name, self.depth))


@dataclass
class Totem:
    """
    A small personal object used to distinguish dreams from reality.

    :param name: What the totem is (e.g., spinning top, loaded die).
    :param owner: The dreamer who owns this totem.
    """

    name: str
    owner: Dreamer

    def __hash__(self) -> int:
        return hash((self.name, self.owner))


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------


class DreamPermission(Enum):
    NAVIGATE = auto()
    """Move through a dream level."""

    ARCHITECT = auto()
    """Reshape the dream level's structure."""

    PLANT_IDEA = auto()
    """Perform inception — plant an idea in the dreamer's subconscious."""

    KICK = auto()
    """Trigger a kick to eject dreamers from the level."""


class TotemPermission(Enum):
    INSPECT = auto()
    """Examine a totem to check if you're in a dream."""


# ---------------------------------------------------------------------------
# Fixtures: Actors
# ---------------------------------------------------------------------------


@pytest.fixture
def cobb() -> Dreamer:
    """Dom Cobb — the extractor, leader of the inception team."""
    return Dreamer(id=1, name="Cobb", role=Role.EXTRACTOR)


@pytest.fixture
def arthur() -> Dreamer:
    """Arthur — the point man, meticulous and reliable."""
    return Dreamer(id=2, name="Arthur", role=Role.POINT_MAN)


@pytest.fixture
def ariadne() -> Dreamer:
    """Ariadne — the architect, designer of dream mazes."""
    return Dreamer(id=3, name="Ariadne", role=Role.ARCHITECT)


@pytest.fixture
def eames() -> Dreamer:
    """Eames — the forger, master of disguise within dreams."""
    return Dreamer(id=4, name="Eames", role=Role.FORGER)


@pytest.fixture
def fischer() -> Dreamer:
    """Robert Fischer — the mark, target of the inception."""
    return Dreamer(id=5, name="Fischer", role=Role.MARK)


@pytest.fixture
def mal() -> Dreamer:
    """Mal — Cobb's deceased wife, a hostile projection that haunts dream levels."""
    return Dreamer(id=6, name="Mal", role=Role.PROJECTION, kicked=True)


# ---------------------------------------------------------------------------
# Fixtures: Resources
# ---------------------------------------------------------------------------


@pytest.fixture
def city_level(arthur: Dreamer) -> DreamLevel:
    """Level 1 — the rainy city streets, designed by Arthur."""
    return DreamLevel(name="City Streets", depth=1, architect=arthur)


@pytest.fixture
def hotel_level(arthur: Dreamer) -> DreamLevel:
    """Level 2 — the hotel with shifting gravity, designed by Arthur."""
    return DreamLevel(name="Hotel", depth=2, architect=arthur)


@pytest.fixture
def snow_fortress(ariadne: Dreamer) -> DreamLevel:
    """Level 3 — the snow fortress, designed by Ariadne."""
    return DreamLevel(name="Snow Fortress", depth=3, architect=ariadne)


@pytest.fixture
def limbo(cobb: Dreamer) -> DreamLevel:
    """Limbo — the deepest unconstructed dream space. Collapsed and dangerous."""
    return DreamLevel(name="Limbo", depth=4, architect=cobb, collapsed=True)


@pytest.fixture
def cobbs_totem(cobb: Dreamer) -> Totem:
    """Cobb's spinning top — the most iconic totem."""
    return Totem(name="spinning top", owner=cobb)


@pytest.fixture
def arthurs_totem(arthur: Dreamer) -> Totem:
    """Arthur's loaded die."""
    return Totem(name="loaded die", owner=arthur)


# ---------------------------------------------------------------------------
# Cadurso instance with rules
# ---------------------------------------------------------------------------


@pytest.fixture
def inception_universe(
    cobb: Dreamer,
    arthur: Dreamer,
    ariadne: Dreamer,
    eames: Dreamer,
    fischer: Dreamer,
    mal: Dreamer,
) -> Cadurso:
    """Build and freeze the Inception authorization universe."""
    inception = Cadurso()

    ########################################################
    # Dream Navigation
    ########################################################

    @inception.add_rule(DreamPermission.NAVIGATE)
    def team_can_navigate(actor: Dreamer, _level: DreamLevel) -> bool:
        """Any team member (non-mark, non-projection) can navigate dream levels."""
        return actor.role not in (Role.MARK, Role.PROJECTION)

    @inception.add_rule(DreamPermission.NAVIGATE)
    def fischer_navigates_shallow_levels(actor: Dreamer, level: DreamLevel) -> bool:
        """Fischer (the mark) can navigate the first two levels — he's been brought along."""
        return actor == fischer and level.depth <= 2

    @inception.add_rule(DreamPermission.NAVIGATE)
    def collapsed_levels_reject_everyone(actor: Dreamer, level: DreamLevel) -> bool:
        """A collapsed dream level forcefully ejects anyone trying to navigate it."""
        if level.collapsed:
            raise Veto("dream level has collapsed")
        return False

    ########################################################
    # Architecting
    ########################################################

    @inception.add_rule(DreamPermission.ARCHITECT)
    def architect_can_reshape_own_level(actor: Dreamer, level: DreamLevel) -> bool:
        """Only the architect of a level can reshape it."""
        return actor == level.architect

    @inception.add_rule(DreamPermission.ARCHITECT)
    def collapsed_level_cannot_be_reshaped(actor: Dreamer, level: DreamLevel) -> bool:
        """A collapsed level resists all manipulation."""
        if level.collapsed:
            raise Veto("dream level has collapsed — cannot reshape")
        return False

    ########################################################
    # Inception (planting ideas)
    ########################################################

    @inception.add_rule(DreamPermission.PLANT_IDEA)
    def extractor_can_plant_idea(actor: Dreamer, _level: DreamLevel) -> bool:
        """Only an extractor has the skill to plant an idea."""
        return actor.role == Role.EXTRACTOR

    @inception.add_rule(DreamPermission.PLANT_IDEA)
    def must_be_deep_enough_to_plant(actor: Dreamer, level: DreamLevel) -> bool:
        """Inception requires at least depth 3 — the idea must be planted deep."""
        if level.depth < 3:
            raise Veto("dream is not deep enough for inception")
        return False

    ########################################################
    # Kicks
    ########################################################

    @inception.add_rule(DreamPermission.KICK)
    def point_man_can_kick(actor: Dreamer, _level: DreamLevel) -> bool:
        """The point man coordinates kicks across dream levels."""
        return actor.role == Role.POINT_MAN

    @inception.add_rule(DreamPermission.KICK)
    def anyone_can_kick_in_shallow(actor: Dreamer, level: DreamLevel) -> bool:
        """In the shallowest level, anyone on the team can trigger a kick."""
        return level.depth == 1 and actor.role not in (Role.MARK, Role.PROJECTION)

    ########################################################
    # Totems
    ########################################################

    @inception.add_rule(TotemPermission.INSPECT)
    def owner_can_inspect_own_totem(actor: Dreamer, totem: Totem) -> bool:
        """Only the owner should ever touch their totem — that's the whole point."""
        return actor == totem.owner

    @inception.add_rule(TotemPermission.INSPECT)
    def no_one_touches_another_persons_totem(actor: Dreamer, totem: Totem) -> bool:
        """Touching someone else's totem defeats its purpose — hard denied."""
        if actor != totem.owner:
            raise Veto("never let someone else touch your totem")
        return False

    ########################################################
    # Freeze
    ########################################################
    inception.freeze()

    return inception
