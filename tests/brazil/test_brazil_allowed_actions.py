"""
Tests for the get_allowed_actions() API in the Brazil universe.

These tests verify that the allowed actions API correctly returns all actions
an actor can perform on a resource, using the RBAC-style Brazil authorization system.
"""

from cadurso import Cadurso

from .conftest import (
    BuildingPermission,
    Character,
    DreamPermission,
    DuctPermission,
    DuctSystem,
    GovernmentBuilding,
    InterrogationChamber,
    OfficialForm,
    PaperworkPermission,
    TorturePermission,
)


def test_bureaucrat_form_permissions(
    brazil_authz: Cadurso, sam_lowry: Character, form_27b_6: OfficialForm
) -> None:
    """Bureaucrats can READ and SUBMIT forms, but not ARCHIVE them."""
    allowed = brazil_authz.get_allowed_actions(sam_lowry, form_27b_6)

    assert PaperworkPermission.READ_FORM in allowed
    assert PaperworkPermission.SUBMIT_FORM in allowed
    assert PaperworkPermission.ARCHIVE_FORM not in allowed


def test_minister_full_form_permissions(
    brazil_authz: Cadurso, chief_minister: Character, form_27b_6: OfficialForm
) -> None:
    """Ministers can perform all paperwork actions."""
    allowed = brazil_authz.get_allowed_actions(chief_minister, form_27b_6)

    assert PaperworkPermission.READ_FORM in allowed
    assert PaperworkPermission.SUBMIT_FORM in allowed
    assert PaperworkPermission.ARCHIVE_FORM in allowed


def test_citizen_limited_form_permissions(
    brazil_authz: Cadurso, jill_layton: Character, form_27b_6: OfficialForm
) -> None:
    """Citizens can only SUBMIT forms."""
    allowed = brazil_authz.get_allowed_actions(jill_layton, form_27b_6)

    assert PaperworkPermission.READ_FORM not in allowed
    assert PaperworkPermission.SUBMIT_FORM in allowed
    assert PaperworkPermission.ARCHIVE_FORM not in allowed


def test_engineer_duct_permissions_without_form(
    brazil_authz: Cadurso, spoor: Character, sample_duct: DuctSystem
) -> None:
    """Engineers can INSPECT ducts but cannot REPAIR without Form 27B/6."""
    allowed = brazil_authz.get_allowed_actions(spoor, sample_duct)

    assert DuctPermission.INSPECT in allowed
    assert DuctPermission.REPAIR not in allowed
    assert DuctPermission.DESTROY not in allowed


def test_engineer_duct_permissions_with_form(
    brazil_authz: Cadurso,
    spoor: Character,
    sample_duct: DuctSystem,
    form_27b_6: OfficialForm,
) -> None:
    """Engineers can REPAIR ducts when they have Form 27B/6."""
    # Add the form to the engineer's pocket
    spoor.pocket_contents.append(form_27b_6)

    allowed = brazil_authz.get_allowed_actions(spoor, sample_duct)

    assert DuctPermission.INSPECT in allowed
    assert DuctPermission.REPAIR in allowed
    assert DuctPermission.DESTROY not in allowed


def test_rebel_full_duct_permissions(
    brazil_authz: Cadurso, harry_tuttle: Character, sample_duct: DuctSystem
) -> None:
    """Rebels have full access to duct operations (no paperwork needed)."""
    allowed = brazil_authz.get_allowed_actions(harry_tuttle, sample_duct)

    assert DuctPermission.INSPECT in allowed
    assert DuctPermission.REPAIR in allowed
    assert DuctPermission.DESTROY in allowed


def test_bureaucrat_duct_permissions(
    brazil_authz: Cadurso, mr_kurtzmann: Character, sample_duct: DuctSystem
) -> None:
    """Bureaucrats can INSPECT ducts (keeping an eye on things)."""
    allowed = brazil_authz.get_allowed_actions(mr_kurtzmann, sample_duct)

    assert DuctPermission.INSPECT in allowed
    assert DuctPermission.REPAIR not in allowed
    assert DuctPermission.DESTROY not in allowed


