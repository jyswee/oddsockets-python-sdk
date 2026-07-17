# OddSockets Python SDK

[![PyPI version](https://badge.fury.io/py/oddsocketsai-python-sdk.svg)](https://badge.fury.io/py/oddsocketsai-python-sdk)
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
pip install oddsocketsai-python-sdk
# or
poetry add oddsocketsai-python-sdk
```

## 🏃‍♂️ Quick Start

### Basic Usage (Async)

```python
import asyncio
from oddsockets import OddSockets

async def main():
    client = OddSockets(
        api_key='ak_live_1234567890abcdef',
        manager_url='https://connect.oddsockets.tyga.network'
    )
    
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
from oddsockets import OddSockets, Channel, Message

client: OddSockets = OddSockets(
    api_key='ak_live_1234567890abcdef'
)

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

client = OddSockets(
    api_key='your-api-key',           # Required: Your OddSockets API key
    manager_url='manager-url',        # Optional: Manager URL
    user_id='user-id',                # Optional: User identifier
    auto_connect=True,                # Optional: Auto-connect on creation
    reconnect_attempts=5,             # Optional: Max reconnection attempts
    heartbeat_interval=30.0           # Optional: Heartbeat interval (seconds)
)
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

- **[GitHub Issues](https://github.com/tygacloud/oddsocketsai-python-sdk/issues)** - Bug reports and feature requests
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
