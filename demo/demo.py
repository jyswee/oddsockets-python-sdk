#!/usr/bin/env python3
"""
OddSockets Python SDK - runnable two-client demo

A genuine end-to-end round-trip using TWO independent clients:
    - a SUBSCRIBER (user "alice") that listens on a channel
    - a PUBLISHER  (user "bob")   that sends one message

Because they are separate connections, a message reaching the subscriber can
ONLY have travelled through the OddSockets worker - it cannot be a local echo.
A matched nonce here is proof of a real round-trip. Uses the same SDK a consumer
installs. No mocks.

Exercised surface: connect -> subscribe (+presence) -> publish -> receive
-> presence -> unsubscribe -> disconnect.

Run:
    export ODDSOCKETS_API_KEY="ak_..."   # get an API key: see README
    pip install oddsockets
    python demo.py
"""
import asyncio
import os
import sys
import random
import string

from oddsockets import OddSockets

API_KEY = os.environ.get("ODDSOCKETS_API_KEY")
if not API_KEY:
    print("Missing ODDSOCKETS_API_KEY. Get an API key (see README), then:")
    print('  export ODDSOCKETS_API_KEY="ak_..."')
    sys.exit(1)

NONCE = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
CHANNEL = f"demo-{NONCE}"


async def main():
    done = asyncio.Event()

    # Two independent clients on the same platform.
    subscriber = OddSockets({"api_key": API_KEY, "user_id": "alice", "auto_connect": False})
    publisher = OddSockets({"api_key": API_KEY, "user_id": "bob", "auto_connect": False})

    subscriber.on("worker_assigned", lambda d: print("[alice] worker", d.get("worker_id")))
    publisher.on("worker_assigned", lambda d: print("[bob]   worker", d.get("worker_id")))
    subscriber.on("error", lambda e: print("[alice] error", e))
    publisher.on("error", lambda e: print("[bob]   error", e))

    inbox = None

    async def on_message(data):
        body = data.get("message", data) if isinstance(data, dict) else data
        if isinstance(body, dict) and body.get("nonce") == NONCE:
            print("[alice] received bob\u2019s message (nonce matched) - real round-trip.")
            try:
                presence = await inbox.get_presence()
                count = presence.get("count", len(presence.get("occupants", [])))
                print("[alice] presence:", count, "user(s).")
                await inbox.unsubscribe()
                print("[alice] unsubscribed.")
            except Exception:
                pass  # best-effort; round-trip already proven
            done.set()

    print("[connect] connecting both clients...")
    await asyncio.gather(subscriber.connect(), publisher.connect())
    print("[connect] both connected")

    # Subscriber joins with presence enabled.
    inbox = subscriber.channel(CHANNEL)
    await inbox.subscribe(on_message, {"enable_presence": True})
    print("[alice] subscribed to", CHANNEL, "(presence on)")

    # Publisher sends from its OWN connection.
    outbox = publisher.channel(CHANNEL)
    ack = await outbox.publish({"text": "hello from bob", "nonce": NONCE, "from": "bob"})
    print("[bob] published, ack =", ack)

    try:
        await asyncio.wait_for(done.wait(), timeout=15)
        print(f"\nOK - cross-client round-trip verified on {CHANNEL}")
    except asyncio.TimeoutError:
        print("\nTIMEOUT - no cross-client delivery within 15s")
        await subscriber.disconnect()
        await publisher.disconnect()
        sys.exit(2)

    await subscriber.disconnect()
    await publisher.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
