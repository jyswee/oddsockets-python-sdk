# OddSockets Python SDK — Demo

A tiny, runnable program that proves a real real-time round-trip against OddSockets
using **two independent clients**: **connect → subscribe → publish → receive**.

Because the subscriber (`alice`) and the publisher (`bob`) are separate connections,
a message that reaches the subscriber can only have travelled through the OddSockets
worker — so this doubles as an honest end-to-end regression test (no mocks, no local
echo). It uses the exact SDK you would install.

## 1. Get an API key

Two-step email verification (no card required):

```bash
# Step 1 — request a code
curl -X POST https://oddsockets.com/api/agent-signup \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","agentName":"demo","platform":"claude"}'

# Step 2 — verify and receive your apiKey
curl -X POST https://oddsockets.com/api/agent-signup/verify \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","code":"123456","agentName":"demo"}'
```

The verify response contains your `apiKey` (starts with `ak_`).

## 2. Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install oddsockets
export ODDSOCKETS_API_KEY="ak_your_key_here"
python demo.py
```

Expected output:

```
[connect] connecting both clients...
[connect] both connected
[alice] subscribed to demo-... (presence on)
[alice] received bob’s message (nonce matched) - real round-trip.
[bob] published, ack = {'messageId': '...', 'channel': 'demo-...', 'subscriberCount': 1}
[alice] presence: 1 user(s).
[alice] unsubscribed.

OK - cross-client round-trip verified on demo-...
```

## The code, step by step

Create two clients — a subscriber and a publisher — each on its own connection:

```python
from oddsockets import OddSockets

subscriber = OddSockets({"api_key": api_key, "user_id": "alice", "auto_connect": False})
publisher  = OddSockets({"api_key": api_key, "user_id": "bob",   "auto_connect": False})

await asyncio.gather(subscriber.connect(), publisher.connect())
```

Subscribe on the subscriber (presence enabled):

```python
inbox = subscriber.channel("my-channel")
await inbox.subscribe(on_message, {"enable_presence": True})
```

Publish from the *other* client — this is what makes the test honest:

```python
outbox = publisher.channel("my-channel")
ack = await outbox.publish({"text": "hello from bob"})
print("messageId:", ack["messageId"])
```

Inspect presence, then tear down cleanly:

```python
presence = await inbox.get_presence()   # {"channel", "count", "occupants"}
await inbox.unsubscribe()
await subscriber.disconnect()
await publisher.disconnect()
```

## What it demonstrates

- Manager discovery + automatic worker assignment (fully transparent)
- `client.channel(name)` → `channel.subscribe(cb, opts)` → `channel.publish(msg)`
- **Cross-client delivery**: a message published by `bob` is delivered to `alice`’s
  subscription in real time — provably through the worker, not a local echo
- Presence tracking, unsubscribe, and graceful disconnect
- A 15-second timeout so a stalled round-trip is reported as a failure (non-zero exit)
