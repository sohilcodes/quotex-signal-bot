import os
import asyncio
import json
import httpx
from models import TradingSignal

QUOTEX_EMAIL = os.getenv("QUOTEX_EMAIL")
QUOTEX_PASSWORD = os.getenv("QUOTEX_PASSWORD")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

WS_URL = "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket"

async def execute_trade(signal: TradingSignal):
    if not QUOTEX_EMAIL or not QUOTEX_PASSWORD:
        print("⚠️ Quotex credentials missing, skipping trade")
        return
    try:
        token = await get_auth_token()
        if not token:
            print("❌ Quotex auth failed")
            return
        await place_trade_ws(token, signal)
    except Exception as e:
        print(f"❌ Trade execution error: {e}")

async def get_auth_token():
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://qxbroker.com/api/v1/login",
                json={"email": QUOTEX_EMAIL, "password": QUOTEX_PASSWORD},
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("token") or data.get("data", {}).get("token")
                if token:
                    print("✅ Quotex login successful")
                    return token
            print(f"⚠️ Login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

async def place_trade_ws(token: str, signal: TradingSignal):
    try:
        import websockets
        async with websockets.connect(WS_URL, extra_headers={"Authorization": f"Bearer {token}"}, timeout=15) as ws:
            await ws.send(json.dumps({"action": "authenticate", "token": token}))
            await asyncio.sleep(1)
            account_type = "practice" if DEMO_MODE else "real"
            await ws.send(json.dumps({
                "action": "buy",
                "asset": signal.asset.upper(),
                "direction": signal.direction.lower(),
                "duration": signal.duration,
                "amount": signal.amount,
                "account_type": account_type
            }))
            print(f"✅ Trade sent: {signal.direction} {signal.asset} ${signal.amount}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
