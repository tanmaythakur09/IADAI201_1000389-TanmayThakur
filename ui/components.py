"""
Reusable UI components for ParkVision AI.
Provides Plotly visualizations (donut, gauge, histogram), KPI metric cards,
congestion badges, schematic slot maps, and recommendation cards.
"""

import plotly.graph_objects as go
import streamlit as st
from typing import List, Dict, Any, Optional
from utils.insights import LotSummary, SlotResult
from ui.theme import render_html


def render_kpi_cards(summary: LotSummary) -> None:
    """Renders 4 modern KPI cards with glassmorphism styling."""
    render_html(
        f"""
        <div class="pv-kpi-container">
            <div class="pv-kpi-card">
                <div class="pv-kpi-label">Total Capacity</div>
                <div class="pv-kpi-val">{summary.total_slots}</div>
                <div class="pv-kpi-sub">Total calibrated bays</div>
            </div>
            <div class="pv-kpi-card">
                <div class="pv-kpi-label">Occupied Bays</div>
                <div class="pv-kpi-val" style="color: #f87171;">{summary.occupied_slots}</div>
                <div class="pv-kpi-sub">Vehicles parked</div>
            </div>
            <div class="pv-kpi-card">
                <div class="pv-kpi-label">Available Bays</div>
                <div class="pv-kpi-val" style="color: #34d399;">{summary.available_slots}</div>
                <div class="pv-kpi-sub">Open for parking</div>
            </div>
            <div class="pv-kpi-card">
                <div class="pv-kpi-label">Occupancy Rate</div>
                <div class="pv-kpi-val" style="color: #60a5fa;">{summary.occupancy_pct}%</div>
                <div class="pv-kpi-sub">Current lot saturation</div>
            </div>
        </div>
        """
    )


def render_congestion_badge(congestion: str) -> None:
    """Renders a styled congestion level badge."""
    badge_classes = {
        "Low": ("pv-badge-low", "🟢", "Low Congestion (&lt; 40%)"),
        "Moderate": ("pv-badge-moderate", "🟡", "Moderate Congestion (40% - 75%)"),
        "High": ("pv-badge-high", "🔴", "High Congestion (&gt; 75%)"),
    }
    cls, icon, label = badge_classes.get(congestion, ("pv-badge-low", "⚪", congestion))
    render_html(
        f"""
        <div style="margin: 12px 0;">
            <span class="pv-badge {cls}">
                <span>{icon}</span>
                <span>{label}</span>
            </span>
        </div>
        """
    )


def render_recommendation_card(summary: Any, available_slot_ids: Optional[List[int]] = None) -> None:
    """Renders the recommendation card with icon and optional available slot ID chips."""
    if isinstance(summary, str):
        recommendation_text = summary
        congestion = "Moderate"
    else:
        recommendation_text = getattr(summary, "recommendation", str(summary))
        congestion = getattr(summary, "congestion", "Moderate")

    if congestion == "Low":
        card_bg = "rgba(16, 185, 129, 0.12)"
        border_col = "rgba(16, 185, 129, 0.35)"
        icon = "✅"
        title = "Slots Readily Available — Proceed to Lot"
    elif congestion == "Moderate":
        card_bg = "rgba(245, 158, 11, 0.12)"
        border_col = "rgba(245, 158, 11, 0.35)"
        icon = "⚠️"
        title = "Filling Up — Limited Spaces Remaining"
    else:
        card_bg = "rgba(239, 68, 68, 0.12)"
        border_col = "rgba(239, 68, 68, 0.35)"
        icon = "🚫"
        title = "Lot Critical / Full — Reroute Vehicles"

    render_html(
        f"""
        <div style="background: {card_bg}; border: 1.5px solid {border_col}; box-shadow: 0 0 16px rgba(0, 140, 255, 0.14); border-radius: 12px; padding: 18px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="font-size: 1.4rem;">{icon}</span>
                <span style="font-weight: 700; font-size: 1rem; color: #f9fafb;">{title}</span>
            </div>
            <p style="color: #e2e8f0; font-size: 0.90rem; margin: 0; line-height: 1.45;">
                {recommendation_text}
            </p>
        </div>
        """
    )

    if available_slot_ids:
        chips_html = "".join([f"<span class='pv-slot-chip pv-slot-empty'>Bay {sid:02d}</span>" for sid in available_slot_ids])
        render_html(
            f"""
            <div style="margin-top: -6px; margin-bottom: 14px;">
                <div style="font-size: 0.78rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                    Open Slot Numbers ({len(available_slot_ids)} total)
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                    {chips_html}
                </div>
            </div>
            """
        )



