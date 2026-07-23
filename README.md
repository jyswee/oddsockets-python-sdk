# OddSockets Python SDK

[![PyPI version](https://badge.fury.io/py/oddsockets.svg)](https://pypi.org/project/oddsockets/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

Official Python SDK for OddSockets real-time messaging platform.

## Features

- **AsyncIO Support**: Full async/await support with asyncio
- **Sync Support**: Traditional synchronous API available
- **Type Hints**: Complete type annotations for better IDE support
- **PubNub Compatible**: Drop-in replacement for PubNub Python SDK
- **High Performance**: 50% lower latency than PubNub
- **Cost Effective**: No per-message pricing, no message size limits
- **Framework Ready**: Django, Flask, FastAPI integrations available

## Installation

```bash
pip install oddsockets
# or
poetry add oddsockets
```

## 🏃‍♂️ Quick Start

### Basic Usage (Async)

```python
import asyncio
from oddsockets import OddSockets

async def main():
    client = OddSockets({
        'api_key': 'ak_live_1234567890abcdef',
        'user_id': 'server-user-123'
    })

    channel = client.channel('my-channel')
    
    # Subscribe to messages
    async def on_message(message):
        print(f'Received: {message}')
    
    await channel.subscribe(on_message)
    
    # Publish a message
    await channel.publish('Hello from Python!')
    
    # Keep the connection alive
    await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
```

### Basic Usage (Sync)

```python
from oddsockets.sync import OddSockets

client = OddSockets(
    api_key='ak_live_1234567890abcdef',
    manager_url='https://connect.oddsockets.tyga.network'
)

channel = client.channel('my-channel')

# Subscribe to messages
def on_message(message):
    print(f'Received: {message}')

channel.subscribe(on_message)

# Publish a message
channel.publish('Hello from Python!')

# Keep the connection alive
import time
time.sleep(10)
```

### PubNub Migration

```python
from oddsockets.pubnub_compat import PubNub

# Drop-in replacement for PubNub
pubnub = PubNub({
    'publish_key': 'ak_live_1234567890abcdef',
    'subscribe_key': 'ak_live_1234567890abcdef',
    'user_id': 'user123'
})

def message_callback(message, envelope):
    print(f'Message: {message}')

pubnub.add_listener({
    'message': message_callback
})

pubnub.subscribe().channels(['my-channel']).execute()
```

### Type Hints

```python
from typing import Dict, Any
from oddsockets import OddSockets, Channel
from oddsockets.types import Message

client: OddSockets = OddSockets({
    'api_key': 'ak_live_1234567890abcdef'
})

channel: Channel = client.channel('typed-channel')

async def typed_handler(message: Message) -> None:
    data: Dict[str, Any] = message.data
    print(f'Typed message: {data}')
```

## Documentation

- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Getting Started](docs/getting-started.md)** - Detailed setup guide
- **[Migration Guide](docs/migration-guide.md)** - Migrate from PubNub
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## Examples

Explore our comprehensive examples:

- **[Basic Usage](examples/basic_usage.py)** - Simple messaging
- **[PubNub Migration](examples/pubnub_migration.py)** - Migration example
- **[Django Integration](examples/django_example.py)** - Django integration
- **[FastAPI Integration](examples/fastapi_example.py)** - FastAPI integration

## Configuration

### Client Options

```python
from oddsockets import OddSockets

client = OddSockets({
    'api_key': 'your-api-key',          # Required: Your OddSockets API key
    'user_id': 'user-id',               # Optional: User identifier
    'options': {                        # Optional: connection options
        'auto_connect': True,           #   Auto-connect on creation
        'reconnect_attempts': 5,        #   Max reconnection attempts
        'heartbeat_interval': 30.0      #   Heartbeat interval (seconds)
    }
})
```

### Channel Options

```python
# Subscribe with options
await channel.subscribe(
    callback,
    enable_presence=True,             # Enable presence tracking
    retain_history=True,              # Retain message history
    filter_expression='user.premium == True'  # Message filter
)

# Publish with options
await channel.publish(
    message,
    ttl=3600,                         # Time to live (seconds)
    metadata={'priority': 'high'},    # Additional metadata
    store_in_history=True             # Store in message history
)
```

## Enhanced Features

Beyond core pub/sub, OddSockets ships a Slack-like **enhanced surface** — reactions,
typing indicators, threads, read receipts, presence/status, notifications, DMs,
channel management, message editing and search. It lives on `client.enhanced`. The
pattern is always the same:

1. **Send** an action with an `await client.enhanced.*` coroutine (snake_case).
2. **Receive** the paired broadcast with `client.on('<event>', handler)`.

```python
import asyncio
from oddsockets import OddSockets

async def main():
    client = OddSockets({'api_key': 'ak_live_1234567890abcdef', 'user_id': 'alice'})
    channel = client.channel('room-42')
    await channel.subscribe()

    # Receive-path: broadcasts from other users on the channel
    client.on('user_typing', lambda e: print(f"{e['userId']} is typing"))
    client.on('reaction_added', lambda e: print(f"{e['userId']} reacted {e['emoji']}"))
    client.on('thread_reply', lambda e: print('New reply:', e))

    # Send-path: enhanced actions over the live socket
    await client.enhanced.start_typing('alice', 'room-42')
    await client.enhanced.add_reaction(
        message_id='msg-1',
        channel='room-42',
        emoji=':thumbsup:',
        user_id='alice',
        user_name='Alice'
    )
    await client.enhanced.thread_reply(
        channel='room-42',
        parent_message_id='msg-1',
        message='Replying in the thread',
        user_id='alice',
        user_name='Alice'
    )

    await asyncio.sleep(2)
    await client.disconnect()

asyncio.run(main())
```

Each area exposes coroutine methods on `client.enhanced`; the worker broadcasts the
paired events which you handle with `client.on(...)`. Query methods (`get_*`,
`search_*`) await and return the worker response.

| Area | Requests (`await client.enhanced.*`) | Broadcast events (`client.on`) |
|------|--------------------------------------|--------------------------------|
| Typing | `start_typing`, `stop_typing` | `user_typing`, `user_stopped_typing` |
| Reactions | `add_reaction`, `remove_reaction`, `get_reactions` | `reaction_added`, `reaction_removed` |
| Threads | `thread_reply`, `get_thread`, `subscribe_thread`, `follow_thread`, `mark_thread_read` | `thread_reply`, `thread_subscribed`, `thread_followed`, `thread_read_updated` |
| Read receipts | `mark_read`, `mark_all_read`, `get_unread_counts` | `user_read`, `unread_count_updated`, `all_marked_read` |
| Messages | `edit_message`, `delete_message`, `pin_message`, `unpin_message`, `get_pinned_messages`, `search_messages` | `message_edited`, `message_deleted`, `message_pinned`, `message_unpinned` |
| Presence & status | `set_status`, `set_custom_status`, `set_dnd`, `get_user_presence` | `user_status_changed`, `custom_status_updated`, `dnd_status_changed` |
| Channels | `create_channel`, `update_channel`, `archive_channel`, `invite_to_channel`, `join_channel`, `leave_channel` | `channel_created`, `channel_updated`, `user_invited`, `user_joined_channel`, `user_left_channel` |
| DMs | `create_dm`, `send_dm`, `get_dm_conversations` | `dm_created`, `dm_received` |
| Notifications | `subscribe_notifications`, `get_notifications`, `mark_notification_read`, `clear_notifications` | `notification`, `notification_read`, `notifications_cleared` |
| File uploads | `start_file_upload`, `upload_progress`, `upload_complete` | `file_upload_completed`, `file_upload_progress`, `file_upload_failed` |

For any worker event not wrapped above, subscribe with the raw
`client.on('<event>', handler)` API — all enhanced broadcasts are forwarded onto the
client surface.

## 🐍 Python Support

- Python 3.8+
- AsyncIO support
- Type hints included
- Both sync and async APIs

## 🧪 Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=oddsockets

# Run async tests
pytest -m asyncio

# Run integration tests
pytest tests/integration/
```

## 🔨 Building

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run linting
flake8 src/
black src/
mypy src/

# Build package
python -m build

# Install locally
pip install -e .
```

## 📈 Performance

OddSockets Python SDK delivers superior performance:

- **50% lower latency** compared to PubNub
- **99.9% uptime** with automatic failover
- **Unlimited message size** - no artificial limits
- **High throughput** - handle millions of messages

## 🔐 Security

- **End-to-end encryption** available
- **API key authentication** with fine-grained permissions
- **Rate limiting** and abuse protection
- **GDPR compliant** data handling

## Framework Integrations

### Django

```python
# settings.py
ODDSOCKETS = {
    'API_KEY': 'ak_live_1234567890abcdef',
    'MANAGER_URL': 'https://connect.oddsockets.tyga.network'
}

# views.py
from django.http import JsonResponse
from oddsockets.django import get_client

async def send_message(request):
    client = get_client()
    channel = client.channel('notifications')
    await channel.publish({
        'user_id': request.user.id,
        'message': 'Hello from Django!'
    })
    return JsonResponse({'status': 'sent'})
```

### FastAPI

```python
from fastapi import FastAPI
from oddsockets import OddSockets

app = FastAPI()
client = OddSockets(api_key='ak_live_1234567890abcdef')

@app.post("/send-message")
async def send_message(message: str):
    channel = client.channel('api-messages')
    await channel.publish({'text': message})
    return {"status": "sent"}

@app.on_event("startup")
async def startup():
    await client.connect()

@app.on_event("shutdown")
async def shutdown():
    await client.disconnect()
```

### Flask

```python
from flask import Flask, request, jsonify
from oddsockets.sync import OddSockets

app = Flask(__name__)
client = OddSockets(api_key='ak_live_1234567890abcdef')

@app.route('/send-message', methods=['POST'])
def send_message():
    message = request.json.get('message')
    channel = client.channel('flask-messages')
    channel.publish({'text': message})
    return jsonify({'status': 'sent'})
```

## 🌍 Other SDKs

OddSockets is available in multiple languages:

- **[JavaScript SDK](../javascript/)** - Browser + Node.js, TypeScript ready
- **[Go SDK](../go/)** - High-performance, goroutines and channels
- **[Java SDK](../java/)** - Enterprise-ready, Spring Boot integration
- **[C# SDK](../csharp/)** - .NET Core/Framework, Azure integrations
- **[Swift SDK](../swift/)** - iOS native, Combine framework
- **[Kotlin SDK](../kotlin/)** - Android native, coroutines support

## 📞 Support

- **[GitHub Issues](https://github.com/jyswee/oddsockets-python-sdk/issues)** - Bug reports and feature requests
- **[Documentation](https://docs.oddsockets.com)** - Complete documentation
- **[Community Discord](https://discord.gg/oddsockets)** - Community support
- **Email**: support@oddsockets.com

## 📄 License

## Get a Free API Key

AI agents can sign up with a verified email in two steps — no dashboard, no human required.

**Step 1:** Request a verification code
```bash
curl -X POST https://oddsockets.com/api/agent-signup \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "agentName": "my-agent", "platform": "python"}'
```

**Step 2:** Verify the 6-digit code from your email and get your API key
```bash
curl -X POST https://oddsockets.com/api/agent-signup/verify \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "code": "123456", "agentName": "my-agent"}'
```

## Plans

| | Free | Starter | Pro |
|---|---|---|---|
| **Price** | $0/mo | $49.99/mo | $299/mo |
| **MAU** | 100 | 1,000 | 50,000 |
| **Concurrent connections** | 50 | 1,000 | Unlimited |
| **Messages/day** | 10,000 | 4,320,000 | Unlimited |
| **Messages/minute** | 100 | 3,000 | Unlimited |
| **Channels** | 10 | Unlimited | Unlimited |
| **Storage** | 100MB (24h) | 50GB (6 months) | Unlimited |
| **Webhooks** | No | Yes | Yes |
| **Analytics** | No | Yes | Yes |
| **Support** | Community | 24/5 email & chat | Dedicated team |

All limits are enforced in real time. When a limit is reached, the SDK receives a `RATE_LIMIT_EXCEEDED` error with a `retryAfter` value.

## Support

- [Documentation](https://docs.oddsockets.com/sdks/python)
- [Issue Tracker](https://github.com/jyswee/oddsockets-python-sdk/issues)
- [Email Support](mailto:support@oddsockets.com)

## License

MIT License - Copyright (c) 2026 Joe Wee, Tyga.Cloud Ltd. See [LICENSE](LICENSE) for details.
