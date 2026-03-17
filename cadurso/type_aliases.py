from typing import Any, Awaitable, Callable, Hashable

Actor = Any
"""
An Actor is an entity (instance) that will be granted or denied access to a resource.
"""

ActorType = type[Actor]
"""
An ActorType is a type that represents an Actor.
"""

Action = Hashable
"""
An Action that an Actor can perform on a Resource.

Anything that implements __hash__ can be used as an ActionType.
"""

Resource = Any
"""
A Resource that an Actor can perform an Action on.
"""

ResourceType = type[Resource]
"""
A ResourceType is a type that represents a Resource.
"""


class AuthorizationDecision:
    """
    The result of an authorization query. Carries the decision and an optional reason for denial.

    Fully backward-compatible with boolean usage via ``__bool__``.
    """

    __slots__ = ("allowed", "reason")

    def __init__(self, *, allowed: bool, reason: str | None = None) -> None:
        self.allowed = allowed
        self.reason = reason

    def __bool__(self) -> bool:
        return self.allowed

    def __repr__(self) -> str:
        if self.reason is not None:
            return f"AuthorizationDecision(allowed={self.allowed!r}, reason={self.reason!r})"
        return f"AuthorizationDecision(allowed={self.allowed!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AuthorizationDecision):
            return self.allowed == other.allowed and self.reason == other.reason
        return NotImplemented


AuthorizationFunction = (
    Callable[[Actor, Resource], bool] | Callable[[Actor, Resource], Awaitable[bool]]
)
"""
An AuthorizationFunction is a function that takes an Actor and a Resource and returns (synchronously or asynchronously)
a bool, representing the decision to allow or deny the Actor to perform an Action on the Resource.
"""

RuleStorageKey = tuple[ActorType, Action, ResourceType]
RuleStorage = dict[RuleStorageKey, set[AuthorizationFunction]]
"""
A RuleStorage is a dictionary that maps a tuple of an Actor, an Action, and a Resource to a set of AuthorizationFunctions.
"""
