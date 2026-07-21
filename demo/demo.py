#!/usr/bin/env python3
"""
OddSockets Python SDK - runnable demo

A full pub/sub round-trip: connect -> subscribe -> publish -> receive.
Uses the same SDK a consumer installs. No mocks.

Run:
    export ODDSOCKETS_API_KEY="ak_..."   # get a free key: see README
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
    print("Missing ODDSOCKETS_API_KEY. Get a free key (see README), then:")
    print('  export ODDSOCKETS_API_KEY="ak_..."')
    sys.exit(1)

USER_ID = os.environ.get("ODDSOCKETS_USER_ID", "demo-agent")
NONCE = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
CHANNEL = f"demo-{NONCE}"


async def main():
    done = asyncio.Event()

    client = OddSockets({
        "api_key": API_KEY,
        "user_id": USER_ID,
        "auto_connect": False,
    })

    client.on("worker_assigned", lambda d: print("[worker] assigned", d.get("worker_id")))
    client.on("error", lambda e: print("[error]", e))

    async def on_message(data):
        body = data.get("message", data) if isinstance(data, dict) else data
        print("[recv]", body)
        if isinstance(body, dict) and body.get("nonce") == NONCE:
            print(f"\nOK - round-trip verified: published message received back on {CHANNEL}")
            done.set()

    print("[connect] connecting to OddSockets...")
    await client.connect()
    print("[connect] connected")

    channel = client.channel(CHANNEL)
    await channel.subscribe(on_message)
    print("[sub] subscribed to", CHANNEL)

    ack = await channel.publish({"text": "hello from the Python demo", "nonce": NONCE})
    print("[pub] published, ack =", ack)

    try:
        await asyncio.wait_for(done.wait(), timeout=15)
    except asyncio.TimeoutError:
        print("\nTIMEOUT - no echo received within 15s")
        await client.disconnect()
        sys.exit(2)

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
