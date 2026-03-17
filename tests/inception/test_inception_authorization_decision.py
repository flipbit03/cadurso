"""Tests verifying AuthorizationDecision truthiness/falsiness and attribute access."""

from cadurso import AuthorizationDecision, Cadurso

from .conftest import Dreamer, DreamLevel, DreamPermission

# ---------------------------------------------------------------------------
# Truthiness / backward compatibility
# ---------------------------------------------------------------------------


def test_allowed_decision_is_truthy(
    inception_universe: Cadurso, arthur: Dreamer, city_level: DreamLevel
) -> None:
    decision = inception_universe.is_allowed(
        arthur, DreamPermission.NAVIGATE, city_level
    )
    assert decision
    assert decision.allowed is True


def test_denied_decision_is_falsy(
    inception_universe: Cadurso, fischer: Dreamer, snow_fortress: DreamLevel
) -> None:
    decision = inception_universe.is_allowed(
        fischer, DreamPermission.NAVIGATE, snow_fortress
    )
    assert not decision
    assert decision.allowed is False


def test_if_statement_works(
    inception_universe: Cadurso, arthur: Dreamer, city_level: DreamLevel
) -> None:
    """Backward compat: `if cadurso.is_allowed(...)` works unchanged."""
    assert inception_universe.is_allowed(arthur, DreamPermission.NAVIGATE, city_level)


def test_assert_not_works(
    inception_universe: Cadurso, mal: Dreamer, city_level: DreamLevel
) -> None:
    """Backward compat: `assert not cadurso.is_allowed(...)` works."""
    assert not inception_universe.is_allowed(mal, DreamPermission.NAVIGATE, city_level)


# ---------------------------------------------------------------------------
# Reason attribute
# ---------------------------------------------------------------------------


def test_reason_is_none_when_no_veto(
    inception_universe: Cadurso, arthur: Dreamer, city_level: DreamLevel
) -> None:
    decision = inception_universe.is_allowed(
        arthur, DreamPermission.NAVIGATE, city_level
    )
    assert decision.reason is None


def test_reason_is_none_when_denied_without_veto(
    inception_universe: Cadurso, mal: Dreamer, city_level: DreamLevel
) -> None:
    """Mal is a projection — denied by rule logic, not Veto. Reason should be None."""
    decision = inception_universe.is_allowed(mal, DreamPermission.NAVIGATE, city_level)
    assert not decision
    assert decision.reason is None


def test_reason_populated_on_veto(
    inception_universe: Cadurso, cobb: Dreamer, limbo: DreamLevel
) -> None:
    decision = inception_universe.is_allowed(cobb, DreamPermission.NAVIGATE, limbo)
    assert not decision
    assert decision.reason == "dream level has collapsed"


# ---------------------------------------------------------------------------
# AuthorizationDecision class unit tests
# ---------------------------------------------------------------------------


def test_authorization_decision_bool_true() -> None:
    d = AuthorizationDecision(allowed=True)
    assert bool(d) is True


def test_authorization_decision_bool_false() -> None:
    d = AuthorizationDecision(allowed=False)
    assert bool(d) is False


def test_authorization_decision_repr_without_reason() -> None:
    d = AuthorizationDecision(allowed=True)
    assert repr(d) == "AuthorizationDecision(allowed=True)"


def test_authorization_decision_repr_with_reason() -> None:
    d = AuthorizationDecision(allowed=False, reason="nope")
    assert repr(d) == "AuthorizationDecision(allowed=False, reason='nope')"


def test_authorization_decision_equality() -> None:
    a = AuthorizationDecision(allowed=True)
    b = AuthorizationDecision(allowed=True)
    assert a == b


def test_authorization_decision_inequality_different_allowed() -> None:
    a = AuthorizationDecision(allowed=True)
    b = AuthorizationDecision(allowed=False)
    assert a != b


def test_authorization_decision_inequality_different_reason() -> None:
    a = AuthorizationDecision(allowed=False, reason="a")
    b = AuthorizationDecision(allowed=False, reason="b")
    assert a != b


def test_authorization_decision_not_equal_to_other_types() -> None:
    d = AuthorizationDecision(allowed=True)
    assert d != True  # noqa: E712
    assert d != 1
