from cadurso import Cadurso
from tests.brazil.conftest import (
    Character,
    DuctPermission,
    DuctSystem,
    OfficialForm,
)


def test_engineer_needs_form_for_duct_repair(
    brazil_authz: Cadurso,
    spoor: Character,
    sample_duct: DuctSystem,
    form_27b_6: OfficialForm,
) -> None:
    """
    Spoor is an ENGINEER but starts with no forms_in_pocket,
    so he can't REPAIR. Once he obtains form_27b_6, he can.
    """
    assert not brazil_authz.is_allowed(spoor, DuctPermission.REPAIR, sample_duct)

    # Give him the dreaded form 27B-6
    spoor.pocket_contents.append(form_27b_6)
    assert brazil_authz.is_allowed(spoor, DuctPermission.REPAIR, sample_duct)


def test_rebel_does_not_need_form(
    brazil_authz: Cadurso, harry_tuttle: Character, sample_duct: DuctSystem
) -> None:
    """
    Harry Tuttle, being a REBEL, can REPAIR the duct
    without any official forms.
    """
    assert brazil_authz.is_allowed(harry_tuttle, DuctPermission.REPAIR, sample_duct)


def test_bureaucrat_inspect_duct_not_repair(
    brazil_authz: Cadurso, mr_kurtzmann: Character, sample_duct: DuctSystem
) -> None:
    """
    Mr. Kurtzmann is BUREAUCRAT, so he can INSPECT the duct
    but cannot REPAIR it (he's no ENGINEER and definitely not a REBEL).
    """
    assert brazil_authz.is_allowed(mr_kurtzmann, DuctPermission.INSPECT, sample_duct)
    assert not brazil_authz.is_allowed(mr_kurtzmann, DuctPermission.REPAIR, sample_duct)


def test_rebel_destroy_duct(
    brazil_authz: Cadurso,
    harry_tuttle: Character,
    sam_lowry: Character,
    sample_duct: DuctSystem,
) -> None:
    """
    A REBEL can DESTROY the duct system,
    while Sam Lowry (BUREAUCRAT) cannot.
    """
    assert brazil_authz.is_allowed(harry_tuttle, DuctPermission.DESTROY, sample_duct)
    assert not brazil_authz.is_allowed(sam_lowry, DuctPermission.DESTROY, sample_duct)
