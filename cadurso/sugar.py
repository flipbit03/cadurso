from dataclasses import dataclass
from typing import TYPE_CHECKING, Never

from cadurso.errors import ERROR_QUERY_IS_INCOMPLETE
from cadurso.exceptions import CadursoIncompleteQueryError
from cadurso.type_aliases import Action, Actor, AuthorizationDecision, Resource

if TYPE_CHECKING:  # pragma: no cover
    from cadurso import Cadurso


@dataclass
class OnResourceClause:
    can_query: CanQueryBuilder
    action: Action

    def on(self, resource: Resource) -> AuthorizationDecision:
        return self.can_query.cadurso.is_allowed(
            self.can_query.actor, self.action, resource
        )

    async def on_async(self, resource: Resource) -> AuthorizationDecision:
        return await self.can_query.cadurso.is_allowed_async(
            self.can_query.actor, self.action, resource
        )

    def __bool__(self) -> Never:
        """Avoid accidentally using the incomplete query as a boolean"""
        raise CadursoIncompleteQueryError(
            f"{ERROR_QUERY_IS_INCOMPLETE}: Do .on() or .on_async() to continue building it"
        )


@dataclass
class CanQueryBuilder:
    cadurso: Cadurso
    actor: Actor

    def do(self, action: Action) -> OnResourceClause:
        return OnResourceClause(can_query=self, action=action)

    def allowed_actions_on(self, resource: Resource) -> set[Action]:
        """Return all actions this actor can perform on the given resource."""
        return self.cadurso.get_allowed_actions(self.actor, resource)

    async def allowed_actions_on_async(self, resource: Resource) -> set[Action]:
        """Return all actions this actor can perform on the given resource (async)."""
        return await self.cadurso.get_allowed_actions_async(self.actor, resource)

    def __bool__(self) -> Never:
        """Avoid accidentally using the incomplete query as a boolean"""
        raise CadursoIncompleteQueryError(
            f"{ERROR_QUERY_IS_INCOMPLETE}: Do .do() to continue building it"
        )
