class CadursoBaseError(Exception):
    pass


class CadursoRuleDefinitionError(CadursoBaseError):
    """
    Exception that gets raised when `Cadurso` is unable to ingest a new rule definition.
    """

    pass


class CadursoOperationalError(CadursoBaseError):
    """
    Exception that gets raised when `Cadurso` encounters an operational error.
    """

    pass


class CadursoIncompleteQueryError(CadursoBaseError):
    """
    Exception that gets raised when a query is incomplete and cannot be evaluated.
    """

    pass


class Veto(Exception):
    """Raised inside a rule function to hard-deny an authorization request with an optional reason."""

    def __init__(self, reason: str | None = None) -> None:
        self.reason = reason
        super().__init__(reason)
