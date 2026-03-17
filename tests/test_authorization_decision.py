"""Unit tests for the AuthorizationDecision class itself."""

from cadurso import AuthorizationDecision


def test_bool_true() -> None:
    d = AuthorizationDecision(allowed=True)
    assert bool(d) is True


def test_bool_false() -> None:
    d = AuthorizationDecision(allowed=False)
    assert bool(d) is False


def test_repr_without_reason() -> None:
    d = AuthorizationDecision(allowed=True)
    assert repr(d) == "AuthorizationDecision(allowed=True)"


def test_repr_with_reason() -> None:
    d = AuthorizationDecision(allowed=False, reason="nope")
    assert repr(d) == "AuthorizationDecision(allowed=False, reason='nope')"


def test_equality() -> None:
    a = AuthorizationDecision(allowed=True)
    b = AuthorizationDecision(allowed=True)
    assert a == b


def test_inequality_different_allowed() -> None:
    a = AuthorizationDecision(allowed=True)
    b = AuthorizationDecision(allowed=False)
    assert a != b


def test_inequality_different_reason() -> None:
    a = AuthorizationDecision(allowed=False, reason="a")
    b = AuthorizationDecision(allowed=False, reason="b")
    assert a != b


def test_equal_to_matching_bool() -> None:
    assert AuthorizationDecision(allowed=True) == True  # noqa: E712
    assert AuthorizationDecision(allowed=False) == False  # noqa: E712
    assert AuthorizationDecision(allowed=True) != False  # noqa: E712
    assert AuthorizationDecision(allowed=False) != True  # noqa: E712


def test_not_equal_to_non_bool_types() -> None:
    d = AuthorizationDecision(allowed=True)
    assert d != 1
    assert d != "True"
