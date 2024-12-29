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

AuthorizationDecision = bool
"""
An AuthorizationDecision is a boolean that indicates whether an Actor is allowed to perform an Action on a Resource.
"""

AuthorizationFunction = (
    Callable[[Actor, Resource], AuthorizationDecision]
    | Callable[[Actor, Resource], Awaitable[AuthorizationDecision]]
)
"""
An AuthorizationFunction is a function that takes an Actor and a Resource and returns (synchronously or asynchronously)
an AuthorizationDecision, representing the decision to allow or deny the Actor to perform an Action on the Resource.
"""

RuleStorageKey = tuple[ActorType, Action, ResourceType]
RuleStorage = dict[RuleStorageKey, set[AuthorizationFunction]]
"""
A RuleStorage is a dictionary that maps a tuple of an Actor, an Action, and a Resource to a set of AuthorizationFunctions.
"""
