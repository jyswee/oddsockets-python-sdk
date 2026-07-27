"""
Channel class for pub/sub messaging

Provides methods for subscribing, publishing, and managing presence
on a specific channel within the OddSockets platform.
"""

import asyncio
import logging
from typing import Optional, Any, List, Dict, Callable, TYPE_CHECKING
from datetime import datetime
import json

from .exceptions import OddSocketsError, ConnectionError

if TYPE_CHECKING:
    from .client import OddSockets

logger = logging.getLogger(__name__)

# Message size limits (industry standard - matches PubNub)
MESSAGE_SIZE_LIMITS = {
    'MAX_MESSAGE_SIZE': 32768,  # 32KB in bytes
    'MAX_MESSAGE_SIZE_KB': 32
}


def validate_message_size(message: Any) -> int:
    """
    Validate message size
    
    Args:
        message: Message to validate
        
    Returns:
        Message size in bytes
        
    Raises:
        ValueError: If message exceeds size limit
    """
    message_str = message if isinstance(message, str) else json.dumps(message)
    message_size = len(message_str.encode('utf-8'))
    
    if message_size > MESSAGE_SIZE_LIMITS['MAX_MESSAGE_SIZE']:
        raise ValueError(
            f"Message size ({round(message_size / 1024)}KB) exceeds maximum allowed size of "
            f"{MESSAGE_SIZE_LIMITS['MAX_MESSAGE_SIZE_KB']}KB. "
            f"This limit matches industry standards (PubNub, Socket.IO) for reliable real-time messaging."
        )
    
    return message_size


