from typing import cast

import pytest

from cadurso import Cadurso
from cadurso.errors import ERROR_CANNOT_FREEZE_ALREADY_FROZEN, ERROR_INSTANCE_NOT_FROZEN
from cadurso.exceptions import CadursoOperationalError


def test_cannot_evaluate_permission_without_freezing_cadurso_instance() -> None:
    """
    You cannot evaluate permissions on a Cadurso instance that has not been frozen.
    """
    cadurso = Cadurso()

    with pytest.raises(CadursoOperationalError) as exc_info:
        cadurso.is_allowed("test", "test", "test")

    assert cast(str, exc_info.value.args[0]) == ERROR_INSTANCE_NOT_FROZEN


def test_cannot_freeze_instance_already_frozen() -> None:
    """
    You cannot freeze a Cadurso instance that has already been frozen.
    """
    cadurso = Cadurso()
    cadurso.freeze()

    with pytest.raises(CadursoOperationalError) as exc_info:
        cadurso.freeze()

    assert cast(str, exc_info.value.args[0]) == ERROR_CANNOT_FREEZE_ALREADY_FROZEN
