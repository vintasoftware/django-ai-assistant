class AIAssistantMisconfiguredError(Exception):
    """Raised when the AI assistant is misconfigured, e.g. when assistant id is invalid."""

    pass


class AIAssistantNotDefinedError(Exception):
    """Raised when the AI assistant is not defined when trying to get it by id."""

    pass


class AIUserNotAllowedError(Exception):
    """Raised when the user has no permission to manage a Thread, Message, or AIAssistant."""

    pass