class Channel:
    """
    Channel class for pub/sub messaging
    
    Provides methods for subscribing, publishing, and managing presence
    on a specific channel within the OddSockets platform.
    """
    
    def __init__(self, name: str, client: 'OddSockets'):
        """
        Create a Channel instance
        
        Args:
            name: Channel name
            client: Parent OddSockets client
        """
        self.name = name
        self.client = client
        self.subscribed = False
        self.subscribing = False
        self.options = {}
        self.presence = {}
        self.message_history = []
        self.max_history_size = 100
        
        # Event handlers
        self._event_handlers: Dict[str, List] = {}
    
    async def subscribe(self, callback: Callable, options: Optional[Dict] = None):
        """
        Subscribe to the channel
        
        Args:
            callback: Message callback function
            options: Subscription options
                - max_history: Maximum history messages to retain (default: 100)
                - retain_history: Whether to retain message history (default: True)
                - enable_presence: Whether to enable presence tracking (default: False)
        """
        if not callable(callback):
            raise ValueError('Callback function is required')
        
        if self.subscribed or self.subscribing:
            # Add callback to existing subscription
            self.on('message', callback)
            return
        
        if not self.client._is_connected():
            raise ConnectionError('Client is not connected')
        
        self.subscribing = True
        options = options or {}
        self.options = {
            'max_history': options.get('max_history', 100),
            'retain_history': options.get('retain_history', True),
            'enable_presence': options.get('enable_presence', False),
            **options
        }
        
        self.max_history_size = self.options['max_history']
        
        try:
            socket = self.client._get_socket()
            
            # Set up subscription response handler
            subscription_future = asyncio.Future()
            
            async def on_subscribed(data):
                if data.get('channel') == self.name:
                    self.subscribed = True
                    self.subscribing = False
                    self.on('message', callback)
                    self._emit('subscribed', data)
                    if not subscription_future.done():
                        subscription_future.set_result(data)
            
            async def on_error(error):
                self.subscribing = False
                if not subscription_future.done():
                    subscription_future.set_exception(error)
            
            # Register temporary handlers
            socket.on('subscribed', on_subscribed)
            socket.on('error', on_error)
            
            # Send subscription request
            await socket.emit('subscribe', {
                'channel': self.name,
                'options': self.options
            })
            
            # Wait for subscription confirmation with timeout
            try:
                await asyncio.wait_for(subscription_future, timeout=10.0)
            except asyncio.TimeoutError:
                self.subscribing = False
                raise ConnectionError('Subscription timeout')
            finally:
                # Clean up temporary handlers
                pass  # socket.off('subscribed', on_subscribed)
                pass  # socket.off('error', on_error)
                
        except Exception as e:
            self.subscribing = False
            raise ConnectionError(f'Subscription failed: {str(e)}')
    
    async def unsubscribe(self):
        """
        Unsubscribe from the channel
        """
        if not self.subscribed:
            return
        
        if not self.client._is_connected():
            raise ConnectionError('Client is not connected')
        
        try:
            socket = self.client._get_socket()
            
            # Set up unsubscription response handler
            unsubscription_future = asyncio.Future()
            
            async def on_unsubscribed(data):
                if data.get('channel') == self.name:
                    self.subscribed = False
                    self._clear_event_handlers('message')
                    self._emit('unsubscribed', data)
                    if not unsubscription_future.done():
                        unsubscription_future.set_result(data)
            
            async def on_error(error):
                if not unsubscription_future.done():
                    unsubscription_future.set_exception(error)
            
            # Register temporary handlers
            socket.on('unsubscribed', on_unsubscribed)
            socket.on('error', on_error)
            
            # Send unsubscription request
            await socket.emit('unsubscribe', {
                'channel': self.name
            })
            
            # Wait for unsubscription confirmation with timeout
            try:
                await asyncio.wait_for(unsubscription_future, timeout=5.0)
            except asyncio.TimeoutError:
                raise ConnectionError('Unsubscription timeout')
            finally:
                # Clean up temporary handlers
                pass  # socket.off('unsubscribed', on_unsubscribed)
                pass  # socket.off('error', on_error)
                
        except Exception as e:
            raise ConnectionError(f'Unsubscription failed: {str(e)}')
    
    async def publish(self, message: Any, options: Optional[Dict] = None) -> Dict:
        """
        Publish a message to the channel
        
        Args:
            message: Message to publish (string, object, or array)
            options: Publishing options
                - ttl: Time to live in seconds
                - metadata: Additional message metadata
                
        Returns:
            Publication result
        """
        if not self.client._is_connected():
            raise ConnectionError('Client is not connected')
        
        # Validate message size before publishing
        try:
            validate_message_size(message)
        except ValueError as e:
            raise ValueError(str(e))
        
        options = options or {}
        
        try:
            socket = self.client._get_socket()
            
            # Set up publish response handler
            publish_future = asyncio.Future()
            
            async def on_published(data):
                if data.get('channel') == self.name:
                    if not publish_future.done():
                        publish_future.set_result(data)
            
            async def on_error(error):
                if not publish_future.done():
                    publish_future.set_exception(error)
            
            # Register temporary handlers
            socket.on('published', on_published)
            socket.on('error', on_error)
            
            # Send publish request
            await socket.emit('publish', {
                'channel': self.name,
                'message': message,
                'options': options
            })
            
            # Wait for publish confirmation with timeout
            try:
                result = await asyncio.wait_for(publish_future, timeout=10.0)
                return result
            except asyncio.TimeoutError:
                raise ConnectionError('Publish timeout')
            finally:
                # Clean up temporary handlers
                pass  # socket.off('published', on_published)
                pass  # socket.off('error', on_error)
                
        except Exception as e:
            raise ConnectionError(f'Publish failed: {str(e)}')
    
    async def get_history(self, options: Optional[Dict] = None) -> List[Dict]:
        """
        Get message history for the channel
        
        Args:
            options: History options
                - count: Number of messages to retrieve (default: 50)
                - start: Start time (ISO string)
                - end: End time (ISO string)
                
        Returns:
            Message history
        """
        if not self.client._is_connected():
            raise ConnectionError('Client is not connected')
        
        options = options or {}
        
        try:
            socket = self.client._get_socket()
            
            # Set up history response handler
            history_future = asyncio.Future()
            
            async def on_history(data):
                # Only resolve on the explicit get_history RESPONSE (query:True). The
                # worker also emits 'history' as a fire-and-forget on-join snapshot
                # (capped at ~10 local messages, no query flag); without this guard
                # get_history() could resolve with that snapshot instead of the
                # requested count from the shared store. BUG-2026-0727-0012.
                if data.get('channel') == self.name and data.get('query') is True:
                    if not history_future.done():
                        history_future.set_result(data.get('messages', []))
            
            async def on_error(error):
                if not history_future.done():
                    history_future.set_exception(error)
            
            # Register temporary handlers
            socket.on('history', on_history)
            socket.on('error', on_error)
            
            # Send history request
            await socket.emit('get_history', {
                'channel': self.name,
                'count': options.get('count', 50),
                'start': options.get('start'),
                'end': options.get('end')
            })
            
            # Wait for history response with timeout
            try:
                result = await asyncio.wait_for(history_future, timeout=10.0)
                return result
            except asyncio.TimeoutError:
                raise ConnectionError('History request timeout')
            finally:
                # Clean up temporary handlers
                pass  # socket.off('history', on_history)
                pass  # socket.off('error', on_error)
                
        except Exception as e:
            raise ConnectionError(f'History request failed: {str(e)}')
    
    async def get_presence(self) -> Dict:
        """
        Get current presence information
        
        Returns:
            Presence information
        """
        if not self.client._is_connected():
            raise ConnectionError('Client is not connected')
        
        try:
            socket = self.client._get_socket()
            
            # Set up presence response handler
            presence_future = asyncio.Future()
            
            async def on_presence(data):
                if data.get('channel') == self.name:
                    if not presence_future.done():
                        presence_future.set_result(data)
            
            async def on_error(error):
                if not presence_future.done():
                    presence_future.set_exception(error)
            
            # Register temporary handlers
            socket.on('presence', on_presence)
            socket.on('error', on_error)
            
            # Send presence request
            await socket.emit('get_presence', {
                'channel': self.name
            })
            
            # Wait for presence response with timeout
            try:
                result = await asyncio.wait_for(presence_future, timeout=5.0)
                return result
            except asyncio.TimeoutError:
                raise ConnectionError('Presence request timeout')
            finally:
                # Clean up temporary handlers
                pass  # socket.off('presence', on_presence)
                pass  # socket.off('error', on_error)
                
        except Exception as e:
            raise ConnectionError(f'Presence request failed: {str(e)}')
    
    async def update_state(self, state: Dict):
        """
        Update user state
        
        Args:
            state: User state object
        """
        if not self.client._is_connected():
            raise ConnectionError('Client is not connected')
        
        try:
            socket = self.client._get_socket()
            
            # Set up state update response handler
            state_future = asyncio.Future()
            
            async def on_state_updated(data):
                if not state_future.done():
                    state_future.set_result(data)
            
            async def on_error(error):
                if not state_future.done():
                    state_future.set_exception(error)
            
            # Register temporary handlers
            socket.on('state_updated', on_state_updated)
            socket.on('error', on_error)
            
            # Send state update request
            await socket.emit('update_state', {
                'state': state
            })
            
            # Wait for state update confirmation with timeout
            try:
                result = await asyncio.wait_for(state_future, timeout=5.0)
                return result
            except asyncio.TimeoutError:
                raise ConnectionError('State update timeout')
            finally:
                # Clean up temporary handlers
                pass  # socket.off('state_updated', on_state_updated)
                pass  # socket.off('error', on_error)
                
        except Exception as e:
            raise ConnectionError(f'State update failed: {str(e)}')
    
    def is_subscribed(self) -> bool:
        """
        Get channel subscription status
        
        Returns:
            Whether channel is subscribed
        """
        return self.subscribed
    
    def get_name(self) -> str:
        """
        Get channel name
        
        Returns:
            Channel name
        """
        return self.name
    
    def get_presence_map(self) -> Dict:
        """
        Get current presence map
        
        Returns:
            Presence map
        """
        return self.presence.copy()
    
    def get_cached_history(self) -> List:
        """
        Get cached message history
        
        Returns:
            Cached messages
        """
        return self.message_history.copy()
    
    def on(self, event: str, handler: Callable):
        """
        Add event listener
        
        Args:
            event: Event name
            handler: Event handler function
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def off(self, event: str, handler: Optional[Callable] = None):
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
    
    def _clear_event_handlers(self, event: str):
        """
        Clear all event handlers for an event
        
        Args:
            event: Event name
        """
        if event in self._event_handlers:
            del self._event_handlers[event]
    
    def _emit(self, event: str, data=None):
        """
        Emit event to handlers
        
        Args:
            event: Event name
            data: Event data
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
    
    # Internal event handlers called by client
    def _handle_message(self, data):
        """Internal: Handle incoming message"""
        # Add to history if enabled
        if self.options.get('retain_history'):
            self.message_history.append(data)
            
            # Trim history if too large
            if len(self.message_history) > self.max_history_size:
                self.message_history = self.message_history[-self.max_history_size:]
        
        self._emit('message', data)
    
    def _handle_subscribed(self, data):
        """Internal: Handle subscription confirmation"""
        self._emit('subscribed', data)
    
    def _handle_unsubscribed(self, data):
        """Internal: Handle unsubscription confirmation"""
        self._emit('unsubscribed', data)
    
    def _handle_published(self, data):
        """Internal: Handle publish confirmation"""
        self._emit('published', data)
    
    def _handle_presence(self, data):
        """Internal: Handle presence information"""
        # Update presence map
        if data.get('occupants'):
            self.presence.clear()
            for occupant in data['occupants']:
                self.presence[occupant.get('userId')] = occupant
        
        self._emit('presence', data)
    
    def _handle_presence_change(self, data):
        """Internal: Handle presence changes"""
        # Update presence map
        if data.get('action') == 'join':
            user = data.get('user', {})
            self.presence[user.get('userId')] = user
        elif data.get('action') == 'leave':
            user = data.get('user', {})
            user_id = user.get('userId')
            if user_id in self.presence:
                del self.presence[user_id]
        
        self._emit('presence_change', data)
    
    def _handle_history(self, data):
        """Internal: Handle message history"""
        self._emit('history', data)
