"""
Shared parking-insight logic for ParkVision AI.

Kept separate from app.py so the same rules can be unit-tested and
reused (e.g. from a notebook) without importing Streamlit.
"""

from dataclasses import dataclass
from typing import List, Literal

CongestionLevel = Literal["Low", "Moderate", "High"]


@dataclass
class SlotResult:
    slot_id: int
    occupied: bool
    confidence: float  # model confidence in the predicted label, 0-1


@dataclass
class LotSummary:
    total_slots: int
    occupied_slots: int
    available_slots: int
    occupancy_pct: float
    congestion: CongestionLevel
    recommendation: str


def classify_congestion(occupancy_pct: float) -> CongestionLevel:
    """Brief's thresholds: Low <40%, Moderate 40-75%, High >75%."""
    if occupancy_pct < 40:
        return "Low"
    elif occupancy_pct <= 75:
        return "Moderate"
    else:
        return "High"


def generate_recommendation(congestion: CongestionLevel, available_slots: int) -> str:
    if congestion == "Low":
        return f"Plenty of space — {available_slots} slots open. Go ahead and park here."
    elif congestion == "Moderate":
        return f"Filling up — {available_slots} slots left. Proceed, but don't expect to be picky about location."
    else:
        if available_slots > 0:
            return f"Nearly full — only {available_slots} slot(s) left. Consider another lot if you're not already close."
        return "Parking full — try another location."


def summarize_lot(results: List[SlotResult]) -> LotSummary:
    total = len(results)
    occupied = sum(1 for r in results if r.occupied)
    available = total - occupied
    occupancy_pct = (occupied / total * 100) if total > 0 else 0.0
    congestion = classify_congestion(occupancy_pct)
    recommendation = generate_recommendation(congestion, available)
    return LotSummary(
        total_slots=total,
        occupied_slots=occupied,
        available_slots=available,
        occupancy_pct=round(occupancy_pct, 1),
        congestion=congestion,
        recommendation=recommendation,
    )
