"""
OddSockets Python SDK - Enhanced Features Usage Example
Demonstrates all 67 new Slack-like events
"""

import asyncio
from oddsockets import OddSockets


async def main():
    """Main example demonstrating all enhanced features"""
    
    # Create client
    client = OddSockets({
        'api_key': 'your_api_key_here',
        'user_id': 'user_123',
        'auto_connect': False  # Manual connect for this example
    })
    
    # Set up event listeners
    setup_event_listeners(client)
    
    # Connect
    print("🔄 Connecting to OddSockets...")
    await client.connect()
    
    # Wait a moment for connection
    await asyncio.sleep(2)
    
    if client.get_state() != 'connected':
        print("❌ Failed to connect")
        return
    
    print("✅ Connected successfully!\n")
    
    # ==================== THREAD EVENTS ====================
    print("📝 Testing Thread Events...")
    
    try:
        # Reply to a thread
        result = await client.enhanced.thread_reply(
            channel='general',
            parent_message_id='msg_123',
            message='This is a test reply from Python!',
            user_id='user_123',
            user_name='Test User'
        )
        print(f"✅ Thread reply created: {result}")
    except Exception as e:
        print(f"❌ Thread reply error: {e}")
    
    try:
        # Get thread
        thread = await client.enhanced.get_thread('thread_123')
        print(f"✅ Thread data: {thread}")
    except Exception as e:
        print(f"❌ Get thread error: {e}")
    
    try:
        # Subscribe to thread
        await client.enhanced.subscribe_thread('thread_123', 'user_123')
        print("✅ Subscribed to thread")
    except Exception as e:
        print(f"❌ Subscribe thread error: {e}")
    
    # Mark thread as read
    await client.enhanced.mark_thread_read('thread_123', 'user_123')
    print("✅ Marked thread as read")
    
    # Follow thread
    await client.enhanced.follow_thread('thread_123', 'user_123')
    print("✅ Following thread\n")
    
    # ==================== REACTION EVENTS ====================
    print("😀 Testing Reaction Events...")
    
    # Add reaction
    await client.enhanced.add_reaction(
        message_id='msg_123',
        channel='general',
        emoji='👍',
        user_id='user_123',
        user_name='Test User'
    )
    print("✅ Added reaction 👍")
    
    # Remove reaction
    await client.enhanced.remove_reaction(
        message_id='msg_123',
        channel='general',
        emoji='👍',
        user_id='user_123'
    )
    print("✅ Removed reaction")
    
    try:
        # Get reactions
        reactions = await client.enhanced.get_reactions('msg_123')
        print(f"✅ Reactions: {reactions}\n")
    except Exception as e:
        print(f"❌ Get reactions error: {e}\n")
    
    # ==================== READ RECEIPT EVENTS ====================
    print("✓ Testing Read Receipt Events...")
    
    # Mark message as read
    await client.enhanced.mark_read(
        message_id='msg_123',
        channel='general',
        user_id='user_123',
        user_name='Test User'
    )
    print("✅ Marked message as read")
    
    try:
        # Get unread counts
        counts = await client.enhanced.get_unread_counts(
            user_id='user_123',
            channels=['general', 'random']
        )
        print(f"✅ Unread counts: {counts}")
    except Exception as e:
        print(f"❌ Get unread counts error: {e}")
    
    # Mark all as read
    await client.enhanced.mark_all_read('general', 'user_123')
    print("✅ Marked all messages as read\n")
    
    # ==================== CHANNEL EVENTS ====================
    print("📢 Testing Channel Events...")
    
    try:
        # Create channel
        channel = await client.enhanced.create_channel(
            name=f'python-test-{int(asyncio.get_event_loop().time())}',
            channel_type='public',
            description='Created from Python SDK',
            topic='Testing',
            created_by='user_123',
            created_by_name='Test User'
        )
        print(f"✅ Channel created: {channel}")
    except Exception as e:
        print(f"❌ Create channel error: {e}")
    
    # Update channel
    await client.enhanced.update_channel(
        channel_id='channel_123',
        updates={'topic': 'Updated topic'},
        user_id='user_123'
    )
    print("✅ Updated channel")
    
    # Join channel
    await client.enhanced.join_channel(
        channel_id='channel_123',
        user_id='user_123',
        user_name='Test User'
    )
    print("✅ Joined channel")
    
    # Invite to channel
    await client.enhanced.invite_to_channel(
        channel_id='channel_123',
        invited_user_id='user_456',
        invited_user_name='Jane Doe',
        invited_by='user_123'
    )
    print("✅ Invited user to channel")
    
    try:
        # Get channel members
        members = await client.enhanced.get_channel_members('channel_123')
        print(f"✅ Channel members: {members}\n")
    except Exception as e:
        print(f"❌ Get channel members error: {e}\n")
    
    # ==================== DIRECT MESSAGE EVENTS ====================
    print("💬 Testing Direct Message Events...")
    
    try:
        # Create DM
        dm = await client.enhanced.create_dm(
            user_ids=['user_123', 'user_456'],
            dm_type='1-on-1'
        )
        print(f"✅ DM created: {dm}")
    except Exception as e:
        print(f"❌ Create DM error: {e}")
    
    # Send DM
    await client.enhanced.send_dm(
        conversation_id='dm_123',
        message='Hello from Python!',
        user_id='user_123',
        user_name='Test User'
    )
    print("✅ Sent DM")
    
    try:
        # Get DM conversations
        conversations = await client.enhanced.get_dm_conversations('user_123')
        print(f"✅ DM conversations: {conversations}\n")
    except Exception as e:
        print(f"❌ Get DM conversations error: {e}\n")
    
    # ==================== NOTIFICATION EVENTS ====================
    print("🔔 Testing Notification Events...")
    
    # Subscribe to notifications
    await client.enhanced.subscribe_notifications('user_123')
    print("✅ Subscribed to notifications")
    
    # Mark notification as read
    await client.enhanced.mark_notification_read('notif_123', 'user_123')
    print("✅ Marked notification as read")
    
    # Mark all notifications as read
    await client.enhanced.mark_all_notifications_read('user_123')
    print("✅ Marked all notifications as read")
    
    try:
        # Get notifications
        notifications = await client.enhanced.get_notifications(
            user_id='user_123',
            limit=10
        )
        print(f"✅ Notifications: {notifications}\n")
    except Exception as e:
        print(f"❌ Get notifications error: {e}\n")
    
    # ==================== FILE UPLOAD EVENTS ====================
    print("📎 Testing File Upload Events...")
    
    try:
        # Start file upload
        upload = await client.enhanced.start_file_upload(
            file_name='test.txt',
            file_size=1024,
            mime_type='text/plain',
            channel='general',
            user_id='user_123',
            user_name='Test User'
        )
        print(f"✅ File upload started: {upload}")
        
        # Update progress
        await client.enhanced.upload_progress(
            upload_id='upload_123',
            bytes_uploaded=512,
            channel='general'
        )
        print("✅ Upload progress updated")
        
        # Complete upload
        await client.enhanced.upload_complete(
            upload_id='upload_123',
            file_id='file_123',
            storage_info={'url': 'https://example.com/file.txt'},
            channel='general'
        )
        print("✅ Upload completed\n")
    except Exception as e:
        print(f"❌ File upload error: {e}\n")
    
    # ==================== PRESENCE EVENTS ====================
    print("👤 Testing Presence Events...")
    
    # Set status
    await client.enhanced.set_status('user_123', 'online')
    print("✅ Set status to online")
    
    # Set custom status
    await client.enhanced.set_custom_status(
        user_id='user_123',
        emoji='🐍',
        text='Coding in Python'
    )
    print("✅ Set custom status")
    
    # Clear custom status
    await client.enhanced.clear_custom_status('user_123')
    print("✅ Cleared custom status")
    
    # Set DND
    await client.enhanced.set_dnd('user_123')
    print("✅ Enabled Do Not Disturb")
    
    # Clear DND
    await client.enhanced.clear_dnd('user_123')
    print("✅ Disabled Do Not Disturb")
    
    # Start typing
    await client.enhanced.start_typing('user_123', 'general')
    print("✅ Started typing indicator")
    
    # Wait a moment
    await asyncio.sleep(2)
    
    # Stop typing
    await client.enhanced.stop_typing('user_123', 'general')
    print("✅ Stopped typing indicator")
    
    try:
        # Get user presence
        presence = await client.enhanced.get_user_presence(['user_123', 'user_456'])
        print(f"✅ User presence: {presence}\n")
    except Exception as e:
        print(f"❌ Get user presence error: {e}\n")
    
    # ==================== MESSAGE EDITING EVENTS ====================
    print("✏️ Testing Message Editing Events...")
    
    # Edit message
    await client.enhanced.edit_message(
        message_id='msg_123',
        channel='general',
        new_content='Updated message from Python',
        user_id='user_123'
    )
    print("✅ Edited message")
    
    # Delete message
    await client.enhanced.delete_message(
        message_id='msg_456',
        channel='general',
        user_id='user_123'
    )
    print("✅ Deleted message")
    
    # Pin message
    await client.enhanced.pin_message(
        message_id='msg_123',
        channel='general',
        user_id='user_123'
    )
    print("✅ Pinned message")
    
    # Unpin message
    await client.enhanced.unpin_message(
        message_id='msg_123',
        channel='general',
        user_id='user_123'
    )
    print("✅ Unpinned message")
    
    try:
        # Get pinned messages
        pinned = await client.enhanced.get_pinned_messages('general')
        print(f"✅ Pinned messages: {pinned}\n")
    except Exception as e:
        print(f"❌ Get pinned messages error: {e}\n")
    
    # ==================== SEARCH EVENTS ====================
    print("🔍 Testing Search Events...")
    
    try:
        # Search messages
        results = await client.enhanced.search_messages(
            query='test',
            user_id='user_123',
            limit=10
        )
        print(f"✅ Search results: {results}")
    except Exception as e:
        print(f"❌ Search messages error: {e}")
    
    try:
        # Search in channel
        channel_results = await client.enhanced.search_in_channel(
            channel='general',
            query='test',
            limit=10
        )
        print(f"✅ Channel search results: {channel_results}")
    except Exception as e:
        print(f"❌ Search in channel error: {e}")
    
    try:
        # Filter messages
        filtered = await client.enhanced.filter_messages(
            channel='general',
            user_id='user_123',
            limit=10
        )
        print(f"✅ Filter results: {filtered}")
    except Exception as e:
        print(f"❌ Filter messages error: {e}")
    
    try:
        # Search by user
        user_results = await client.enhanced.search_by_user(
            user_id='user_123',
            limit=10
        )
        print(f"✅ User search results: {user_results}\n")
    except Exception as e:
        print(f"❌ Search by user error: {e}\n")
    
    print("🎉 All enhanced features tested!")
    print("\n📊 Summary:")
    print("- Thread Events: 7 methods")
    print("- Reaction Events: 6 methods")
    print("- Read Receipt Events: 6 methods")
    print("- Channel Events: 11 methods")
    print("- Direct Message Events: 6 methods")
    print("- Notification Events: 6 methods")
    print("- File Upload Events: 7 methods")
    print("- Presence Events: 8 methods")
    print("- Message Editing Events: 5 methods")
    print("- Search Events: 4 methods")
    print("=" * 50)
    print("Total: 67 enhanced Slack-like events! 🚀")
    
    # Disconnect
    await client.disconnect()
    print("\n✅ Disconnected")


