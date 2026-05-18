"""
Enhanced Features for OddSockets Python SDK
Provides methods for all 67 new Slack-like events
"""

from typing import Dict, List, Any, Optional
import asyncio


class EnhancedFeatures:
    """
    Enhanced features providing 67 new Slack-like events for OddSockets.
    Access via client.enhanced property.
    """

    def __init__(self, client):
        """
        Initialize enhanced features.
        
        Args:
            client: The OddSockets client instance
        """
        self.client = client

    def _get_socket(self):
        """Get socket instance, raising error if not connected."""
        if not self.client._is_connected():
            raise RuntimeError("Not connected to OddSockets")
        return self.client.sio

    # ==================== THREAD EVENTS ====================

    async def thread_reply(self, channel: str, parent_message_id: str, message: str,
                          user_id: str, user_name: str) -> Dict[str, Any]:
        """
        Reply to a message in a thread.
        
        Args:
            channel: Channel name
            parent_message_id: ID of the parent message
            message: Reply message content
            user_id: User ID
            user_name: User name
            
        Returns:
            Dict containing the reply result
        """
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_success(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'thread_reply':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('thread_reply_success', on_success)
        socket.once('error', on_error)
        
        await socket.emit('thread_reply', {
            'channel': channel,
            'parentMessageId': parent_message_id,
            'message': message,
            'userId': user_id,
            'userName': user_name
        })
        
        return await future

    async def get_thread(self, thread_id: str) -> Dict[str, Any]:
        """Get thread with all replies."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_data(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'get_thread':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('thread_data', on_data)
        socket.once('error', on_error)
        
        await socket.emit('get_thread', {'threadId': thread_id})
        
        return await future

    async def subscribe_thread(self, thread_id: str, user_id: str) -> Dict[str, Any]:
        """Subscribe to thread updates."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_subscribed(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'subscribe_thread':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('thread_subscribed', on_subscribed)
        socket.once('error', on_error)
        
        await socket.emit('subscribe_thread', {'threadId': thread_id, 'userId': user_id})
        
        return await future

    async def mark_thread_read(self, thread_id: str, user_id: str):
        """Mark thread as read."""
        socket = self._get_socket()
        await socket.emit('mark_thread_read', {'threadId': thread_id, 'userId': user_id})

    async def follow_thread(self, thread_id: str, user_id: str):
        """Follow a thread."""
        socket = self._get_socket()
        await socket.emit('follow_thread', {'threadId': thread_id, 'userId': user_id})

    async def unfollow_thread(self, thread_id: str, user_id: str):
        """Unfollow a thread."""
        socket = self._get_socket()
        await socket.emit('unfollow_thread', {'threadId': thread_id, 'userId': user_id})

    # ==================== REACTION EVENTS ====================

    async def add_reaction(self, message_id: str, channel: str, emoji: str,
                          user_id: str, user_name: str):
        """Add reaction to a message."""
        socket = self._get_socket()
        await socket.emit('add_reaction', {
            'messageId': message_id,
            'channel': channel,
            'emoji': emoji,
            'userId': user_id,
            'userName': user_name
        })

    async def remove_reaction(self, message_id: str, channel: str, emoji: str, user_id: str):
        """Remove reaction from a message."""
        socket = self._get_socket()
        await socket.emit('remove_reaction', {
            'messageId': message_id,
            'channel': channel,
            'emoji': emoji,
            'userId': user_id
        })

    async def get_reactions(self, message_id: str) -> Dict[str, Any]:
        """Get all reactions for a message."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_reactions(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'get_reactions':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('message_reactions', on_reactions)
        socket.once('error', on_error)
        
        await socket.emit('get_reactions', {'messageId': message_id})
        
        return await future

    # ==================== READ RECEIPT EVENTS ====================

    async def mark_read(self, message_id: str, channel: str, user_id: str, user_name: str):
        """Mark message as read."""
        socket = self._get_socket()
        await socket.emit('mark_read', {
            'messageId': message_id,
            'channel': channel,
            'userId': user_id,
            'userName': user_name
        })

    async def get_unread_counts(self, user_id: str, channels: List[str]) -> Dict[str, Any]:
        """Get unread counts for channels."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_counts(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'get_unread_counts':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('unread_counts', on_counts)
        socket.once('error', on_error)
        
        await socket.emit('get_unread_counts', {'userId': user_id, 'channels': channels})
        
        return await future

    async def mark_all_read(self, channel: str, user_id: str):
        """Mark all messages in channel as read."""
        socket = self._get_socket()
        await socket.emit('mark_all_read', {'channel': channel, 'userId': user_id})

    # ==================== CHANNEL EVENTS ====================

    async def create_channel(self, name: str, channel_type: str, description: str,
                            topic: str, created_by: str, created_by_name: str,
                            members: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Create a new channel."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_success(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'create_channel':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('channel_create_success', on_success)
        socket.once('error', on_error)
        
        await socket.emit('create_channel', {
            'name': name,
            'type': channel_type,
            'description': description,
            'topic': topic,
            'createdBy': created_by,
            'createdByName': created_by_name,
            'members': members or []
        })
        
        return await future

    async def update_channel(self, channel_id: str, updates: Dict[str, Any], user_id: str):
        """Update channel details."""
        socket = self._get_socket()
        await socket.emit('update_channel', {
            'channelId': channel_id,
            'updates': updates,
            'userId': user_id
        })

    async def archive_channel(self, channel_id: str, user_id: str):
        """Archive a channel."""
        socket = self._get_socket()
        await socket.emit('archive_channel', {'channelId': channel_id, 'userId': user_id})

    async def invite_to_channel(self, channel_id: str, invited_user_id: str,
                               invited_user_name: str, invited_by: str):
        """Invite user to channel."""
        socket = self._get_socket()
        await socket.emit('invite_to_channel', {
            'channelId': channel_id,
            'invitedUserId': invited_user_id,
            'invitedUserName': invited_user_name,
            'invitedBy': invited_by
        })

    async def remove_from_channel(self, channel_id: str, removed_user_id: str, removed_by: str):
        """Remove user from channel."""
        socket = self._get_socket()
        await socket.emit('remove_from_channel', {
            'channelId': channel_id,
            'removedUserId': removed_user_id,
            'removedBy': removed_by
        })

    async def join_channel(self, channel_id: str, user_id: str, user_name: str):
        """Join a public channel."""
        socket = self._get_socket()
        await socket.emit('join_channel', {
            'channelId': channel_id,
            'userId': user_id,
            'userName': user_name
        })

    async def leave_channel(self, channel_id: str, user_id: str):
        """Leave a channel."""
        socket = self._get_socket()
        await socket.emit('leave_channel', {'channelId': channel_id, 'userId': user_id})

    async def get_channel_members(self, channel_id: str) -> Dict[str, Any]:
        """Get channel members."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_members(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'get_channel_members':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('channel_members', on_members)
        socket.once('error', on_error)
        
        await socket.emit('get_channel_members', {'channelId': channel_id})
        
        return await future

    # ==================== DIRECT MESSAGE EVENTS ====================

    async def create_dm(self, user_ids: List[str], dm_type: str = '1-on-1',
                       group_name: Optional[str] = None) -> Dict[str, Any]:
        """Create or get DM conversation."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_success(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'create_dm':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('dm_create_success', on_success)
        socket.once('error', on_error)
        
        payload = {'userIds': user_ids, 'type': dm_type}
        if group_name:
            payload['groupName'] = group_name
        
        await socket.emit('create_dm', payload)
        
        return await future

    async def send_dm(self, conversation_id: str, message: str, user_id: str, user_name: str):
        """Send direct message."""
        socket = self._get_socket()
        await socket.emit('send_dm', {
            'conversationId': conversation_id,
            'message': message,
            'userId': user_id,
            'userName': user_name
        })

    async def get_dm_conversations(self, user_id: str,
                                   include_archived: bool = False) -> Dict[str, Any]:
        """Get user's DM conversations."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_conversations(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'get_dm_conversations':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('dm_conversations', on_conversations)
        socket.once('error', on_error)
        
        await socket.emit('get_dm_conversations', {
            'userId': user_id,
            'includeArchived': include_archived
        })
        
        return await future

    # ==================== NOTIFICATION EVENTS ====================

    async def subscribe_notifications(self, user_id: str):
        """Subscribe to user notifications."""
        socket = self._get_socket()
        await socket.emit('subscribe_notifications', {'userId': user_id})

    async def mark_notification_read(self, notification_id: str, user_id: str):
        """Mark notification as read."""
        socket = self._get_socket()
        await socket.emit('mark_notification_read', {
            'notificationId': notification_id,
            'userId': user_id
        })

    async def mark_all_notifications_read(self, user_id: str):
        """Mark all notifications as read."""
        socket = self._get_socket()
        await socket.emit('mark_all_notifications_read', {'userId': user_id})

    async def clear_notifications(self, user_id: str):
        """Clear all notifications."""
        socket = self._get_socket()
        await socket.emit('clear_notifications', {'userId': user_id})

    async def get_notifications(self, user_id: str, limit: int = 50,
                               status: str = 'all') -> Dict[str, Any]:
        """Get user notifications."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_notifications(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'get_notifications':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('notifications_data', on_notifications)
        socket.once('error', on_error)
        
        await socket.emit('get_notifications', {
            'userId': user_id,
            'limit': limit,
            'status': status
        })
        
        return await future

    # ==================== FILE UPLOAD EVENTS ====================

    async def start_file_upload(self, file_name: str, file_size: int, mime_type: str,
                                channel: str, user_id: str, user_name: str) -> Dict[str, Any]:
        """Start file upload."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_started(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'start_file_upload':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('upload_started', on_started)
        socket.once('error', on_error)
        
        await socket.emit('start_file_upload', {
            'fileName': file_name,
            'fileSize': file_size,
            'mimeType': mime_type,
            'channel': channel,
            'userId': user_id,
            'userName': user_name
        })
        
        return await future

    async def upload_progress(self, upload_id: str, bytes_uploaded: int,
                             channel: Optional[str] = None):
        """Update upload progress."""
        socket = self._get_socket()
        payload = {'uploadId': upload_id, 'bytesUploaded': bytes_uploaded}
        if channel:
            payload['channel'] = channel
        await socket.emit('upload_progress', payload)

    async def upload_complete(self, upload_id: str, file_id: str, storage_info: Dict[str, Any],
                             channel: Optional[str] = None, message_id: Optional[str] = None):
        """Complete file upload."""
        socket = self._get_socket()
        payload = {
            'uploadId': upload_id,
            'fileId': file_id,
            'storageInfo': storage_info
        }
        if channel:
            payload['channel'] = channel
        if message_id:
            payload['messageId'] = message_id
        await socket.emit('upload_complete', payload)

    # ==================== PRESENCE EVENTS ====================

    async def set_status(self, user_id: str, status: str):
        """Set user status (online, away, dnd, offline)."""
        socket = self._get_socket()
        await socket.emit('set_status', {'userId': user_id, 'status': status})

    async def set_custom_status(self, user_id: str, emoji: str, text: str,
                               expires_at: Optional[str] = None):
        """Set custom status."""
        socket = self._get_socket()
        payload = {'userId': user_id, 'emoji': emoji, 'text': text}
        if expires_at:
            payload['expiresAt'] = expires_at
        await socket.emit('set_custom_status', payload)

    async def clear_custom_status(self, user_id: str):
        """Clear custom status."""
        socket = self._get_socket()
        await socket.emit('clear_custom_status', {'userId': user_id})

    async def set_dnd(self, user_id: str, until: Optional[str] = None):
        """Enable Do Not Disturb."""
        socket = self._get_socket()
        payload = {'userId': user_id}
        if until:
            payload['until'] = until
        await socket.emit('set_dnd', payload)

    async def clear_dnd(self, user_id: str):
        """Disable Do Not Disturb."""
        socket = self._get_socket()
        await socket.emit('clear_dnd', {'userId': user_id})

    async def start_typing(self, user_id: str, channel: str):
        """Start typing indicator."""
        socket = self._get_socket()
        await socket.emit('start_typing', {'userId': user_id, 'channel': channel})

    async def stop_typing(self, user_id: str, channel: str):
        """Stop typing indicator."""
        socket = self._get_socket()
        await socket.emit('stop_typing', {'userId': user_id, 'channel': channel})

    async def get_user_presence(self, user_ids: List[str]) -> Dict[str, Any]:
        """Get user presence information."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_presence(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'get_user_presence':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('user_presence_data', on_presence)
        socket.once('error', on_error)
        
        await socket.emit('get_user_presence', {'userIds': user_ids})
        
        return await future

    # ==================== MESSAGE EDITING EVENTS ====================

    async def edit_message(self, message_id: str, channel: str, new_content: str, user_id: str):
        """Edit a message."""
        socket = self._get_socket()
        await socket.emit('edit_message', {
            'messageId': message_id,
            'channel': channel,
            'newContent': new_content,
            'userId': user_id
        })

    async def delete_message(self, message_id: str, channel: str, user_id: str):
        """Delete a message."""
        socket = self._get_socket()
        await socket.emit('delete_message', {
            'messageId': message_id,
            'channel': channel,
            'userId': user_id
        })

    async def pin_message(self, message_id: str, channel: str, user_id: str):
        """Pin message to channel."""
        socket = self._get_socket()
        await socket.emit('pin_message', {
            'messageId': message_id,
            'channel': channel,
            'userId': user_id
        })

    async def unpin_message(self, message_id: str, channel: str, user_id: str):
        """Unpin message from channel."""
        socket = self._get_socket()
        await socket.emit('unpin_message', {
            'messageId': message_id,
            'channel': channel,
            'userId': user_id
        })

    async def get_pinned_messages(self, channel: str) -> Dict[str, Any]:
        """Get pinned messages in channel."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_pinned(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'get_pinned_messages':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('pinned_messages', on_pinned)
        socket.once('error', on_error)
        
        await socket.emit('get_pinned_messages', {'channel': channel})
        
        return await future

    # ==================== SEARCH EVENTS ====================

    async def search_messages(self, query: str, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """Search messages across all channels."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_results(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'search_messages':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('search_results', on_results)
        socket.once('error', on_error)
        
        await socket.emit('search_messages', {
            'query': query,
            'limit': limit,
            'userId': user_id
        })
        
        return await future

    async def filter_messages(self, **filters) -> Dict[str, Any]:
        """Filter messages by criteria."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_results(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'filter_messages':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('filter_results', on_results)
        socket.once('error', on_error)
        
        await socket.emit('filter_messages', filters)
        
        return await future

    async def search_in_channel(self, channel: str, query: str, limit: int = 50) -> Dict[str, Any]:
        """Search within specific channel."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_results(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'search_in_channel':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('channel_search_results', on_results)
        socket.once('error', on_error)
        
        await socket.emit('search_in_channel', {
            'channel': channel,
            'query': query,
            'limit': limit
        })
        
        return await future

    async def search_by_user(self, user_id: str, query: Optional[str] = None,
                            limit: int = 50) -> Dict[str, Any]:
        """Search messages by user."""
        socket = self._get_socket()
        
        future = asyncio.Future()
        
        def on_results(data):
            if not future.done():
                future.set_result(data)
        
        def on_error(error):
            if not future.done():
                if error.get('event') == 'search_by_user':
                    future.set_exception(Exception(error.get('message', 'Unknown error')))
        
        socket.once('user_search_results', on_results)
        socket.once('error', on_error)
        
        payload = {'userId': user_id, 'limit': limit}
        if query:
            payload['query'] = query
        
        await socket.emit('search_by_user', payload)
        
        return await future
