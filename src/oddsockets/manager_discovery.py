"""
Manager Discovery Service for OddSockets Python SDK

Simple manager discovery that always connects to the main manager endpoint
which handles all routing and load balancing transparently.
"""

import asyncio
import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ManagerDiscovery:
    """
    Simple Manager Discovery Service
    
    Always connects to the main manager endpoint which handles
    all routing and load balancing transparently.
    """
    
    def __init__(self):
        self.manager_url = 'https://manager1.oddsockets.tyga.network'
    
    async def discover_manager_url(self, api_key: str) -> str:
        """
        Get the manager URL (always returns the main endpoint)
        
        Args:
            api_key: The OddSockets API key (not used, kept for compatibility)
            
        Returns:
            The manager URL
        """
        return self.manager_url
    
    def clear_cache(self) -> None:
        """
        Clear cache (no-op, kept for compatibility)
        """
        # No cache to clear in simplified version
        pass


# Singleton instance
manager_discovery = ManagerDiscovery()
