"""
Custom exception classes for AIDP MCP Server
"""
from typing import Any, Optional


class AIDPError(Exception):
    """Base exception for all AIDP-related errors"""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.original_error = original_error

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary format"""
        result: dict[str, Any] = {
            "type": self.__class__.__name__,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        if self.original_error:
            result["original_error"] = str(self.original_error)
        return result


class AuthenticationError(AIDPError):
    """Raised when authentication fails"""

    pass


class AuthorizationError(AIDPError):
    """Raised when user lacks permission for an operation"""

    pass


class ResourceNotFoundError(AIDPError):
    """Raised when a requested resource is not found"""

    pass


class ResourceAlreadyExistsError(AIDPError):
    """Raised when attempting to create a resource that already exists"""

    pass


class ValidationError(AIDPError):
    """Raised when input validation fails"""

    pass


class APIError(AIDPError):
    """Raised when an API call fails"""

    pass


class ConfigurationError(AIDPError):
    """Raised when configuration is invalid or missing"""

    pass


class TimeoutError(AIDPError):
    """Raised when an operation times out"""

    pass


class RateLimitError(AIDPError):
    """Raised when API rate limit is exceeded"""

    pass


class NetworkError(AIDPError):
    """Raised when network connectivity issues occur"""

    pass


class InvalidStateError(AIDPError):
    """Raised when a resource is in an invalid state for the requested operation"""

    pass


class QuotaExceededError(AIDPError):
    """Raised when a quota or limit is exceeded"""

    pass
