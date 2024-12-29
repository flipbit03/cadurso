from cadurso import Cadurso
from tests.brazil.conftest import Character, InterrogationChamber, TorturePermission


def test_torturer_can_interrogate(
    brazil_authz: Cadurso,
    jack_lint: Character,
    sam_lowry: Character,
    torture_room: InterrogationChamber,
) -> None:
    """
    Jack Lint has the TORTURER role,
    so he can INTERROGATE in the torture_room.
    """
    assert brazil_authz.is_allowed(
        jack_lint, TorturePermission.INTERROGATE, torture_room
    )

    # Sam Lowry is not a torturer
    assert not brazil_authz.is_allowed(
        sam_lowry, TorturePermission.INTERROGATE, torture_room
    )
