from cadurso import Cadurso
from tests.brazil.conftest import (
    Character,
    DreamPermission,
)


def test_sam_lowry_daydream(brazil_authz: Cadurso, sam_lowry: Character) -> None:
    """
    Sam Lowry is a DREAMER and can daydream in his own mind.
    """
    assert brazil_authz.is_allowed(sam_lowry, DreamPermission.DAYDREAM, sam_lowry)


def test_others_cannot_daydream_in_sam(
    brazil_authz: Cadurso,
    sam_lowry: Character,
    jill_layton: Character,
    harry_tuttle: Character,
    mr_kurtzmann: Character,
    chief_minister: Character,
    jack_lint: Character,
    spoor: Character,
    dowser: Character,
) -> None:
    """
    None of these other characters have the right to daydream in Sam's mind,
    because either they are not Sam, or they lack the DREAMER role.
    """
    for not_sam_character in [
        jill_layton,
        harry_tuttle,
        mr_kurtzmann,
        chief_minister,
        jack_lint,
        spoor,
        dowser,
    ]:
        assert not brazil_authz.is_allowed(
            not_sam_character, DreamPermission.DAYDREAM, sam_lowry
        )

        # They cannot daydream in their own minds either, as only Sam is a DREAMER in this universe
        assert not brazil_authz.is_allowed(
            not_sam_character, DreamPermission.DAYDREAM, not_sam_character
        )


def test_sam_cannot_daydream_in_others(
    brazil_authz: Cadurso,
    sam_lowry: Character,
    jill_layton: Character,
    harry_tuttle: Character,
    mr_kurtzmann: Character,
    chief_minister: Character,
    jack_lint: Character,
    spoor: Character,
    dowser: Character,
) -> None:
    """
    Sam Lowry cannot daydream in the minds of others, as he is not a psychic.
    """
    for someone_else in [
        jill_layton,
        harry_tuttle,
        mr_kurtzmann,
        chief_minister,
        jack_lint,
        spoor,
        dowser,
    ]:
        assert not brazil_authz.is_allowed(
            sam_lowry, DreamPermission.DAYDREAM, someone_else
        )
