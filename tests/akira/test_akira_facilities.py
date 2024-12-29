from cadurso import Cadurso
from tests.akira.conftest import (
    Character,
    FacilityPermission,
    MilitaryFacility,
)


def test_colonel_can_enter_any_facility(
    akira_authz: Cadurso,
    colonel: Character,
    olympic_stadium: MilitaryFacility,
    research_lab: MilitaryFacility,
) -> None:
    """
    The Colonel's administrative status allows him entry into all facilities.
    """
    assert akira_authz.is_allowed(colonel, FacilityPermission.ENTER, olympic_stadium)
    assert akira_authz.is_allowed(colonel, FacilityPermission.ENTER, research_lab)


def test_facility_overseer_can_enter_own_facility(
    akira_authz: Cadurso, doctor: Character, research_lab: MilitaryFacility
) -> None:
    """
    The overseer of a facility has unrestricted access to their own domain.
    """
    assert akira_authz.is_allowed(doctor, FacilityPermission.ENTER, research_lab)


def test_psychic_can_infiltrate_facility_if_strong(
    akira_authz: Cadurso, tetsuo: Character, olympic_stadium: MilitaryFacility
) -> None:
    """
    Tetsuo can bypass facility security if his psychic_level exceeds the
    facility's security_level.
    """
    assert not akira_authz.is_allowed(tetsuo, FacilityPermission.ENTER, olympic_stadium)

    tetsuo.psychic_level = 15
    assert akira_authz.is_allowed(tetsuo, FacilityPermission.ENTER, olympic_stadium)


def test_colonel_can_shutdown_any_facility(
    akira_authz: Cadurso, colonel: Character, olympic_stadium: MilitaryFacility
) -> None:
    """
    The Colonel has the authority to shut down any facility at will.
    """
    assert akira_authz.is_allowed(colonel, FacilityPermission.SHUTDOWN, olympic_stadium)


def test_tetsuo_cannot_shutdown_facilities(
    akira_authz: Cadurso, tetsuo: Character, olympic_stadium: MilitaryFacility
) -> None:
    """
    Tetsuo, despite his powers, lacks the administrative authority to shut down
    facilities.
    """
    assert not akira_authz.is_allowed(
        tetsuo, FacilityPermission.SHUTDOWN, olympic_stadium
    )
