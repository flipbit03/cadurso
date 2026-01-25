"""
Tests for the get_allowed_actions() API in the Brazil universe.

These tests verify that the allowed actions API correctly returns all actions
an actor can perform on a resource, using the RBAC-style Brazil authorization system.
"""

import pytest

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

    # NOT allowed: PaperworkPermission.ARCHIVE_FORM
    assert allowed == {PaperworkPermission.READ_FORM, PaperworkPermission.SUBMIT_FORM}


def test_minister_full_form_permissions(
    brazil_authz: Cadurso, chief_minister: Character, form_27b_6: OfficialForm
) -> None:
    """
    Ministers can perform all paperwork actions.

    Edge case: Verifies that get_allowed_actions() finds ALL matching actions,
    not just the first one. The method must iterate through all rule storage keys
    and collect every action that passes evaluation.
    """
    allowed = brazil_authz.get_allowed_actions(chief_minister, form_27b_6)

    assert allowed == {
        PaperworkPermission.READ_FORM,
        PaperworkPermission.SUBMIT_FORM,
        PaperworkPermission.ARCHIVE_FORM,
    }


def test_citizen_limited_form_permissions(
    brazil_authz: Cadurso, jill_layton: Character, form_27b_6: OfficialForm
) -> None:
    """Citizens can only SUBMIT forms."""
    allowed = brazil_authz.get_allowed_actions(jill_layton, form_27b_6)

    # NOT allowed: PaperworkPermission.READ_FORM, PaperworkPermission.ARCHIVE_FORM
    assert allowed == {PaperworkPermission.SUBMIT_FORM}


def test_engineer_duct_permissions_without_form(
    brazil_authz: Cadurso, spoor: Character, sample_duct: DuctSystem
) -> None:
    """Engineers can INSPECT ducts but cannot REPAIR without Form 27B/6."""
    allowed = brazil_authz.get_allowed_actions(spoor, sample_duct)

    # NOT allowed: DuctPermission.REPAIR, DuctPermission.DESTROY
    assert allowed == {DuctPermission.INSPECT}


def test_engineer_duct_permissions_with_form(
    brazil_authz: Cadurso,
    spoor: Character,
    sample_duct: DuctSystem,
    form_27b_6: OfficialForm,
) -> None:
    """
    Engineers can REPAIR ducts when they have Form 27B/6.

    Edge case: Tests dynamic attribute-based access control in an RBAC context.
    The rule checks actor.pocket_contents for the required form. Permissions
    change based on mutable actor state (having the form or not).
    """
    spoor.pocket_contents.append(form_27b_6)

    allowed = brazil_authz.get_allowed_actions(spoor, sample_duct)

    # NOT allowed: DuctPermission.DESTROY
    assert allowed == {DuctPermission.INSPECT, DuctPermission.REPAIR}


def test_rebel_full_duct_permissions(
    brazil_authz: Cadurso, harry_tuttle: Character, sample_duct: DuctSystem
) -> None:
    """
    Rebels have full access to duct operations (no paperwork needed).

    Edge case: Verifies that get_allowed_actions() finds ALL matching actions.
    Harry Tuttle gets all three duct permissions through his REBEL role.
    """
    allowed = brazil_authz.get_allowed_actions(harry_tuttle, sample_duct)

    assert allowed == {
        DuctPermission.INSPECT,
        DuctPermission.REPAIR,
        DuctPermission.DESTROY,
    }


def test_bureaucrat_duct_permissions(
    brazil_authz: Cadurso, mr_kurtzmann: Character, sample_duct: DuctSystem
) -> None:
    """Bureaucrats can INSPECT ducts (keeping an eye on things)."""
    allowed = brazil_authz.get_allowed_actions(mr_kurtzmann, sample_duct)

    # NOT allowed: DuctPermission.REPAIR, DuctPermission.DESTROY
    assert allowed == {DuctPermission.INSPECT}


def test_bureaucrat_building_permissions(
    brazil_authz: Cadurso,
    sam_lowry: Character,
    central_services_office: GovernmentBuilding,
) -> None:
    """Bureaucrats can ENTER departments but cannot ARREST or APPROVE_BUDGET."""
    allowed = brazil_authz.get_allowed_actions(sam_lowry, central_services_office)

    # NOT allowed: BuildingPermission.ARREST_SUSPECTS, BuildingPermission.APPROVE_BUDGET
    assert allowed == {BuildingPermission.ENTER_DEPARTMENT}


def test_minister_building_permissions(
    brazil_authz: Cadurso,
    chief_minister: Character,
    central_services_office: GovernmentBuilding,
) -> None:
    """Ministers can ENTER and APPROVE_BUDGET but cannot ARREST."""
    allowed = brazil_authz.get_allowed_actions(chief_minister, central_services_office)

    # NOT allowed: BuildingPermission.ARREST_SUSPECTS
    assert allowed == {
        BuildingPermission.ENTER_DEPARTMENT,
        BuildingPermission.APPROVE_BUDGET,
    }


