from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
from dotenv import load_dotenv
from telegram_bot import send_telegram_alert
from quotex_trader import execute_trade
from models import TradingSignal

load_dotenv()

app = FastAPI(title="Quotex Signal Bot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your_secret_key")

@app.get("/")
async def root():
    return {"status": "✅ Quotex Signal Bot is running!"}

@app.get("/health")
async def health():
    return {"status": "ok", "bot": "active"}

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    """TradingView se webhook signal receive karta hai"""
    try:
        # Secret key check karo
        secret = request.headers.get("X-Webhook-Secret", "")
        if secret != WEBHOOK_SECRET:
            raise HTTPException(status_code=403, detail="Invalid webhook secret")

        body = await request.json()

        # Signal parse karo
        signal = TradingSignal(
            asset=body.get("asset", "EURUSD"),
            direction=body.get("direction", "call").upper(),   # CALL ya PUT
            duration=body.get("duration", 60),                  # seconds mein (1 min = 60)
            amount=float(body.get("amount", os.getenv("DEFAULT_TRADE_AMOUNT", "1"))),
            strategy=body.get("strategy", "RSI+EMA"),
            confidence=body.get("confidence", "High"),
            price=body.get("price", "N/A"),
        )

        print(f"📡 Signal received: {signal.direction} on {signal.asset}")

        # Parallel mein Telegram alert + Quotex trade
        await asyncio.gather(
            send_telegram_alert(signal),
            execute_trade(signal)
        )

        return {"status": "success", "message": f"Signal processed: {signal.direction} {signal.asset}"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/manual-trade")
async def manual_trade(signal: TradingSignal):
    """Manual trade trigger karne ke liye"""
    try:
        await asyncio.gather(
            send_telegram_alert(signal),
            execute_trade(signal)
        )
        return {"status": "success", "signal": signal.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
