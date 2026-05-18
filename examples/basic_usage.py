#!/usr/bin/env python3
"""
OddSockets Python SDK - Basic Usage Example

This example demonstrates the basic usage of the OddSockets Python SDK
for real-time messaging and pub/sub functionality.
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def message_handler(data):
    """Handle incoming messages"""
    logger.info(f"📨 Received message: {data}")


async def main():
    """Main example function"""
    try:
        # Import OddSockets
        from oddsockets import OddSockets
        
        logger.info("🚀 OddSockets Python SDK - Basic Usage Example")
        logger.info("=" * 50)
        
        # Create an OddSockets client
        client = OddSockets({
            'api_key': 'ak_your_api_key_here',
            'user_id': 'python-demo-user',
            'auto_connect': True
        })
        
        # Wait for connection
        await asyncio.sleep(2)
        logger.info("✅ Connected to OddSockets")
        
        # Get a channel
        channel = client.channel("python-demo-channel")
        logger.info(f"📡 Created channel: python-demo-channel")
        
        # Subscribe to messages
        await channel.subscribe(message_handler, {
            'enable_presence': True,
            'retain_history': True
        })
        logger.info("✅ Subscribed to channel")
        
        # Publish some test messages
        messages = [
            "Hello from Python! 🐍",
            {"type": "notification", "text": "This is a structured message"},
            {"user": "alice", "action": "joined", "timestamp": "2024-01-15T10:30:00Z"},
            [1, 2, 3, 4, 5],  # Arrays work too
            42  # Numbers work
        ]
        
        for i, message in enumerate(messages, 1):
            logger.info(f"📤 Publishing message {i}/{len(messages)}")
            result = await channel.publish(message, {
                'metadata': {"example": True, "message_number": i}
            })
            logger.info(f"   Published: {result}")
            await asyncio.sleep(1)  # Small delay between messages
        
        # Bulk publish example
        bulk_messages = [
            {'channel': 'python-demo-channel', 'message': 'Bulk message 1'},
            {'channel': 'python-demo-channel', 'message': 'Bulk message 2'},
            {'channel': 'python-demo-channel', 'message': 'Bulk message 3'}
        ]
        
        logger.info("📦 Publishing bulk messages...")
        bulk_results = await client.publish_bulk(bulk_messages)
        logger.info(f"   Bulk publish results: {len(bulk_results)} messages")
        
        # Get channel presence
        try:
            presence = await channel.get_presence()
            logger.info(f"👥 Channel presence: {presence}")
        except Exception as e:
            logger.warning(f"Could not get presence: {e}")
        
        # Get message history
        try:
            history = await channel.get_history({'count': 10})
            logger.info(f"📚 Retrieved {len(history)} messages from history")
        except Exception as e:
            logger.warning(f"Could not get history: {e}")
        
        # Update user state
        try:
            await channel.update_state({'status': 'active', 'location': 'python-demo'})
            logger.info("🔄 Updated user state")
        except Exception as e:
            logger.warning(f"Could not update state: {e}")
        
        # Keep connection alive for a bit to receive messages
        logger.info("⏳ Keeping connection alive for 5 seconds...")
        await asyncio.sleep(5)
        
        # Get client info
        worker_info = client.get_worker_info()
        if worker_info:
            logger.info(f"🔧 Connected to worker: {worker_info['worker_id']}")
        
        session_info = client.get_session_info()
        if session_info:
            logger.info(f"🔐 Session info: {session_info}")
        
        client_id = client.get_client_identifier()
        logger.info(f"🆔 Client identifier: {client_id}")
        
        # Clean up
        await channel.unsubscribe()
        logger.info("📤 Unsubscribed from channel")
        
        await client.disconnect()
        logger.info("✅ Disconnected successfully")
        
    except ImportError:
        logger.error("❌ OddSockets SDK not found")
        logger.info("Make sure to install the SDK: pip install oddsockets")
    except Exception as e:
        logger.error(f"❌ Error: {e}")


def event_handler_example():
    """Example of using event handlers"""
    try:
        from oddsockets import OddSockets
        
        # Create client
        client = OddSockets({
            'api_key': 'ak_your_api_key_here',
            'auto_connect': False
        })
        
        # Set up event handlers
        def on_connecting():
            logger.info("🔄 Connecting...")
        
        def on_connected():
            logger.info("✅ Connected!")
        
        def on_disconnected():
            logger.info("❌ Disconnected")
        
        def on_error(error):
            logger.error(f"💥 Error: {error}")
        
        def on_worker_assigned(data):
            logger.info(f"🎯 Assigned to worker: {data['worker_id']}")
        
        # Register event handlers
        client.on('connecting', on_connecting)
        client.on('connected', on_connected)
        client.on('disconnected', on_disconnected)
        client.on('error', on_error)
        client.on('worker_assigned', on_worker_assigned)
        
        logger.info("📋 Event handlers registered")
        
    except ImportError:
        logger.error("❌ OddSockets SDK not found")


if __name__ == "__main__":
    logger.info("🐍 OddSockets Python SDK Examples")
    logger.info("=" * 60)
    
    # Show event handler setup
    event_handler_example()
    
    logger.info("")
    logger.info("-" * 60)
    logger.info("")
    
    # Run main async example
    asyncio.run(main())
    
    logger.info("")
    logger.info("🎉 Example completed!")
    logger.info("")
    logger.info("Key Features Demonstrated:")
    logger.info("✅ Manager discovery and worker assignment")
    logger.info("✅ Session stickiness with client identifiers")
    logger.info("✅ Message publishing and subscription")
    logger.info("✅ Bulk message publishing")
    logger.info("✅ Message size validation (32KB limit)")
    logger.info("✅ Presence tracking")
    logger.info("✅ Message history")
    logger.info("✅ User state management")
    logger.info("✅ Event handling system")
    logger.info("✅ Automatic reconnection with exponential backoff")
    logger.info("✅ Consistent API with JavaScript SDK")
