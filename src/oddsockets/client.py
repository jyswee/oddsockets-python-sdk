"""
OddSockets Python SDK - Main Client Implementation

Provides a simple interface to the OddSockets real-time messaging platform.
Automatically handles manager discovery and Worker load balancing internally.
"""

import asyncio
import aiohttp
import socketio
import logging
import hashlib
from typing import Dict, Optional, Any, List
from datetime import datetime
import json

from .manager_discovery import manager_discovery
from .channel import Channel
from .exceptions import OddSocketsError, ConnectionError, AuthenticationError
from .enhanced_features import EnhancedFeatures

logger = logging.getLogger(__name__)


class OddSockets:
    """
    OddSockets Python SDK
    
    Provides a simple interface to the OddSockets real-time messaging platform.
    Automatically handles manager discovery and Worker load balancing internally.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Create an OddSockets client
        
        Args:
            config: Configuration dictionary with keys:
                - api_key: Your OddSockets API key (required)
                - user_id: User ID (optional, defaults to API key's user)
                - options: Additional connection options (optional)
        """
        if not config or not config.get('api_key'):
            raise ValueError('API key is required')
        
        self.config = {
            'api_key': config['api_key'],
            'user_id': config.get('user_id'),
            'options': config.get('options', {})
        }
        
        self.socket = None
        self.worker_url = None
        self.worker_id = None
        self.channels: Dict[str, Channel] = {}
        self.connection_state = 'disconnected'  # disconnected, connecting, connected, reconnecting
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1000  # Start with 1 second
        self.client_identifier = self._generate_client_identifier()
        self.session_info = None
        
        # Initialize enhanced features (67 new Slack-like events)
        self.enhanced = EnhancedFeatures(self)
        
        # Event handlers
        self._event_handlers: Dict[str, List] = {}
        
        # Auto-connect by default
        if config.get('auto_connect', True):
            asyncio.create_task(self.connect())
    
    async def connect(self):
        """
        Connect to the OddSockets platform
        Handles the Manager → Worker assignment internally
        """
        if self.connection_state in ['connecting', 'connected']:
            return
        
        self.connection_state = 'connecting'
        self._emit('connecting')
        
        try:
            # Step 1: Get worker assignment from manager
            await self._get_worker_assignment()
            
            # Step 2: Connect to assigned worker
            await self._connect_to_worker()
            
            self.connection_state = 'connected'
            self.reconnect_attempts = 0
            self.reconnect_delay = 1000
            self._emit('connected')
            
        except Exception as error:
            self.connection_state = 'disconnected'
            self._emit('error', error)
            
            # Auto-reconnect with exponential backoff
            if self.reconnect_attempts < self.max_reconnect_attempts:
                await self._schedule_reconnect()
            else:
                self._emit('max_reconnect_attempts_reached')
    
    async def disconnect(self):
        """
        Disconnect from the platform
        """
        self.connection_state = 'disconnected'
        
        if self.socket:
            await self.socket.disconnect()
            self.socket = None
        
        self.worker_url = None
        self.worker_id = None
        self._emit('disconnected')
    
    def channel(self, channel_name: str) -> Channel:
        """
        Get or create a channel
        
        Args:
            channel_name: Name of the channel
            
        Returns:
            Channel instance
        """
        if not channel_name or not isinstance(channel_name, str):
            raise ValueError('Channel name must be a non-empty string')
        
        if channel_name not in self.channels:
            channel = Channel(channel_name, self)
            self.channels[channel_name] = channel
        
        return self.channels[channel_name]
    
    def get_state(self) -> str:
        """
        Get current connection state
        
        Returns:
            Connection state string
        """
        return self.connection_state
    
    def get_worker_info(self) -> Optional[Dict]:
        """
        Get assigned worker information
        
        Returns:
            Worker info dict or None
        """
        if not self.worker_id or not self.worker_url:
            return None
        
        return {
            'worker_id': self.worker_id,
            'worker_url': self.worker_url
        }
    
    async def publish_bulk(self, messages: List[Dict]) -> List[Dict]:
        """
        Publish multiple messages at once
        
        Args:
            messages: Array of message objects with {channel, message, options?} structure
            
        Returns:
            Array of publish results
        """
        if not isinstance(messages, list):
            raise ValueError('Messages must be an array')
        
        if not self._is_connected():
            raise ConnectionError('Not connected to OddSockets')
        
        results = []
        
        for msg in messages:
            try:
                if not msg.get('channel') or 'message' not in msg:
                    results.append({
                        'success': False,
                        'error': 'Missing channel or message'
                    })
                    continue
                
                channel = self.channel(msg['channel'])
                result = await channel.publish(msg['message'], msg.get('options', {}))
                results.append({
                    'success': True,
                    'result': result
                })
                
            except Exception as error:
                results.append({
                    'success': False,
                    'error': str(error)
                })
        
        return results
    
    async def _get_worker_assignment(self):
        """
        Internal: Get worker assignment from manager
        """
        try:
            # Discover the optimal manager URL automatically
            manager_url = await manager_discovery.discover_manager_url(self.config['api_key'])
            
            params = {
                'apiKey': self.config['api_key'],
                'userId': self.config.get('user_id') or self.client_identifier,
                'clientIdentifier': self.client_identifier
            }
            
            headers = {
                'User-Agent': 'OddSockets-Python-SDK/1.0.0'
            }
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    f"{manager_url}/api/cluster/select-worker",
                    params=params,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise ConnectionError(f"Worker assignment failed: {response.status}")
                    
                    data = await response.json()
                    
                    if not data or not data.get('url'):
                        raise ConnectionError('Invalid worker assignment response')
                    
                    self.worker_url = data['url']
                    self.worker_id = data.get('workerId')
                    self.session_info = data.get('session')
                    
                    self._emit('worker_assigned', {
                        'worker_id': self.worker_id,
                        'worker_url': self.worker_url,
                        'session': self.session_info,
                        'client_identifier': self.client_identifier,
                        'manager_url': manager_url  # Include discovered manager URL for debugging
                    })
                    
        except Exception as error:
            # If manager is offline, try fallback logic
            if 'Connection refused' in str(error) or 'Name or service not known' in str(error):
                raise ConnectionError('Manager is offline. Cannot assign worker without session stickiness.')
            raise error
    
    async def _connect_to_worker(self):
        """
        Internal: Connect to assigned worker
        """
        if not self.worker_url:
            raise ConnectionError('No worker URL available')
        
        # Create Socket.IO client
        self.socket = socketio.AsyncClient()
        
        # Set up event handlers
        self._setup_socket_event_handlers()
        
        # Connect with authentication
        auth_data = {
            'apiKey': self.config['api_key'],
            'userId': self.config.get('user_id')
        }
        
        try:
            await self.socket.connect(
                self.worker_url,
                auth=auth_data,
                transports=['websocket', 'polling'],
                wait_timeout=10
            )
        except Exception as error:
            raise ConnectionError(f"Failed to connect to worker: {str(error)}")
    
    def _setup_socket_event_handlers(self):
        """
        Internal: Setup socket event handlers
        """
        if not self.socket:
            return
        
        @self.socket.event
        async def disconnect(reason):
            self.connection_state = 'disconnected'
            self._emit('disconnected', reason)
            
            # Auto-reconnect unless manually disconnected
            if reason != 'disconnect':
                await self._schedule_reconnect()
        
        @self.socket.event
        async def connect_error(error):
            self._emit('error', error)
        
        # Forward channel-related events to appropriate channels
        @self.socket.event
        async def message(data):
            channel = self.channels.get(data.get('channel'))
            if channel:
                channel._handle_message(data)
        
        @self.socket.event
        async def subscribed(data):
            channel = self.channels.get(data.get('channel'))
            if channel:
                channel._handle_subscribed(data)
        
        @self.socket.event
        async def unsubscribed(data):
            channel = self.channels.get(data.get('channel'))
            if channel:
                channel._handle_unsubscribed(data)
        
        @self.socket.event
        async def published(data):
            channel = self.channels.get(data.get('channel'))
            if channel:
                channel._handle_published(data)
        
        @self.socket.event
        async def presence(data):
            channel = self.channels.get(data.get('channel'))
            if channel:
                channel._handle_presence(data)
        
        @self.socket.event
        async def presence_change(data):
            channel = self.channels.get(data.get('channel'))
            if channel:
                channel._handle_presence_change(data)
        
        @self.socket.event
        async def history(data):
            channel = self.channels.get(data.get('channel'))
            if channel:
                channel._handle_history(data)
    
    async def _schedule_reconnect(self):
        """
        Internal: Schedule reconnection with exponential backoff
        """
        if self.connection_state == 'connected':
            return
        
        self.connection_state = 'reconnecting'
        self.reconnect_attempts += 1
        
        delay = min(self.reconnect_delay * (2 ** (self.reconnect_attempts - 1)), 30000) / 1000
        
        self._emit('reconnecting', {
            'attempt': self.reconnect_attempts,
            'max_attempts': self.max_reconnect_attempts,
            'delay': delay
        })
        
        await asyncio.sleep(delay)
        
        if self.connection_state == 'reconnecting':
            await self.connect()
    
    def _get_socket(self):
        """
        Internal: Get socket instance (for Channel class)
        """
        return self.socket
    
    def _is_connected(self) -> bool:
        """
        Internal: Check if connected (for Channel class)
        """
        return self.connection_state == 'connected' and self.socket and self.socket.connected
    
    def _generate_client_identifier(self) -> str:
        """
        Internal: Generate consistent client identifier for session stickiness
        """
        # Create a consistent identifier based on API key and user ID
        base_id = self.config.get('user_id', 'default')
        api_key_hash = self._hash_string(self.config['api_key'])
        return f"{api_key_hash}_{base_id}"
    
    def _hash_string(self, string: str) -> str:
        """
        Internal: Simple hash function for API key
        """
        return hashlib.md5(string.encode()).hexdigest()[:8]
    
    def get_client_identifier(self) -> str:
        """
        Get client identifier used for session stickiness
        
        Returns:
            Client identifier string
        """
        return self.client_identifier
    
    def get_session_info(self) -> Optional[Dict]:
        """
        Get session information
        
        Returns:
            Session info dict or None
        """
        return self.session_info
    
    def on(self, event: str, handler):
        """
        Add event listener
        
        Args:
            event: Event name
            handler: Event handler function
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def off(self, event: str, handler=None):
        """
        Remove event listener
        
        Args:
            event: Event name
            handler: Specific handler to remove (optional)
        """
        if event not in self._event_handlers:
            return
        
        if handler is None:
            del self._event_handlers[event]
        else:
            try:
                self._event_handlers[event].remove(handler)
            except ValueError:
                pass
    
    def _emit(self, event: str, data=None):
        """
        Internal: Emit event to handlers
        """
        if event not in self._event_handlers:
            return
        
        for handler in self._event_handlers[event]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(data))
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Error in event handler for {event}: {e}")
