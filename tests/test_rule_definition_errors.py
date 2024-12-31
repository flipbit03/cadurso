from dataclasses import dataclass
from typing import cast

import pytest

from cadurso import Cadurso
from cadurso.errors import (
    ERROR_AUTH_FUNC_ACTION_NOT_HASHABLE,
    ERROR_AUTH_FUNC_NOT_CALLABLE,
    ERROR_AUTH_FUNC_PARAM_MUST_BE_POSITIONAL,
    ERROR_AUTH_FUNC_RETURN_NOT_BOOL_OR_BOOL_AWAITABLE,
    ERROR_AUTH_FUNC_TYPE_HINT_MUST_BE_TYPE,
    ERROR_AUTH_FUNC_WRONG_ARG_COUNT,
    ERROR_CANNOT_ADD_RULE_FROZEN,
)
from cadurso.exceptions import CadursoRuleDefinitionError


def test_fail_to_add_rule_to_frozen_cadurso_instance() -> None:
    """
    You cannot add a rule to a frozen Cadurso instance.
    """
    cadurso = Cadurso()

    # Freeze the instance
    cadurso_frozen = cadurso.freeze()

    # .freeze() returns itself.
    # This is useful for re-exporting the authz system *after* defining all the rules. e.g:
    #
    # cadurso_base = Cadurso()
    # @cadurso_base.add_rule(...)  (several times)
    #
    # Then, somewhere else in the code, probably in a top-level module:
    # import cadurso_base from some_module
    # cadurso = cadurso_base.freeze()
    # __all__ = ["cadurso"]
    assert cadurso_frozen is cadurso

    with pytest.raises(CadursoRuleDefinitionError) as exc_info:

        @cadurso.add_rule("test")
        def this_rule_will_blow_up(_actor: str, _resource: str) -> bool:
            return True

    assert cast(str, exc_info.value.args[0]) == ERROR_CANNOT_ADD_RULE_FROZEN


def test_fail_cannot_add_non_callable_as_rule() -> None:
    """
    You cannot add a non-callable object as a rule.
    """
    cadurso = Cadurso()

    with pytest.raises(CadursoRuleDefinitionError) as exc_info:
        # Mypy will complain about this, but we're testing the runtime behavior
        cadurso.add_rule("test")(42)  # type: ignore

    assert cast(str, exc_info.value.args[0]) == ERROR_AUTH_FUNC_NOT_CALLABLE


def test_fail_cannot_add_auth_function_with_more_than_two_parameters() -> None:
    """
    You cannot add an authorization function with more than two parameters.
    """
    cadurso = Cadurso()

    with pytest.raises(CadursoRuleDefinitionError) as exc_info:

        @cadurso.add_rule("test")  # type: ignore
        def this_rule_will_blow_up(_actor: str, _resource: str, _extra: str) -> bool:
            # Mypy will complain about this, but we're testing the runtime behavior
            return True

    assert ERROR_AUTH_FUNC_WRONG_ARG_COUNT in cast(str, exc_info.value.args[0])


def test_fail_cannot_add_rule_with_nonhashable_action() -> None:
    """
    It's okay for Actors and Resources to not implement __hash__, as we save their types, not instances,
    and types are always hashable.

    Actions, on the other hand, must be hashable (i.e., implement __hash__), demonstrating uniqueness.
    """
    cadurso = Cadurso()

    @dataclass
    class MockUser:
        name: str
        id: int

    @dataclass
    class MockDocument:
        content: str
        id: int
        owner: MockUser

    # Dicts are not hashable.
    invalid_action_object = {
        "action": "read",
    }

    with pytest.raises(CadursoRuleDefinitionError) as exc_info:
        # MyPy will complain about this, but we're testing the runtime behavior, so we type-ignore
        @cadurso.add_rule(invalid_action_object)  # type: ignore
        def this_rule_will_blow_up(actor: MockUser, resource: MockDocument) -> bool:
            return resource.owner == actor

    assert ERROR_AUTH_FUNC_ACTION_NOT_HASHABLE in cast(str, exc_info.value.args[0])


def test_fail_cannot_add_rule_with_nonpositional_params() -> None:
    """
    You cannot add a rule with non-positional parameters.
    """
    cadurso = Cadurso()

    with pytest.raises(CadursoRuleDefinitionError) as exc_info:

        @cadurso.add_rule("test")  # type: ignore
        def this_rule_will_blow_up(_actor: str, *, _resource: str) -> bool:
            # This function has 2 parameters, so the parameter count check will pass.
            # But the second parameter, `resource`, is a keyword-only argument
            # MyPy will complain about this, but we're testing the runtime behavior
            return True

    assert ERROR_AUTH_FUNC_PARAM_MUST_BE_POSITIONAL in cast(str, exc_info.value.args[0])


def test_can_add_rule_with_only_positional_params() -> None:
    """
    You can add a rule with only positional parameters.
    """
    cadurso = Cadurso()

    @cadurso.add_rule("test")
    def this_rule_will_not_blow_up(_actor: str, _resource: str, /) -> bool:
        # Both of the parameters are positional *ONLY*, because of the `/` in the signature
        # This will work just fine
        return True

    assert cadurso.rule_count == 1
    assert len(cadurso.rule_storage) == 1


def test_fail_cannot_add_rule_that_does_not_return_bool() -> None:
    """
    You cannot add a rule that does not return a boolean.
    """
    cadurso = Cadurso()

    with pytest.raises(CadursoRuleDefinitionError) as exc_info:
        # MyPy will complain about this, but we're testing the runtime behavior, so we type-ignore
        @cadurso.add_rule("test")  # type: ignore
        def this_rule_will_blow_up(_actor: str, _resource: str) -> str:
            # We don't care if non-zero length strings are truthy
            # We favor explicitness, as preconized in the Zen of Python *wink*

            return "This is not a boolean"

    assert ERROR_AUTH_FUNC_RETURN_NOT_BOOL_OR_BOOL_AWAITABLE in cast(
        str, exc_info.value.args[0]
    )


def test_cannot_add_rule_actor_is_not_a_type() -> None:
    """
    You cannot add a rule with an actor (or resource) type hint that is not actually a type.
    """
    cadurso = Cadurso()

    with pytest.raises(CadursoRuleDefinitionError) as exc_info:

        @dataclass
        class User:
            name: str
            id: int

        john = User("John", 42)

        # MyPy will complain about this, but we're testing the runtime behavior, so we type-ignore
        @cadurso.add_rule("test")
        def this_rule_will_blow_up(_actor: john, _resource: int) -> bool:  # type: ignore
            # `john` is an instance, not a type
            return True

    assert ERROR_AUTH_FUNC_TYPE_HINT_MUST_BE_TYPE in cast(str, exc_info.value.args[0])
