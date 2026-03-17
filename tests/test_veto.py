"""Tests for Veto edge cases that don't belong to any specific test universe."""

from dataclasses import dataclass

import pytest

from cadurso import Cadurso
from cadurso.exceptions import Veto


@dataclass
class Actor:
    name: str


@dataclass
class Resource:
    name: str


def test_veto_without_reason() -> None:
    """raise Veto() (no argument) produces reason=None."""
    c = Cadurso()

    @c.add_rule("act")
    def always_vetoed(actor: Actor, resource: Resource) -> bool:
        raise Veto()

    c.freeze()

    decision = c.is_allowed(Actor("a"), "act", Resource("r"))
    assert not decision
    assert decision.reason is None


def test_non_veto_exception_propagates() -> None:
    """Non-Veto exceptions in rules are not caught — they propagate to the caller."""
    c = Cadurso()

    @c.add_rule("act")
    def broken_rule(actor: Actor, resource: Resource) -> bool:
        raise RuntimeError("something went wrong")

    c.freeze()

    with pytest.raises(RuntimeError, match="something went wrong"):
        c.is_allowed(Actor("a"), "act", Resource("r"))
