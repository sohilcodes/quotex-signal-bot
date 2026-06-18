from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TradingSignal(BaseModel):
    asset: str = "EURUSD"
    direction: str = "CALL"        # CALL (UP) ya PUT (DOWN)
    duration: int = 60             # seconds (60 = 1 minute)
    amount: float = 1.0            # trade amount in USD
    strategy: str = "RSI+EMA"
    confidence: str = "High"       # High / Medium / Low
    price: Optional[str] = "N/A"
    timestamp: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.timestamp:
            self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    def emoji(self) -> str:
        return "🟢" if self.direction.upper() == "CALL" else "🔴"

    def direction_label(self) -> str:
        return "📈 CALL (UP)" if self.direction.upper() == "CALL" else "📉 PUT (DOWN)"
