"""
Manager Discovery Service for OddSockets Python SDK

Resolves the manager endpoint used for worker assignment. The manager itself
handles all routing and load balancing across workers transparently.
"""

import logging
import os
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

#: Hosted OddSockets manager endpoint.
#:
#: This applies only when no manager URL has been configured at all. It is never
#: used to recover from a configured manager that is unreachable: silently
#: redirecting a self-hosted or QA deployment at production would make a broken
#: setup look healthy and would send traffic to the wrong cluster.
DEFAULT_MANAGER_URL = 'https://connect.oddsockets.tyga.network'

#: Environment variable consulted when no manager URL is supplied in code.
MANAGER_URL_ENV_VAR = 'ODDSOCKETS_MANAGER_URL'


def resolve_manager_url(manager_url: Optional[str] = None) -> str:
    """
    Resolve the manager URL to use.

    Precedence: explicit argument, then the ODDSOCKETS_MANAGER_URL environment
    variable, then DEFAULT_MANAGER_URL.

    Args:
        manager_url: Manager URL supplied by the caller (optional)

    Returns:
        The validated manager URL, without trailing slashes

    Raises:
        ValueError: If the resolved value is not an absolute http(s) URL
    """
    candidate = (manager_url or '').strip()

    if not candidate:
        candidate = (os.environ.get(MANAGER_URL_ENV_VAR) or '').strip()

    if not candidate:
        candidate = DEFAULT_MANAGER_URL

    normalised = candidate.rstrip('/')
    parsed = urlparse(normalised)

    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        raise ValueError(f'Invalid managerUrl: {candidate}')

    return normalised


class ManagerDiscovery:
    """
    Manager Discovery Service

    Bound to a single manager endpoint, which handles all routing and load
    balancing transparently.
    """

    def __init__(self, manager_url: Optional[str] = None):
        """
        Args:
            manager_url: Manager URL to use (optional, see resolve_manager_url)
        """
        self.manager_url = resolve_manager_url(manager_url)

    async def discover_manager_url(self, api_key: str) -> str:
        """
        Get the manager URL to use for worker assignment

        Args:
            api_key: The OddSockets API key (not used, kept for compatibility)

        Returns:
            The configured manager URL
        """
        return self.manager_url

    def clear_cache(self) -> None:
        """
        Clear cache (no-op, kept for compatibility)
        """
        # No cache to clear in simplified version
        pass
