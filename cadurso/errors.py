# Error messages
from typing import Any

ERROR_CANNOT_ADD_RULE_FROZEN = "Cannot add rules to a frozen Cadurso instance"

ERROR_AUTH_FUNC_NOT_CALLABLE = "Authorization function must be a callable object"

ERROR_AUTH_FUNC_WRONG_ARG_COUNT = (
    "Authorization function must have two positional parameters"
)


def error_auth_func_wrong_number_of_parameters(param_count: int) -> str:
    return f"{ERROR_AUTH_FUNC_WRONG_ARG_COUNT}, got {param_count}"


ERROR_AUTH_FUNC_ACTION_NOT_HASHABLE = (
    "Authorization function's target action must be hashable"
)


ERROR_AUTH_FUNC_RETURN_NOT_BOOL_OR_BOOL_AWAITABLE = "Authorization function must return a boolean or an awaitable that returns a boolean"


def error_auth_func_return_not_bool_or_bool_awaitable(return_type: Any) -> str:
    return f'{ERROR_AUTH_FUNC_RETURN_NOT_BOOL_OR_BOOL_AWAITABLE}, got "{return_type}"'


ERROR_AUTH_FUNC_PARAM_MUST_BE_POSITIONAL = (
    "Authorization function parameters must be positional"
)


def error_auth_func_param_not_positional(param_kind: Any, param: Any) -> str:
    return f"{ERROR_AUTH_FUNC_PARAM_MUST_BE_POSITIONAL}, got {param_kind} on {param}"


ERROR_AUTH_FUNC_TYPE_HINT_MUST_BE_TYPE = "type hint must be a type"


def error_auth_func_type_hint_not_type(identifier: str, hint_value: Any) -> str:
    return f'{identifier} {ERROR_AUTH_FUNC_TYPE_HINT_MUST_BE_TYPE}, got "{hint_value}"'


ERROR_INSTANCE_NOT_FROZEN = (
    "Cadurso instance must be frozen before querying permissions"
)

ERROR_CANNOT_FREEZE_ALREADY_FROZEN = "Cadurso instance is already frozen"

ERROR_QUERY_IS_INCOMPLETE = "Query is incomplete"
