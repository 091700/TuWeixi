"""Token 成本追踪 — P2"""

import time
import logging

logger = logging.getLogger("db_agent.cost")

PRICING = {
    "deepseek-chat": {"input": 0.14, "output": 0.28},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19},
}

class CostTracker:
    def __init__(self):
        self._records = []

    def record(self, session_id: str, model: str, input_tokens: int, output_tokens: int):
        price = PRICING.get(model, PRICING["deepseek-chat"])
        cost = (input_tokens * price["input"] + output_tokens * price["output"]) / 1_000_000
        self._records.append({
            "session": session_id[:8],
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        return cost

    def summary(self) -> dict:
        total = sum(r["cost_usd"] for r in self._records)
        return {
            "total_cost_usd": round(total, 4),
            "total_calls": len(self._records),
            "total_tokens": sum(r["input_tokens"] + r["output_tokens"] for r in self._records),
        }


cost_tracker = CostTracker()