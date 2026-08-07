"""
OddSockets Python SDK

Official Python SDK for OddSockets real-time messaging platform.
Provides a simple interface to the OddSockets real-time messaging platform.
Automatically handles manager discovery and Worker load balancing internally.
"""

from .client import OddSockets
from .channel import Channel
from .manager_discovery import (
    ManagerDiscovery,
    resolve_manager_url,
    DEFAULT_MANAGER_URL,
    MANAGER_URL_ENV_VAR,
)
from .enhanced_features import EnhancedFeatures
from .exceptions import (
    OddSocketsError,
    ConnectionError,
    AuthenticationError,
)

# Version info
__version__ = "1.0.0"

# Convenience factory function
def create(config):
    """
    Create an OddSockets client
    
    Args:
        config: Configuration dictionary with keys:
            - api_key: Your OddSockets API key (required)
            - manager_url: Manager URL (optional, falls back to the
              ODDSOCKETS_MANAGER_URL environment variable and then to the
              hosted endpoint)
            - user_id: User ID (optional, defaults to API key's user)
            - options: Additional connection options (optional)
    
    Returns:
        OddSockets client instance
    """
    return OddSockets(config)

__all__ = [
    # Core classes
    "OddSockets",
    "Channel",
    "EnhancedFeatures",
    
    # Manager discovery
    "ManagerDiscovery",
    "resolve_manager_url",
    "DEFAULT_MANAGER_URL",
    "MANAGER_URL_ENV_VAR",

    # Factory functions
    "create",
    
    # Exceptions
    "OddSocketsError",
    "ConnectionError", 
    "AuthenticationError",
    
    # Version
    "__version__",
]
