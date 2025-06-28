"""Custom exception classes for the application."""


class DatabaseError(Exception):
    """Custom exception for database-related errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ServiceError(Exception):
    """Custom exception for service-related errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class AgentError(Exception):
    """Custom exception for agent-related errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
