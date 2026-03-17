"""Tests verifying AuthorizationDecision behavior within the Inception universe."""

from cadurso import Cadurso

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
