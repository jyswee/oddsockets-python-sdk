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

from .manager_discovery import ManagerDiscovery
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

    # Enhanced-feature broadcast events the worker delivers to other members of a
    # room. Forwarded onto the client event surface so apps can subscribe with
    # client.on(name).
    ENHANCED_BROADCAST_EVENTS = [
        'reaction_added', 'reaction_removed',
        'user_typing', 'user_stopped_typing',
        'user_read', 'unread_count_updated', 'all_marked_read',
        'thread_reply', 'thread_subscribed', 'thread_followed', 'thread_unfollowed', 'thread_read_updated',
        'message_edited', 'message_deleted', 'message_pinned', 'message_unpinned',
        'user_status_changed', 'custom_status_updated', 'custom_status_cleared', 'dnd_status_changed', 'status_updated',
        'file_upload_completed', 'file_upload_progress', 'file_upload_failed',
        'dm_created', 'dm_received',
        'notification', 'notification_read', 'all_notifications_read', 'notifications_cleared',
        'channel_created', 'channel_updated', 'user_invited', 'user_joined_channel', 'user_left_channel', 'user_removed',
    ]

    def __init__(self, config: Dict[str, Any]):
        """
        Create an OddSockets client
        
        Args:
            config: Configuration dictionary with keys:
                - api_key: Your OddSockets API key (required unless token_provider
                  is supplied)
                - token_provider: Async callable returning a fresh minted realtime
                  token, used INSTEAD of api_key by game clients that exchange a
                  player JWT for a short-lived scoped token via the OddSockets
                  /v1/token front door. Called before every (re)connect and again
                  shortly before the token expires. May return a token string or a
                  dict {token, expires_at/expiresAt, exp, base_url}.
                  (FEAT-2026-0824-0040)
                - token_refresh_lead_ms: Refresh a minted token this many
                  milliseconds before it expires (optional, default 120000)
                - manager_url: Manager URL (optional, falls back to the
                  ODDSOCKETS_MANAGER_URL environment variable and then to the
                  hosted endpoint)
                - user_id: User ID (optional, defaults to API key's user)
                - options: Additional connection options (optional)
        """
        token_provider = config.get('token_provider') if config else None
        # Either a static API key OR an async token_provider callback is required.
        # Game clients (front-door auth) carry no API key. (FEAT-2026-0824-0040)
        if not config or (not config.get('api_key') and not callable(token_provider)):
            raise ValueError('Either an API key or a token_provider callback is required')

        # Resolved here so an invalid manager URL is rejected up front rather
        # than quietly sending traffic somewhere the caller did not ask for.
        self.manager_discovery = ManagerDiscovery(config.get('manager_url'))

        self.config = {
            'api_key': config.get('api_key'),
            'token_provider': token_provider,
            'token_refresh_lead_ms': config.get('token_refresh_lead_ms', 120000),
            'manager_url': self.manager_discovery.manager_url,
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
        # Minted-token state (token mode only). (FEAT-2026-0824-0040)
        self._token = None
        self._token_expires_at = None  # epoch milliseconds
        self._token_refresh_task = None
        
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
            # Step 0: In token mode, mint/refresh a realtime token before every
            # (re)connect so the worker assignment and handshake carry a fresh
            # credential rather than an API key. (FEAT-2026-0824-0040)
            if self._is_token_mode():
                await self._resolve_token()

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

        # Stop any pending minted-token refresh. (FEAT-2026-0824-0040)
        if self._token_refresh_task:
            self._token_refresh_task.cancel()
            self._token_refresh_task = None

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
            # The configured manager is used as-is; there is no alternative
            # endpoint to fall back to if it is unreachable.
            manager_url = await self.manager_discovery.discover_manager_url(self.config['api_key'])

            # In token mode present the minted token (not an API key) to the
            # manager. (FEAT-2026-0824-0040 / FEAT-2026-0824-0041)
            params = {
                'userId': self.config.get('user_id') or self.client_identifier,
                'clientIdentifier': self.client_identifier
            }
            if self._is_token_mode():
                params['token'] = self._token
            else:
                params['apiKey'] = self.config['api_key']
            
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
                        'manager_url': manager_url  # Manager the worker was assigned by
                    })

        except aiohttp.ClientConnectorError as error:
            # Classified on the exception type rather than its wording: aiohttp
            # raises this for refused connections and name resolution failures,
            # and the message text differs per platform and library version.
            raise ConnectionError(
                'Manager is offline. Cannot assign worker without session stickiness.'
            ) from error
    
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
        
        # Connect with authentication. In token mode present the minted token at
        # the Socket.IO handshake; the worker verifies auth.token
        # (FEAT-2026-0824-0039). Otherwise send the API key. (FEAT-2026-0824-0040)
        if self._is_token_mode():
            auth_data = {
                'token': self._token,
                'userId': self.config.get('user_id')
            }
        else:
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

        # Forward enhanced-feature broadcasts to the client event surface so apps can
        # listen with client.on('reaction_added', handler), etc. These are the events
        # the worker broadcasts to OTHER members of a room; the request/response acks
        # consumed by EnhancedFeatures methods are intentionally not in this list.
        def _make_forwarder(event_name):
            async def _forward(data=None):
                self._emit(event_name, data)
            return _forward

        for event in OddSockets.ENHANCED_BROADCAST_EVENTS:
            self.socket.on(event, _make_forwarder(event))

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
        # Create a consistent identifier based on API key and user ID. Token-mode
        # clients carry no API key, so fall back to a stable seed.
        # (FEAT-2026-0824-0040)
        base_id = self.config.get('user_id') or 'default'
        seed = self.config.get('api_key') or 'token-client'
        api_key_hash = self._hash_string(seed)
        return f"{api_key_hash}_{base_id}"

    def _is_token_mode(self) -> bool:
        """Internal: is this client authenticating with a minted token vs an API key?"""
        return callable(self.config.get('token_provider'))

    async def _resolve_token(self):
        """
        Internal: call the configured token_provider, cache the fresh token and
        its expiry, and schedule a refresh ahead of expiry. (FEAT-2026-0824-0040)
        """
        provider = self.config['token_provider']
        result = provider()
        if asyncio.iscoroutine(result):
            result = await result

        if not result:
            raise ConnectionError('token_provider returned no token')

        # Accept either a bare token string or a dict {token, expires_at/expiresAt,
        # exp, base_url}, mirroring the OddSockets /v1/token mint response shape.
        expires_at_ms = None
        if isinstance(result, str):
            token = result
        else:
            token = result.get('token')
            raw_expires = result.get('expires_at', result.get('expiresAt'))
            if raw_expires is not None:
                if isinstance(raw_expires, (int, float)):
                    # < 1e12 => epoch seconds, else already milliseconds.
                    expires_at_ms = raw_expires * 1000 if raw_expires < 1e12 else raw_expires
                else:
                    expires_at_ms = self._parse_iso_ms(raw_expires)
            elif isinstance(result.get('exp'), (int, float)):
                expires_at_ms = result['exp'] * 1000

        if not token or not isinstance(token, str):
            raise ConnectionError('token_provider returned an invalid token')

        # Fall back to the JWT's own exp claim if the provider gave no expiry.
        if expires_at_ms is None:
            expires_at_ms = self._expiry_from_jwt(token)

        self._token = token
        self._token_expires_at = expires_at_ms
        self._schedule_token_refresh()

    @staticmethod
    def _parse_iso_ms(value: str):
        """Internal: parse an ISO-8601 timestamp to epoch milliseconds, or None."""
        try:
            text = value.strip()
            if text.endswith('Z'):
                text = text[:-1] + '+00:00'
            return int(datetime.fromisoformat(text).timestamp() * 1000)
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def _expiry_from_jwt(token: str):
        """
        Internal: extract exp (epoch ms) from a JWT payload without verifying it.
        Returns None on failure. (FEAT-2026-0824-0040)
        """
        try:
            import base64
            part = token.split('.')[1]
            padded = part + '=' * (-len(part) % 4)
            payload = json.loads(base64.urlsafe_b64decode(padded))
            exp = payload.get('exp')
            return exp * 1000 if isinstance(exp, (int, float)) else None
        except Exception:
            return None

    def _schedule_token_refresh(self):
        """
        Internal: schedule a task that re-mints the token shortly before it
        expires and swaps it into the live handshake auth in place, with no
        reconnect. Emits 'token_refreshed' on success, 'error' on failure.
        (FEAT-2026-0824-0040)
        """
        # Cancel any pending refresh, but never the task we may be running inside
        # (the refresh loop re-resolves and re-schedules from within itself).
        try:
            current = asyncio.current_task()
        except RuntimeError:
            current = None
        if self._token_refresh_task and self._token_refresh_task is not current:
            self._token_refresh_task.cancel()
        self._token_refresh_task = None

        if not self._token_expires_at:
            return

        lead = self.config['token_refresh_lead_ms']
        now_ms = datetime.now().timestamp() * 1000
        delay = (self._token_expires_at - now_ms - lead) / 1000
        if delay <= 0:
            return  # Too close to expiry to usefully schedule; next connect re-resolves.

        self._token_refresh_task = asyncio.create_task(self._token_refresh_loop(delay))

    async def _token_refresh_loop(self, delay: float):
        """Internal: sleep then refresh the minted token in place. (FEAT-2026-0824-0040)"""
        try:
            await asyncio.sleep(delay)
            await self._resolve_token()
            self._emit('token_refreshed', {'expires_at': self._token_expires_at})
        except asyncio.CancelledError:
            raise
        except Exception as error:
            self._emit('error', error)
    
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
