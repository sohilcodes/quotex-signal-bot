import os
import asyncio
from models import TradingSignal

QUOTEX_EMAIL = os.getenv("QUOTEX_EMAIL")
QUOTEX_PASSWORD = os.getenv("QUOTEX_PASSWORD")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"


async def execute_trade(signal: TradingSignal):
    """Quotex pe auto-trade execute karta hai"""
    if not QUOTEX_EMAIL or not QUOTEX_PASSWORD:
        print("⚠️ Quotex credentials missing, skipping trade")
        return

    try:
        # quotexapi library use karte hain
        from quotexapi.stable_api import Quotex

        client = Quotex(
            email=QUOTEX_EMAIL,
            password=QUOTEX_PASSWORD,
        )

        print(f"🔐 Quotex login kar raha hoon...")
        check, reason = await client.connect()

        if not check:
            print(f"❌ Quotex login failed: {reason}")
            return

        print(f"✅ Quotex connected!")

        # Demo ya Real account
        if DEMO_MODE:
            client.change_account("PRACTICE")
            print("🎮 DEMO account use ho raha hai")
        else:
            client.change_account("REAL")
            print("💰 REAL account use ho raha hai")

        # Balance check karo
        balance = await client.get_balance()
        print(f"💳 Balance: ${balance}")

        # Asset format karo (EURUSD → EURUSD_otc ya EURUSD)
        asset = format_asset(signal.asset)
        direction = signal.direction.lower()  # "call" ya "put"

        print(f"📡 Trade place kar raha hoon: {direction.upper()} {asset} ${signal.amount} {signal.duration}s")

        # Trade execute karo
        status, buy_info = await client.buy(
            price=signal.amount,
            asset=asset,
            direction=direction,
            duration=signal.duration
        )

        if status:
            trade_id = buy_info.get("id", "N/A")
            print(f"✅ Trade placed successfully! ID: {trade_id}")

            # Result wait karo
            await asyncio.sleep(signal.duration + 2)
            result = await client.check_win(trade_id)
            profit = result.get("profit", 0)

            if profit > 0:
                print(f"🏆 WIN! Profit: ${profit}")
            else:
                print(f"❌ LOSS! Amount: ${signal.amount}")
        else:
            print(f"❌ Trade failed: {buy_info}")

        await client.close()

    except ImportError:
        print("⚠️ quotexapi not installed. Run: pip install quotexapi")
        print(f"📊 [SIMULATED] Trade: {signal.direction} {signal.asset} ${signal.amount}")
    except Exception as e:
        print(f"❌ Trade execution error: {e}")


def format_asset(asset: str) -> str:
    """Asset name ko Quotex format mein convert karta hai"""
    asset = asset.upper().replace("/", "").replace("-", "")

    # Common OTC pairs (weekends pe ye use hote hain)
    otc_pairs = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "AUDUSD"]

    # Normally non-OTC try karo pehle
    return asset
