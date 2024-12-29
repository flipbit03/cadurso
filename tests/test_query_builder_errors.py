from typing import cast

import pytest

from cadurso import Cadurso
from cadurso.errors import ERROR_QUERY_IS_INCOMPLETE
from cadurso.exceptions import CadursoIncompleteQueryError


def test_cannot_use_can_query_builder_as_bool() -> None:
    """
    You cannot use the `can` query builder as a boolean.

    Why this is implemented: If you accidentally stop building your query
    as cadurso.can().do().on() and just do cadurso.can(), you would get a faux
    True value, which is not what you want.
    """
    cadurso = Cadurso()

    with pytest.raises(CadursoIncompleteQueryError) as exc_info:
        # Whoops! We forgot to continue with .do().on() to appoint the action and the resource
        if cadurso.can("user"):
            # This will just blow up
            pass

    assert ERROR_QUERY_IS_INCOMPLETE in cast(str, exc_info.value.args[0])

    with pytest.raises(CadursoIncompleteQueryError) as exc_info:
        # Whoops! We forgot to continue with .on() to appoint the resource
        if cadurso.can("user").do("read"):
            # This will just blow up
            pass

    assert ERROR_QUERY_IS_INCOMPLETE in cast(str, exc_info.value.args[0])
