"""
Type definitions for OddSockets Python SDK.
"""

from typing import Any, Dict, List, Optional, Union, Callable, Awaitable
from datetime import datetime
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class OddSocketsConfig(TypedDict, total=False):
    """Configuration options for OddSockets client."""
    
    api_key: str
    manager_url: Optional[str]
    user_id: Optional[str]
    auto_connect: Optional[bool]
    reconnect_attempts: Optional[int]
    heartbeat_interval: Optional[float]


class Message(BaseModel):
    """Represents a message received from OddSockets."""
    
    id: str = Field(..., description="Unique message identifier")
    channel: str = Field(..., description="Channel name")
    data: Any = Field(..., description="Message payload")
    timestamp: datetime = Field(..., description="Message timestamp")
    user_id: Optional[str] = Field(None, description="Sender user ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PresenceInfo(BaseModel):
    """Represents presence information for a channel."""
    
    channel: str = Field(..., description="Channel name")
    users: List[str] = Field(..., description="List of user IDs present")
    count: int = Field(..., description="Total number of users present")
    timestamp: datetime = Field(..., description="Presence snapshot timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SubscribeOptions(TypedDict, total=False):
    """Options for channel subscription."""
    
    enable_presence: Optional[bool]
    retain_history: Optional[bool]
    filter_expression: Optional[str]


class PublishOptions(TypedDict, total=False):
    """Options for message publishing."""
    
    ttl: Optional[int]
    metadata: Optional[Dict[str, Any]]
    store_in_history: Optional[bool]


class HistoryOptions(TypedDict, total=False):
    """Options for retrieving message history."""
    
    limit: Optional[int]
    start: Optional[datetime]
    end: Optional[datetime]
    reverse: Optional[bool]


class PublishResult(BaseModel):
    """Represents the result of a publish operation."""
    
    message_id: str = Field(..., description="Unique identifier of the published message")
    timestamp: datetime = Field(..., description="When the message was published")
    channel: str = Field(..., description="Channel the message was published to")
    success: bool = Field(..., description="Whether the publish was successful")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BulkMessage(BaseModel):
    """Represents a message for bulk publishing."""
    
    channel: str = Field(..., description="Channel name")
    message: Any = Field(..., description="Message payload")


class BulkResult(BaseModel):
    """Represents the result of a bulk publish operation."""
    
    success: bool = Field(..., description="Whether the publish was successful")
    result: Optional[PublishResult] = Field(None, description="Publish result if successful")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")


class UsageStats(TypedDict):
    """Owner-scoped usage analytics returned by OddSockets.get_usage_stats().

    Each tile (mau/dau/total_messages/error_rate) is a number OR None; a None
    tile is meaningful (no data) and is never coerced to 0.
    """

    mau: Optional[int]
    dau: Optional[int]
    total_messages: Optional[int]
    error_rate: Optional[float]
    owner_scope: Optional[str]
    detail: Optional[Any]
    timestamp: Optional[str]


# Type aliases for callbacks
MessageCallback = Union[
    Callable[[Message], None],
    Callable[[Message], Awaitable[None]]
]

EventCallback = Union[
    Callable[[str, Any], None],
    Callable[[str, Any], Awaitable[None]]
]

# Connection states
class ConnectionState:
    """Connection state constants."""
    
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


# Event types
class EventType:
    """Event type constants."""
    
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTED = "reconnected"
    ERROR = "error"
    MESSAGE = "message"
    PRESENCE = "presence"
