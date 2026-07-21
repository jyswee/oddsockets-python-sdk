# OddSockets Python SDK — Demo

A tiny, runnable program that does a full real-time round-trip against OddSockets:
**connect → subscribe → publish → receive**. It uses the exact SDK you would install, so it
doubles as an end-to-end smoke test.

## 1. Get a free API key

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
[connect] connecting to OddSockets...
[worker] assigned w00X-oddsockets-1
[connect] connected
[sub] subscribed to demo-...
[recv] {'text': 'hello from the Python demo', 'nonce': '...'}

OK - round-trip verified: published message received back on demo-...
```

## What it shows

- Manager discovery + automatic worker assignment (fully transparent)
- `client.channel(name)` → `channel.subscribe(cb)` → `channel.publish(msg)`
- Messages you publish are delivered back to your own subscription in real time
