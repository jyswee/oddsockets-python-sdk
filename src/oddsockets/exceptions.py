"""
Exception classes for OddSockets Python SDK.
"""

from typing import Optional, Any, Dict


class OddSocketsError(Exception):
    """Base exception class for all OddSockets errors."""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', code='{self.code}')"


class ConnectionError(OddSocketsError):
    """Raised when connection-related errors occur."""
    
    def __init__(
        self,
        message: str = "Connection error occurred",
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, code or "CONNECTION_ERROR", details)


class AuthenticationError(OddSocketsError):
    """Raised when authentication fails."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, code or "AUTHENTICATION_ERROR", details)


class ChannelError(OddSocketsError):
    """Raised when channel-related errors occur."""
    
    def __init__(
        self,
        message: str = "Channel error occurred",
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, code or "CHANNEL_ERROR", details)


class MessageError(OddSocketsError):
    """Raised when message-related errors occur."""
    
    def __init__(
        self,
        message: str = "Message error occurred",
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, code or "MESSAGE_ERROR", details)


class TimeoutError(OddSocketsError):
    """Raised when operations timeout."""
    
    def __init__(
        self,
        message: str = "Operation timed out",
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, code or "TIMEOUT_ERROR", details)


class RateLimitError(OddSocketsError):
    """Raised when rate limits are exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, code or "RATE_LIMIT_ERROR", details)


class ValidationError(OddSocketsError):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str = "Validation error occurred",
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, code or "VALIDATION_ERROR", details)


# Error code constants
class ErrorCode:
    """Error code constants."""
    
    # Connection errors
    CONNECTION_FAILED = "CONNECTION_FAILED"
    CONNECTION_LOST = "CONNECTION_LOST"
    CONNECTION_TIMEOUT = "CONNECTION_TIMEOUT"
    RECONNECTION_FAILED = "RECONNECTION_FAILED"
    
    # Authentication errors
    INVALID_API_KEY = "INVALID_API_KEY"
    API_KEY_EXPIRED = "API_KEY_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Channel errors
    CHANNEL_NOT_FOUND = "CHANNEL_NOT_FOUND"
    CHANNEL_ACCESS_DENIED = "CHANNEL_ACCESS_DENIED"
    CHANNEL_LIMIT_EXCEEDED = "CHANNEL_LIMIT_EXCEEDED"
    
    # Message errors
    MESSAGE_TOO_LARGE = "MESSAGE_TOO_LARGE"
    MESSAGE_INVALID_FORMAT = "MESSAGE_INVALID_FORMAT"
    MESSAGE_DELIVERY_FAILED = "MESSAGE_DELIVERY_FAILED"
    
    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    
    # Server errors
    SERVER_ERROR = "SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    MAINTENANCE_MODE = "MAINTENANCE_MODE"
