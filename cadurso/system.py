import asyncio
import inspect
import logging
from typing import Callable, Hashable, cast

from cadurso.errors import (
    ERROR_AUTH_FUNC_ACTION_NOT_HASHABLE,
    ERROR_AUTH_FUNC_NOT_CALLABLE,
    ERROR_CANNOT_ADD_RULE_FROZEN,
    ERROR_CANNOT_FREEZE_ALREADY_FROZEN,
    ERROR_INSTANCE_NOT_FROZEN,
    error_auth_func_param_not_positional,
    error_auth_func_return_not_bool_or_bool_awaitable,
    error_auth_func_type_hint_not_type,
    error_auth_func_wrong_number_of_parameters,
)
from cadurso.exceptions import (
    CadursoOperationalError,
    CadursoRuleDefinitionError,
)
from cadurso.sugar import CanQueryBuilder
from cadurso.type_aliases import (
    Action,
    Actor,
    ActorType,
    AuthorizationDecision,
    AuthorizationFunction,
    Resource,
    ResourceType,
    RuleStorage,
    RuleStorageKey,
)

logger = logging.getLogger(__name__)


class Cadurso:
    def __init__(self) -> None:
        self.rule_count = 0
        self.rule_storage: RuleStorage = {}

        self.__frozen = False
        """
        A boolean indicating whether the Cadurso instance is frozen.

        Frozen instances:
        - Cannot have new rules added to them, and
        - Cannot be unfrozen.
        """

    def __add(
        self,
        actor_type: ActorType,
        action: Action,
        resource_type: ResourceType,
        authorization_function: AuthorizationFunction,
    ) -> None:
        storage_key: RuleStorageKey = (actor_type, action, resource_type)

        self.rule_storage.setdefault(storage_key, set()).add(authorization_function)
        self.rule_count += 1

    def add_rule(
        self, action: Action
    ) -> Callable[[AuthorizationFunction], AuthorizationFunction]:
        if self.__frozen:
            raise CadursoRuleDefinitionError(ERROR_CANNOT_ADD_RULE_FROZEN)

        def add_rule_inner(
            authorization_function: AuthorizationFunction,
        ) -> AuthorizationFunction:
            # Check if action is hashable
            if not isinstance(action, Hashable):
                raise CadursoRuleDefinitionError(ERROR_AUTH_FUNC_ACTION_NOT_HASHABLE)

            # Check if the authorization function is callable
            if not callable(authorization_function):
                raise CadursoRuleDefinitionError(ERROR_AUTH_FUNC_NOT_CALLABLE)

            rule_func_signature = inspect.signature(authorization_function)

            # Function should have, exactly, two parameters
            if len(rule_func_signature.parameters) != 2:
                raise CadursoRuleDefinitionError(
                    error_auth_func_wrong_number_of_parameters(
                        len(rule_func_signature.parameters)
                    )
                )

            # Extract actor and resource Parameter objects from the inspected function signature
            # Actor is the first parameter, resource is the second
            actor_parameter, resource_parameter = (
                rule_func_signature.parameters.values()
            )
            identified_parameters = (
                ("Actor", actor_parameter),
                ("Resource", resource_parameter),
            )

            # The two inspected function arguments type hints must be:
            # - Types,
            # - which generate Hashable instances, and
            # - presented as positional arguments
            for identifier, parameter in identified_parameters:
                if not isinstance(parameter.annotation, type):
                    raise CadursoRuleDefinitionError(
                        error_auth_func_type_hint_not_type(
                            identifier, parameter.annotation
                        )
                    )

                if parameter.kind not in (
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.POSITIONAL_ONLY,
                ):
                    raise CadursoRuleDefinitionError(
                        error_auth_func_param_not_positional(parameter.kind, parameter)
                    )

            # The return type must be boolean or an awaitable that returns a boolean
            if not (
                rule_func_signature.return_annotation is bool
                or issubclass(rule_func_signature.return_annotation, asyncio.Future)
            ):
                raise CadursoRuleDefinitionError(
                    error_auth_func_return_not_bool_or_bool_awaitable(
                        rule_func_signature.return_annotation
                    )
                )

            # Add the rule to the rule storage
            # Parameter.annotation is the actual content right of the colon in the function signature
            self.__add(
                actor_parameter.annotation,
                action,
                resource_parameter.annotation,
                authorization_function,
            )

            return authorization_function

        return add_rule_inner

    def is_allowed(
        self, actor: Actor, action: Action, resource: Resource
    ) -> AuthorizationDecision:
        """
        Evaluate a permission query synchronously.
        If there are async rules, this method use asyncio.run() to evaluate them.
        If you are already in an async context, use is_allowed_async() instead.

        :param actor: The actor that is trying to perform an action on a resource.
        :param action:  The action that the actor is trying to perform.
        :param resource:  The resource that the actor is trying to perform the action on.
        :return: A boolean indicating whether the actor is allowed to perform the action on the resource.
        """
        if not self.__frozen:
            raise CadursoOperationalError(ERROR_INSTANCE_NOT_FROZEN)

        for rule in self.rule_storage.get((type(actor), action, type(resource)), []):
            if inspect.iscoroutinefunction(rule):
                decision = cast(bool, asyncio.run(rule(actor, resource)))
            else:
                decision = cast(bool, rule(actor, resource))

            if decision is not True:
                logger.debug(
                    f'"{actor}" is not allowed to "{action}" on "{resource}", trying other rules...'
                )
                continue

            logger.debug(f'"{actor}" is allowed to "{action}" on "{resource}"')
            return True

        return False

    async def is_allowed_async(
        self, actor: Actor, action: Action, resource: Resource
    ) -> AuthorizationDecision:
        """
        Evaluate a permission query asynchronously.

        :param actor: The actor that is trying to perform an action on a resource.
        :param action:  The action that the actor is trying to perform.
        :param resource:  The resource that the actor is trying to perform the action on.
        :return: A boolean indicating whether the actor is allowed to perform the action on the resource.
        """
        for rule in self.rule_storage.get((type(actor), action, type(resource)), []):
            if inspect.iscoroutinefunction(rule):
                decision = await rule(actor, resource)
            else:
                decision = rule(actor, resource)

            if decision is not True:
                logger.debug(
                    f'"{actor}" is not allowed to "{action}" on "{resource}", trying other rules...'
                )
                continue

            logger.debug(f'"{actor}" is allowed to "{action}" on "{resource}"')
            return True

        return False

    def can(self, actor: Actor) -> CanQueryBuilder:
        """
        Syntax sugar for asking permissions (Query Builder-style).
        """
        return CanQueryBuilder(cadurso=self, actor=actor)

    def freeze(self) -> None:
        """
        Freeze the Cadurso instance, preventing new rules from being added.
        """

        if self.__frozen:
            raise CadursoOperationalError(ERROR_CANNOT_FREEZE_ALREADY_FROZEN)

        self.__frozen = True

        # Log the number of rules added
        logger.debug(f"Frozen Cadurso instance with {self.rule_count} rules")