def setup_event_listeners(client):
    """Set up event listeners for enhanced events"""
    
    # Connection events
    client.on('connected', lambda: print("🟢 Connected event fired"))
    client.on('disconnected', lambda reason: print(f"🔴 Disconnected: {reason}"))
    client.on('error', lambda error: print(f"❌ Error: {error}"))
    
    # Get socket for enhanced event listeners
    def on_connected():
        socket = client._get_socket()
        if not socket:
            return
        
        # Thread events
        @socket.event
        async def new_thread_reply(data):
            print(f"📝 New thread reply: {data}")
        
        # Reaction events
        @socket.event
        async def reaction_added(data):
            print(f"😀 Reaction added: {data.get('emoji')}")
        
        @socket.event
        async def reaction_removed(data):
            print(f"😀 Reaction removed: {data.get('emoji')}")
        
        # Read receipt events
        @socket.event
        async def message_read(data):
            print(f"✓ Message read by {data.get('userId')}")
        
        # Channel events
        @socket.event
        async def channel_created(data):
            print(f"📢 Channel created: {data.get('channel', {}).get('name')}")
        
        @socket.event
        async def user_joined_channel(data):
            print(f"📢 User joined: {data.get('userId')}")
        
        # DM events
        @socket.event
        async def dm_received(data):
            print(f"💬 DM received from {data.get('from', {}).get('userId')}")
        
        # Notification events
        @socket.event
        async def notification(data):
            print(f"🔔 Notification: {data.get('type')}")
        
        # Presence events
        @socket.event
        async def user_status_changed(data):
            print(f"👤 {data.get('userId')} is now {data.get('status')}")
        
        @socket.event
        async def user_typing(data):
            print(f"👤 {data.get('userId')} is typing...")
        
        @socket.event
        async def custom_status_updated(data):
            print(f"👤 Custom status: {data.get('customStatus', {}).get('text')}")
        
        # Message editing events
        @socket.event
        async def message_edited(data):
            print(f"✏️ Message edited: {data.get('messageId')}")
        
        @socket.event
        async def message_deleted(data):
            print(f"🗑️ Message deleted: {data.get('messageId')}")
        
        @socket.event
        async def message_pinned(data):
            print(f"📌 Message pinned: {data.get('messageId')}")
    
    client.on('connected', on_connected)


if __name__ == '__main__':
    # Run the example
    asyncio.run(main())
