from cadurso import Cadurso
from tests.brazil.conftest import (
    BuildingPermission,
    Character,
    GovernmentBuilding,
    OfficialForm,
    PaperworkPermission,
)


def test_bureaucrat_can_read_submit(
    brazil_authz: Cadurso, sam_lowry: Character, form_27b_6: OfficialForm
) -> None:
    """
    Sam Lowry has BUREAUCRAT role, so he can READ_FORM and SUBMIT_FORM.
    He cannot ARCHIVE_FORM because that requires being a MINISTER.
    """
    assert brazil_authz.is_allowed(sam_lowry, PaperworkPermission.READ_FORM, form_27b_6)
    assert brazil_authz.is_allowed(
        sam_lowry, PaperworkPermission.SUBMIT_FORM, form_27b_6
    )
    assert not brazil_authz.is_allowed(
        sam_lowry, PaperworkPermission.ARCHIVE_FORM, form_27b_6
    )


def test_minister_can_archive_and_approve(
    brazil_authz: Cadurso,
    chief_minister: Character,
    form_27b_6: OfficialForm,
    central_services_office: GovernmentBuilding,
) -> None:
    """
    The Chief Minister (MINISTER) can ARCHIVE_FORM
    and also APPROVE_BUDGET in a building.
    """
    assert brazil_authz.is_allowed(
        chief_minister, PaperworkPermission.ARCHIVE_FORM, form_27b_6
    )
    assert brazil_authz.is_allowed(
        chief_minister, BuildingPermission.APPROVE_BUDGET, central_services_office
    )


def test_citizen_can_submit_form_not_read(
    brazil_authz: Cadurso, jill_layton: Character, form_27b_6: OfficialForm
) -> None:
    """
    Jill Layton (CITIZEN) can SUBMIT_FORM but cannot READ_FORM or ARCHIVE_FORM,
    because that requires BUREAUCRAT or MINISTER.
    """
    assert brazil_authz.is_allowed(
        jill_layton, PaperworkPermission.SUBMIT_FORM, form_27b_6
    )
    assert not brazil_authz.is_allowed(
        jill_layton, PaperworkPermission.READ_FORM, form_27b_6
    )
    assert not brazil_authz.is_allowed(
        jill_layton, PaperworkPermission.ARCHIVE_FORM, form_27b_6
    )
