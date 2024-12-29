from cadurso import Cadurso
from tests.akira.conftest import (
    Character,
    PsychicPermission,
    PsychicPower,
)


def test_tetsuo_use_power_when_psychic_level_sufficient(
    akira_authz: Cadurso, tetsuo: Character, telekinesis: PsychicPower
) -> None:
    """
    Tetsuo can only use powers like Telekinesis if his psychic_level
    meets the minimum requirement.
    """
    assert not akira_authz.is_allowed(tetsuo, PsychicPermission.USE_POWER, telekinesis)

    tetsuo.psychic_level = 50
    assert akira_authz.is_allowed(tetsuo, PsychicPermission.USE_POWER, telekinesis)


def test_doctor_can_use_power_discovered_by_him(
    akira_authz: Cadurso, doctor: Character, telekinesis: PsychicPower
) -> None:
    """
    Dr. Onishi, as the discoverer of Telekinesis, has special privileges
    to use it regardless of psychic_level.
    """
    assert akira_authz.is_allowed(doctor, PsychicPermission.USE_POWER, telekinesis)


def test_kaneda_cannot_use_psychic_powers(
    akira_authz: Cadurso, kaneda: Character, telekinesis: PsychicPower
) -> None:
    """
    Kaneda lacks psychic abilities and should never be able to use
    powers like Telekinesis.
    """
    assert not akira_authz.is_allowed(kaneda, PsychicPermission.USE_POWER, telekinesis)


def test_tetsuo_cannot_use_undiscovered_power_if_weak(
    akira_authz: Cadurso, tetsuo: Character
) -> None:
    """
    Tetsuo should not be able to use a power that hasn't been discovered yet, if he
    lacks the psychic_level to use it.

    Over time, he may grow strong enough to use it, but that's a different story.
    """
    new_power = PsychicPower(
        name="Chronokinesis", min_required_level=70, discovered_by=None
    )
    assert not akira_authz.is_allowed(tetsuo, PsychicPermission.USE_POWER, new_power)

    tetsuo.psychic_level = 70
    assert akira_authz.is_allowed(tetsuo, PsychicPermission.USE_POWER, new_power)
