"""Custom domain-specific exceptions for the Library API.

These exceptions are raised by the service and repository layers
to represent expected error conditions, which are then mapped
to structured JSON responses by the error handlers.
"""

class NotFound(Exception):
    """Requested resource was not found."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)
        self.message = message


class Conflict(Exception):
    """Operation conflicts with current resource state (e.g., already borrowed)."""
    def __init__(self, message: str = "Conflict"):
        super().__init__(message)
        self.message = message


class ValidationError(Exception):
    """Domain validation error (not payload shape — that’s handled by Pydantic)."""
    def __init__(self, message: str = "Validation error"):
        super().__init__(message)
        self.message = message
