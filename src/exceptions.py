"""Expected application/domain exceptions."""


class ZycusAppError(Exception):
    """Base application exception."""


class DataLoadError(ZycusAppError):
    """Dataset loading or structure failure."""


class InvalidTicketError(ZycusAppError):
    """Ticket input cannot be processed."""


class InvalidAccountIdError(ZycusAppError):
    """Account identifier is invalid."""


class AccountNotFoundError(ZycusAppError):
    """Requested account was not found."""


class RetrievalError(ZycusAppError):
    """Retrieval/indexing failure."""


class LLMUnavailableError(ZycusAppError):
    """LLM cannot be used for the requested operation."""


class OutputValidationError(ZycusAppError):
    """Generated output failed structural or evidence validation."""
