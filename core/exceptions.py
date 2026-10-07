class FurFindException(Exception):
    """Base exception class for all custom exceptions in FurFind application."""
    def __init__(self, message="An unexpected system error occurred."):
        self.message = message
        super().__init__(self.message)


class DatabaseError(FurFindException):
    """Raised when a database query, connection, or transaction fails."""
    def __init__(self, message="A database operation error occurred."):
        super().__init__(message)


class ValidationError(FurFindException):
    """Raised when user input or data validation fails (e.g., missing fields, invalid formats)."""
    def __init__(self, message="Invalid input data provided."):
        super().__init__(message)


class AuthError(FurFindException):
    """Raised when authentication fails (e.g., wrong credentials, invalid session)."""
    def __init__(self, message="Authentication failed. Invalid credentials."):
        super().__init__(message)


# Alias AuthenticationError to AuthError for backwards compatibility across controllers
AuthenticationError = AuthError


class AuthorizationError(FurFindException):
    """Raised when a user attempts an action forbidden by their role (Role-Based Access Control)."""
    def __init__(self, message="Access denied. You do not have permission to perform this action."):
        super().__init__(message)


class ResourceNotFoundError(FurFindException):
    """Raised when a requested database entity or record is not found."""
    def __init__(self, message="The requested resource could not be found."):
        super().__init__(message)