def test_bureaucrat_building_permissions(
    brazil_authz: Cadurso,
    sam_lowry: Character,
    central_services_office: GovernmentBuilding,
) -> None:
    """Bureaucrats can ENTER departments but cannot ARREST or APPROVE_BUDGET."""
    allowed = brazil_authz.get_allowed_actions(sam_lowry, central_services_office)

    assert BuildingPermission.ENTER_DEPARTMENT in allowed
    assert BuildingPermission.ARREST_SUSPECTS not in allowed
    assert BuildingPermission.APPROVE_BUDGET not in allowed


def test_minister_building_permissions(
    brazil_authz: Cadurso,
    chief_minister: Character,
    central_services_office: GovernmentBuilding,
) -> None:
    """Ministers can ENTER and APPROVE_BUDGET but cannot ARREST."""
    allowed = brazil_authz.get_allowed_actions(chief_minister, central_services_office)

    assert BuildingPermission.ENTER_DEPARTMENT in allowed
    assert BuildingPermission.ARREST_SUSPECTS not in allowed
    assert BuildingPermission.APPROVE_BUDGET in allowed


def test_dreamer_can_only_daydream_in_own_mind(
    brazil_authz: Cadurso,
    sam_lowry: Character,
    jill_layton: Character,
) -> None:
    """Dreamers can only DAYDREAM in their own mind (actor == resource)."""
    # Sam daydreaming in his own mind
    allowed_self = brazil_authz.get_allowed_actions(sam_lowry, sam_lowry)
    assert DreamPermission.DAYDREAM in allowed_self

    # Sam cannot daydream in Jill's mind
    allowed_other = brazil_authz.get_allowed_actions(sam_lowry, jill_layton)
    assert allowed_other == set()


def test_non_dreamer_cannot_daydream(
    brazil_authz: Cadurso, jill_layton: Character
) -> None:
    """Non-dreamers cannot DAYDREAM even in their own mind."""
    allowed = brazil_authz.get_allowed_actions(jill_layton, jill_layton)

    assert DreamPermission.DAYDREAM not in allowed


def test_torturer_interrogation_permissions(
    brazil_authz: Cadurso, jack_lint: Character, torture_room: InterrogationChamber
) -> None:
    """Torturers can INTERROGATE in chambers."""
    allowed = brazil_authz.get_allowed_actions(jack_lint, torture_room)

    assert TorturePermission.INTERROGATE in allowed


def test_non_torturer_cannot_interrogate(
    brazil_authz: Cadurso, sam_lowry: Character, torture_room: InterrogationChamber
) -> None:
    """Non-torturers cannot INTERROGATE."""
    allowed = brazil_authz.get_allowed_actions(sam_lowry, torture_room)

    assert TorturePermission.INTERROGATE not in allowed


def test_citizen_no_building_permissions(
    brazil_authz: Cadurso,
    jill_layton: Character,
    central_services_office: GovernmentBuilding,
) -> None:
    """Citizens have no permissions on government buildings."""
    allowed = brazil_authz.get_allowed_actions(jill_layton, central_services_office)

    assert allowed == set()


def test_fluent_api_consistency(
    brazil_authz: Cadurso, harry_tuttle: Character, sample_duct: DuctSystem
) -> None:
    """The fluent API returns the same result as the direct method."""
    direct_result = brazil_authz.get_allowed_actions(harry_tuttle, sample_duct)
    fluent_result = brazil_authz.can(harry_tuttle).allowed_actions_on(sample_duct)

    assert direct_result == fluent_result


def test_multiple_roles_accumulate_permissions(
    brazil_authz: Cadurso,
    jack_lint: Character,
    form_27b_6: OfficialForm,
    torture_room: InterrogationChamber,
    central_services_office: GovernmentBuilding,
) -> None:
    """Jack Lint (BUREAUCRAT + TORTURER) accumulates permissions from both roles."""
    # Form permissions from BUREAUCRAT role
    form_allowed = brazil_authz.get_allowed_actions(jack_lint, form_27b_6)
    assert PaperworkPermission.READ_FORM in form_allowed
    assert PaperworkPermission.SUBMIT_FORM in form_allowed

    # Interrogation permissions from TORTURER role
    chamber_allowed = brazil_authz.get_allowed_actions(jack_lint, torture_room)
    assert TorturePermission.INTERROGATE in chamber_allowed

    # Building permissions from BUREAUCRAT role
    building_allowed = brazil_authz.get_allowed_actions(
        jack_lint, central_services_office
    )
    assert BuildingPermission.ENTER_DEPARTMENT in building_allowed
