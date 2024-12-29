from cadurso import Cadurso
from tests.brazil.conftest import (
    BuildingPermission,
    Character,
    GovernmentBuilding,
)


def test_security_roles_arrest_and_enter(
    brazil_authz: Cadurso,
    chief_minister: Character,
    jill_layton: Character,
    information_retrieval_center: GovernmentBuilding,
) -> None:
    """
    Check that only SECURITY can ARREST_SUSPECTS,
    and BUREAUCRAT or MINISTER can ENTER_DEPARTMENT.
    We'll demonstrate that Jill, a CITIZEN, has neither capability.
    For example, the Chief Minister can ENTER, but not ARREST (no SECURITY role).
    """
    # Just for demonstration, we assume the Chief Minister is not SECURITY
    assert brazil_authz.is_allowed(
        chief_minister,
        BuildingPermission.ENTER_DEPARTMENT,
        information_retrieval_center,
    )
    assert not brazil_authz.is_allowed(
        chief_minister, BuildingPermission.ARREST_SUSPECTS, information_retrieval_center
    )

    # Jill is only CITIZEN
    assert not brazil_authz.is_allowed(
        jill_layton, BuildingPermission.ENTER_DEPARTMENT, information_retrieval_center
    )
    assert not brazil_authz.is_allowed(
        jill_layton, BuildingPermission.ARREST_SUSPECTS, information_retrieval_center
    )
