import httpx
import os
from models import TradingSignal

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def send_telegram_alert(signal: TradingSignal):
    """Telegram pe signal alert bhejta hai"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials missing, skipping alert")
        return

    message = build_message(signal)

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ Telegram alert sent: {signal.direction} {signal.asset}")
            else:
                print(f"❌ Telegram error: {response.text}")
    except Exception as e:
        print(f"❌ Telegram send failed: {e}")


def build_message(signal: TradingSignal) -> str:
    duration_min = signal.duration // 60
    duration_sec = signal.duration % 60
    duration_str = f"{duration_min}m {duration_sec}s" if duration_sec else f"{duration_min}m"

    confidence_emoji = {
        "High": "🔥",
        "Medium": "⚡",
        "Low": "⚠️"
    }.get(signal.confidence, "📊")

    return f"""
{signal.emoji()} <b>QUOTEX SIGNAL</b> {signal.emoji()}
━━━━━━━━━━━━━━━━━━━
💹 <b>Asset:</b> {signal.asset}
{signal.direction_label()}
⏱ <b>Duration:</b> {duration_str} (1 Minute)
💰 <b>Amount:</b> ${signal.amount}
{confidence_emoji} <b>Confidence:</b> {signal.confidence}
📊 <b>Strategy:</b> {signal.strategy}
💲 <b>Entry Price:</b> {signal.price}
🕐 <b>Time:</b> {signal.timestamp}
━━━━━━━━━━━━━━━━━━━
⚡ Auto-trade executing on Quotex...
⚠️ <i>Trade at your own risk</i>
"""