def test_dreamer_can_only_daydream_in_own_mind(
    brazil_authz: Cadurso,
    sam_lowry: Character,
    jill_layton: Character,
) -> None:
    """
    Dreamers can only DAYDREAM in their own mind (actor == resource).

    Edge case: The same object serves as both actor and resource. Tests that
    type matching and rule evaluation work correctly when actor is resource.
    The rule explicitly checks actor == other_actor.
    """
    # Sam daydreaming in his own mind
    allowed_self = brazil_authz.get_allowed_actions(sam_lowry, sam_lowry)
    assert allowed_self == {DreamPermission.DAYDREAM}

    # Sam cannot daydream in Jill's mind
    allowed_other = brazil_authz.get_allowed_actions(sam_lowry, jill_layton)
    assert allowed_other == set()


def test_non_dreamer_cannot_daydream(
    brazil_authz: Cadurso, jill_layton: Character
) -> None:
    """
    Non-dreamers cannot DAYDREAM even in their own mind.

    Edge case: Verifies that get_allowed_actions() correctly returns an empty set
    when no rules match, rather than erroring or returning unexpected values.
    """
    allowed = brazil_authz.get_allowed_actions(jill_layton, jill_layton)

    assert allowed == set()


def test_torturer_interrogation_permissions(
    brazil_authz: Cadurso, jack_lint: Character, torture_room: InterrogationChamber
) -> None:
    """Torturers can INTERROGATE in chambers."""
    allowed = brazil_authz.get_allowed_actions(jack_lint, torture_room)

    assert allowed == {TorturePermission.INTERROGATE}


def test_non_torturer_cannot_interrogate(
    brazil_authz: Cadurso, sam_lowry: Character, torture_room: InterrogationChamber
) -> None:
    """
    Non-torturers cannot INTERROGATE.

    Edge case: Verifies empty set is returned when actor lacks required role.
    """
    allowed = brazil_authz.get_allowed_actions(sam_lowry, torture_room)

    assert allowed == set()


def test_citizen_no_building_permissions(
    brazil_authz: Cadurso,
    jill_layton: Character,
    central_services_office: GovernmentBuilding,
) -> None:
    """
    Citizens have no permissions on government buildings.

    Edge case: Verifies that get_allowed_actions() correctly returns an empty set
    when no rules match for the given actor type and resource type combination.
    """
    allowed = brazil_authz.get_allowed_actions(jill_layton, central_services_office)

    assert allowed == set()


def test_fluent_api_consistency(
    brazil_authz: Cadurso, harry_tuttle: Character, sample_duct: DuctSystem
) -> None:
    """
    The fluent API returns the same result as the direct method.

    Edge case: Ensures can(actor).allowed_actions_on(resource) is functionally
    equivalent to get_allowed_actions(actor, resource). Both code paths must
    produce identical results.
    """
    direct_result = brazil_authz.get_allowed_actions(harry_tuttle, sample_duct)
    fluent_result = brazil_authz.can(harry_tuttle).allowed_actions_on(sample_duct)

    assert direct_result == fluent_result


@pytest.mark.asyncio
async def test_fluent_api_async_consistency(
    brazil_authz: Cadurso, harry_tuttle: Character, sample_duct: DuctSystem
) -> None:
    """
    The async fluent API returns the same result as the direct async method.

    Edge case: Ensures can(actor).allowed_actions_on_async(resource) is functionally
    equivalent to get_allowed_actions_async(actor, resource).
    """
    direct_result = await brazil_authz.get_allowed_actions_async(
        harry_tuttle, sample_duct
    )
    fluent_result = await brazil_authz.can(harry_tuttle).allowed_actions_on_async(
        sample_duct
    )

    assert direct_result == fluent_result


def test_multiple_roles_accumulate_permissions(
    brazil_authz: Cadurso,
    jack_lint: Character,
    form_27b_6: OfficialForm,
    torture_room: InterrogationChamber,
    central_services_office: GovernmentBuilding,
) -> None:
    """
    Jack Lint (BUREAUCRAT + TORTURER) accumulates permissions from both roles.

    Edge case: Verifies that having multiple roles doesn't cause conflicts or
    missed permissions. Each resource type query should return permissions
    granted by any of the actor's roles.
    """
    # Form permissions from BUREAUCRAT role
    # NOT allowed: PaperworkPermission.ARCHIVE_FORM
    form_allowed = brazil_authz.get_allowed_actions(jack_lint, form_27b_6)
    assert form_allowed == {
        PaperworkPermission.READ_FORM,
        PaperworkPermission.SUBMIT_FORM,
    }

    # Interrogation permissions from TORTURER role
    chamber_allowed = brazil_authz.get_allowed_actions(jack_lint, torture_room)
    assert chamber_allowed == {TorturePermission.INTERROGATE}

    # Building permissions from BUREAUCRAT role
    # NOT allowed: BuildingPermission.ARREST_SUSPECTS, BuildingPermission.APPROVE_BUDGET
    building_allowed = brazil_authz.get_allowed_actions(
        jack_lint, central_services_office
    )
    assert building_allowed == {BuildingPermission.ENTER_DEPARTMENT}
