"""Tests verifying AuthorizationDecision truthiness/falsiness and attribute access."""

from cadurso import AuthorizationDecision, Cadurso

from .conftest import DreamLevel, DreamPermission, Dreamer, Totem, TotemPermission


class TestAuthorizationDecisionTruthiness:
    """AuthorizationDecision works seamlessly with if/assert/assert not."""

    def test_allowed_decision_is_truthy(
        self, inception_universe: Cadurso, arthur: Dreamer, city_level: DreamLevel
    ) -> None:
        decision = inception_universe.is_allowed(arthur, DreamPermission.NAVIGATE, city_level)
        assert decision
        assert decision.allowed is True

    def test_denied_decision_is_falsy(
        self, inception_universe: Cadurso, fischer: Dreamer, snow_fortress: DreamLevel
    ) -> None:
        decision = inception_universe.is_allowed(fischer, DreamPermission.NAVIGATE, snow_fortress)
        assert not decision
        assert decision.allowed is False

    def test_if_statement_works(
        self, inception_universe: Cadurso, arthur: Dreamer, city_level: DreamLevel
    ) -> None:
        """Backward compat: `if cadurso.is_allowed(...)` works unchanged."""
        if inception_universe.is_allowed(arthur, DreamPermission.NAVIGATE, city_level):
            pass  # expected
        else:
            raise AssertionError("should have been allowed")

    def test_assert_not_works(
        self, inception_universe: Cadurso, mal: Dreamer, city_level: DreamLevel
    ) -> None:
        """Backward compat: `assert not cadurso.is_allowed(...)` works."""
        assert not inception_universe.is_allowed(mal, DreamPermission.NAVIGATE, city_level)


class TestAuthorizationDecisionReason:
    """The .reason attribute is populated on Veto and None otherwise."""

    def test_reason_is_none_when_no_veto(
        self, inception_universe: Cadurso, arthur: Dreamer, city_level: DreamLevel
    ) -> None:
        decision = inception_universe.is_allowed(arthur, DreamPermission.NAVIGATE, city_level)
        assert decision.reason is None

    def test_reason_is_none_when_denied_without_veto(
        self, inception_universe: Cadurso, mal: Dreamer, city_level: DreamLevel
    ) -> None:
        """Mal is a projection — denied by rule logic, not Veto. Reason should be None."""
        decision = inception_universe.is_allowed(mal, DreamPermission.NAVIGATE, city_level)
        assert not decision
        assert decision.reason is None

    def test_reason_populated_on_veto(
        self, inception_universe: Cadurso, cobb: Dreamer, limbo: DreamLevel
    ) -> None:
        decision = inception_universe.is_allowed(cobb, DreamPermission.NAVIGATE, limbo)
        assert not decision
        assert decision.reason == "dream level has collapsed"


class TestAuthorizationDecisionClass:
    """Unit tests for the AuthorizationDecision class itself."""

    def test_bool_true(self) -> None:
        d = AuthorizationDecision(allowed=True)
        assert bool(d) is True

    def test_bool_false(self) -> None:
        d = AuthorizationDecision(allowed=False)
        assert bool(d) is False

    def test_repr_without_reason(self) -> None:
        d = AuthorizationDecision(allowed=True)
        assert repr(d) == "AuthorizationDecision(allowed=True)"

    def test_repr_with_reason(self) -> None:
        d = AuthorizationDecision(allowed=False, reason="nope")
        assert repr(d) == "AuthorizationDecision(allowed=False, reason='nope')"

    def test_equality(self) -> None:
        a = AuthorizationDecision(allowed=True)
        b = AuthorizationDecision(allowed=True)
        assert a == b

    def test_inequality_different_allowed(self) -> None:
        a = AuthorizationDecision(allowed=True)
        b = AuthorizationDecision(allowed=False)
        assert a != b

    def test_inequality_different_reason(self) -> None:
        a = AuthorizationDecision(allowed=False, reason="a")
        b = AuthorizationDecision(allowed=False, reason="b")
        assert a != b

    def test_not_equal_to_other_types(self) -> None:
        d = AuthorizationDecision(allowed=True)
        assert d != True  # noqa: E712
        assert d != 1