def create_donut_chart(occupied: int, available: int) -> go.Figure:
    """Creates a sleek Plotly donut chart of occupied vs available bays."""
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Available", "Occupied"],
                values=[available, occupied],
                hole=0.68,
                marker=dict(colors=["#10b981", "#ef4444"], line=dict(color="#111827", width=3)),
                textinfo="label+percent",
                hoverinfo="label+value+percent",
                textfont=dict(size=13, family="Inter", color="#ffffff"),
            )
        ]
    )
    fig.update_layout(
        title=dict(text="Occupancy Breakdown", font=dict(size=15, color="#f9fafb")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=20, l=20, r=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color="#9ca3af", size=12),
        ),
        height=270,
    )
    return fig


def create_gauge_chart(occupancy_pct: float) -> go.Figure:
    """Creates an occupancy gauge showing 40% and 75% congestion zones."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=occupancy_pct,
            number=dict(suffix="%", font=dict(size=28, color="#f9fafb")),
            gauge=dict(
                axis=dict(range=[0, 100], tickwidth=1, tickcolor="#64748b", tickfont=dict(color="#94a3b8")),
                bar=dict(color="#3b82f6", thickness=0.25),
                bgcolor="rgba(255,255,255,0.05)",
                borderwidth=1,
                bordercolor="rgba(255,255,255,0.1)",
                steps=[
                    {"range": [0, 40], "color": "rgba(16, 185, 129, 0.25)"},
                    {"range": [40, 75], "color": "rgba(245, 158, 11, 0.25)"},
                    {"range": [75, 100], "color": "rgba(239, 68, 68, 0.25)"},
                ],
                threshold=dict(
                    line=dict(color="#ffffff", width=3),
                    thickness=0.8,
                    value=occupancy_pct,
                ),
            ),
        )
    )
    fig.update_layout(
        title=dict(text="Congestion Gauge (0-40% Low, 40-75% Mod, >75% High)", font=dict(size=13, color="#f9fafb")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=20, l=25, r=25),
        height=270,
    )
    return fig


def create_confidence_histogram(results: List[SlotResult]) -> go.Figure:
    """Generates a confidence distribution histogram for all classified slots."""
    confs = [r.confidence * 100 for r in results]
    fig = go.Figure(
        data=[
            go.Histogram(
                x=confs,
                nbinsx=10,
                marker=dict(color="#3b82f6", line=dict(color="#1e3a8a", width=1)),
                opacity=0.85,
            )
        ]
    )
    fig.update_layout(
        title=dict(text="Model Prediction Confidence Distribution", font=dict(size=14, color="#f9fafb")),
        xaxis=dict(
            title=dict(text="Confidence (%)", font=dict(color="#94a3b8")),
            tickfont=dict(color="#94a3b8"),
            gridcolor="rgba(255,255,255,0.06)",
        ),
        yaxis=dict(
            title=dict(text="Number of Slots", font=dict(color="#94a3b8")),
            tickfont=dict(color="#94a3b8"),
            gridcolor="rgba(255,255,255,0.06)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=30, l=30, r=20),
        height=260,
    )
    return fig


def render_slot_map(results: List[SlotResult]) -> None:
    """Renders a schematic tile grid of every slot colored by status."""
    chips = []
    for r in sorted(results, key=lambda x: x.slot_id):
        cls = "pv-slot-occupied" if r.occupied else "pv-slot-empty"
        tag = "OCC" if r.occupied else "FREE"
        chips.append(f"<span class='pv-slot-chip {cls}' title='Slot #{r.slot_id}: {tag} ({int(r.confidence*100)}%)'>#{r.slot_id} {tag}</span>")

    render_html(
        f"""
        <div class="pv-slot-grid">
            {"".join(chips)}
        </div>
        """
    )
