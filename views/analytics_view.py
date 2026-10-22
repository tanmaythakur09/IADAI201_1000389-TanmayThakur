"""
Historical Parking Analytics view for ParkVision AI.
High-fidelity dark glassmorphic operations center.
Displays exclusively authentic historical analysis records from SQLite.
Contains zero invented data, zero synthetic points, zero fake deltas,
and honest empty states when insufficient data exists.
"""

from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from db.database import get_user_analyses_by_email, get_user_analyses
from ui.theme import get_dash_banner_base64, render_html


def create_real_history_chart(analyses: List[Dict[str, Any]], metric: str = "Occupancy") -> go.Figure:
    """Builds a chart based strictly on real analysis records ordered chronologically."""
    fig = go.Figure()
    chronological = sorted(analyses, key=lambda x: str(x.get("created_at", "")))

    timestamps = [str(a.get("created_at", ""))[:19] for a in chronological]

    if metric == "Congestion":
        cong_map = {"Low": 25, "Moderate": 60, "High": 85}
        y_vals = [cong_map.get(a.get("congestion", "Low"), 25) for a in chronological]
        cong_labels = [a.get("congestion", "Low") for a in chronological]

        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=y_vals,
                mode="lines+markers",
                name="Congestion Level",
                line=dict(color="#fbbf24", width=2.5),
                marker=dict(size=8, color="#fbbf24", line=dict(width=1.5, color="#ffffff")),
                text=cong_labels,
                hovertemplate="Time: %{x}<br>Congestion: <b>%{text}</b><extra></extra>",
            )
        )
        y_title = "Congestion Level"
    else:
        y_vals = [float(a.get("occupancy_pct", 0.0)) for a in chronological]
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=y_vals,
                mode="lines+markers",
                name="Occupancy Rate (%)",
                line=dict(color="#00d2ff", width=2.5),
                marker=dict(size=8, color="#00d2ff", line=dict(width=1.5, color="#ffffff")),
                fill="tozeroy",
                fillcolor="rgba(0, 210, 255, 0.12)",
                hovertemplate="Time: %{x}<br>Occupancy: <b>%{y:.1f}%</b><extra></extra>",
            )
        )
        # 75% High Congestion threshold line
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=[75] * len(timestamps),
                mode="lines",
                name="High Congestion Threshold (75%)",
                line=dict(color="#ef4444", width=1.5, dash="dash"),
                hoverinfo="name",
            )
        )
        y_title = "Occupancy (%)"

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=45, r=20, t=32, b=35),
        height=270,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="left",
            x=0.0,
            font=dict(family="Inter, sans-serif", size=10.5, color="#cbd5e1"),
        ),
        xaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.05)",
            tickfont=dict(family="Inter, sans-serif", size=10, color="#94a3b8"),
            zeroline=False,
            title=None,
        ),
        yaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.05)",
            tickfont=dict(family="Inter, sans-serif", size=10, color="#94a3b8"),
            range=[0, 105],
            dtick=20,
            zeroline=False,
            title=dict(text=y_title, font=dict(family="Inter, sans-serif", size=10, color="#64748b")),
        ),
        hovermode="closest",
    )
    return fig


def create_distribution_donut(avg_occ: float) -> go.Figure:
    """Builds the real occupancy distribution donut chart."""
    avail_pct = max(0.0, round(100.0 - avg_occ, 1))
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Occupied", "Available"],
                values=[avg_occ, avail_pct],
                hole=0.72,
                marker=dict(
                    colors=["#00a8ff", "#00e5ff"],
                    line=dict(color="#070e1c", width=3),
                ),
                textinfo="none",
                hoverinfo="label+percent",
                direction="clockwise",
                sort=False,
            )
        ]
    )

    fig.add_annotation(
        text=f"<b style='font-size:1.35rem; color:#ffffff;'>{avg_occ:.1f}%</b><br><span style='font-size:0.68rem; color:#94a3b8;'>Avg. Occupancy</span>",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(family="Inter, sans-serif", size=14, color="#ffffff"),
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=5, b=5),
        height=170,
        showlegend=False,
    )
    return fig


def render_analytics_view() -> None:
    """Renders the Historical Parking Analytics page using only real database records."""
    user = st.session_state.get("user") or {}
    is_guest = st.session_state.get("is_guest", False)
    user_email = user.get("email") if (user and not is_guest) else None

    # Fetch genuine analysis records strictly scoped per user:
    # Guests: in-session history only (honest empty state if none)
    # Registered users: only rows belonging to their logged-in user_email
    if is_guest:
        analyses = list(st.session_state.get("guest_analyses", []))
    elif user_email:
        analyses = get_user_analyses_by_email(user_email, limit=100)
    else:
        analyses = []

    banner_b64 = get_dash_banner_base64()
    banner_bg_css = ""
    if banner_b64:
        banner_bg_css = f"background-image: linear-gradient(90deg, rgba(7, 16, 38, 0.94) 0%, rgba(7, 18, 44, 0.82) 45%, rgba(6, 14, 32, 0.40) 100%), url('data:image/jpeg;base64,{banner_b64}');"

    # Determine real date range from recorded analyses
    if analyses:
        chronological = sorted(analyses, key=lambda x: str(x.get("created_at", "")))
        first_date = str(chronological[0].get("created_at", ""))[:10]
        last_date = str(chronological[-1].get("created_at", ""))[:10]
        date_range_str = f"{first_date} – {last_date}" if first_date != last_date else first_date
    else:
        date_range_str = "No recorded sessions"

    # -------------------------------------------------------------------------
    # 1. TOP PANORAMIC HERO BANNER
    # -------------------------------------------------------------------------
    render_html(
        f"""
        <div class="pv-hero-banner" style="{banner_bg_css}">
            <div style="display: flex; align-items: center; gap: 16px; z-index: 2;">
                <div class="pv-hero-icon-box" style="font-size: 1.55rem; line-height: 1;">
                    📈
                </div>
                <div>
                    <div style="font-size: 1.55rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                        Historical Parking Analytics
                    </div>
                    <div style="color: #94a3b8; font-size: 0.84rem; margin-top: 3px; font-weight: 500;">
                        Instant analysis of uploaded images • SQLite Audit Log
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 24px; z-index: 2;">
                <div style="background: rgba(7, 16, 38, 0.85); border: 1.5px solid rgba(0, 140, 255, 0.35); border-radius: 12px; padding: 8px 16px; display: flex; align-items: center; gap: 10px; backdrop-filter: blur(12px); box-shadow: 0 0 12px rgba(0, 140, 255, 0.12);">
                    <span style="font-size: 1.05rem;">📅</span>
                    <span style="font-size: 0.82rem; font-weight: 600; color: #f1f5f9; letter-spacing: 0.02em;">
                        {date_range_str}
                    </span>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.82rem; font-weight: 700; color: #f1f5f9; letter-spacing: 0.02em;">Smarter Cities.</div>
                    <div style="font-size: 0.82rem; font-weight: 700; color: #f1f5f9; letter-spacing: 0.02em;">Better Parking.</div>
                    <div style="width: 32px; height: 3px; background: #00d2ff; border-radius: 2px; margin-left: auto; margin-top: 4px;"></div>
                </div>
            </div>
        </div>
        """
    )

    # -------------------------------------------------------------------------
    # 2. CHECK FOR EMPTY STATE
    # -------------------------------------------------------------------------
    if not analyses:
        render_html(
            """
            <div style="background: rgba(2, 6, 18, 0.88); border: 1.5px dashed rgba(0, 140, 255, 0.35); border-radius: 14px; padding: 48px 24px; text-align: center; margin: 24px 0;">
                <div style="font-size: 2.5rem; margin-bottom: 12px;">📊</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #ffffff; margin-bottom: 6px;">
                    No Historical Analysis Records Found
                </div>
                <div style="color: #94a3b8; font-size: 0.88rem; max-width: 480px; margin: 0 auto 20px auto; line-height: 1.5;">
                    Historical analytics are generated strictly from genuine computer vision inference runs.
                    Upload or select an image on the Dashboard to record your first analysis session.
                </div>
            </div>
            """
        )
        if st.button("🚀 Run Analysis on Dashboard", type="primary", use_container_width=False):
            if "nav_pages" in st.session_state and "dashboard" in st.session_state["nav_pages"]:
                st.switch_page(st.session_state["nav_pages"]["dashboard"])
        return

    # -------------------------------------------------------------------------
    # 3. COMPUTE REAL METRICS FROM ANALYSES
    # -------------------------------------------------------------------------
    total_sessions = len(analyses)
    occ_values = [float(a.get("occupancy_pct", 0.0)) for a in analyses]
    avg_occ = sum(occ_values) / total_sessions if total_sessions > 0 else 0.0
    peak_occ = max(occ_values) if occ_values else 0.0

    cong_counts = Counter(a.get("congestion", "Low") for a in analyses)
    modal_cong = cong_counts.most_common(1)[0][0] if cong_counts else "Low"
    cong_colors = {"Low": "#34d399", "Moderate": "#fbbf24", "High": "#f87171"}
    modal_cong_color = cong_colors.get(modal_cong, "#34d399")

    # -------------------------------------------------------------------------
    # 4. 4 KPI METRIC CARDS (CLEAN REAL DATA, NO DELTAS, NO SPARKLINES)
    # -------------------------------------------------------------------------
    render_html(
        f"""
        <div class="pv-kpi-v2-grid">
            <div class="pv-kpi-v2-card">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="pv-kpi-icon-circle" style="background: rgba(0, 140, 255, 0.14); border: 1px solid rgba(0, 180, 255, 0.35); color: #00d2ff;">
                        👥
                    </div>
                    <div>
                        <div class="pv-kpi-v2-title">TOTAL SESSIONS</div>
                        <div class="pv-kpi-v2-val" style="color: #ffffff;">{total_sessions}</div>
                        <div class="pv-kpi-v2-sub">Recorded inference runs</div>
                    </div>
                </div>
            </div>
            <div class="pv-kpi-v2-card">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="pv-kpi-icon-circle" style="background: rgba(59, 130, 246, 0.14); border: 1px solid rgba(59, 130, 246, 0.35); color: #60a5fa;">
                        ⏱️
                    </div>
                    <div>
                        <div class="pv-kpi-v2-title">AVERAGE OCCUPANCY</div>
                        <div class="pv-kpi-v2-val" style="color: #ffffff;">{avg_occ:.1f}%</div>
                        <div class="pv-kpi-v2-sub">Mean across all sessions</div>
                    </div>
                </div>
            </div>
            <div class="pv-kpi-v2-card">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="pv-kpi-icon-circle" style="background: rgba(168, 85, 247, 0.14); border: 1px solid rgba(168, 85, 247, 0.35); color: #c084fc;">
                        📈
                    </div>
                    <div>
                        <div class="pv-kpi-v2-title">PEAK OCCUPANCY</div>
                        <div class="pv-kpi-v2-val" style="color: #ffffff;">{peak_occ:.1f}%</div>
                        <div class="pv-kpi-v2-sub">Highest recorded point</div>
                    </div>
                </div>
            </div>
            <div class="pv-kpi-v2-card">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="pv-kpi-icon-circle" style="background: rgba(16, 185, 129, 0.14); border: 1px solid rgba(16, 185, 129, 0.35); color: #34d399;">
                        🚗
                    </div>
                    <div>
                        <div class="pv-kpi-v2-title">MODAL CONGESTION</div>
                        <div class="pv-kpi-v2-val" style="color: {modal_cong_color};">{modal_cong}</div>
                        <div class="pv-kpi-v2-sub">Dominant status</div>
                    </div>
                </div>
            </div>
        </div>
        """
    )

    # -------------------------------------------------------------------------
    # 5. MIDDLE ROW: REAL TREND CHART (65%) & REAL INSIGHTS (35%)
    # -------------------------------------------------------------------------
    col_mid_left, col_mid_right = st.columns([1.7, 1])

    with col_mid_left:
        with st.container(border=True):
            h_col1, h_col2 = st.columns([2, 1], vertical_alignment="center")
            with h_col1:
                render_html(
                    """
                    <div style="margin-bottom: 0px;">
                        <div class="pv-panel-title">
                            <span>📈</span>
                            <span>Historical Inference Sessions</span>
                        </div>
                        <div style="color: #94a3b8; font-size: 0.74rem; margin-top: 2px;">
                            Actual occupancy and congestion recorded in SQLite.
                        </div>
                    </div>
                    """
                )
            with h_col2:
                sel_metric = st.segmented_control(
                    "Metric",
                    options=["Occupancy", "Congestion"],
                    default="Occupancy",
                    key="analytics_metric_sel",
                    label_visibility="collapsed",
                ) or "Occupancy"

            st.plotly_chart(
                create_real_history_chart(analyses, metric=sel_metric),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    with col_mid_right:
        with st.container(border=True):
            render_html(
                """
                <div class="pv-panel-header" style="margin-bottom: 14px;">
                    <div class="pv-panel-title">
                        <span>📅</span>
                        <span>Session Insights</span>
                    </div>
                </div>
                """
            )

            # Honest computation: Require at least 5 sessions to establish diurnal/pricing patterns
            if total_sessions < 5:
                render_html(
                    f"""
                    <div style="background: rgba(2, 6, 18, 0.90); border: 1.5px dashed rgba(245, 158, 11, 0.35); border-radius: 12px; padding: 18px 16px; text-align: center;">
                        <span style="font-size: 1.8rem;">⏳</span>
                        <div style="color: #fbbf24; font-weight: 700; font-size: 0.88rem; margin: 8px 0 4px 0;">
                            Awaiting Historical Baseline
                        </div>
                        <div style="color: #94a3b8; font-size: 0.76rem; line-height: 1.45;">
                            Diurnal peak times, lowest occupancy windows, and routing trends require at least <b>5 sessions</b> across multiple time periods.
                        </div>
                        <div style="margin-top: 10px; font-size: 0.78rem; color: #cbd5e1;">
                            Recorded: <b style="color: #00d2ff;">{total_sessions} / 5 sessions</b>
                        </div>
                    </div>
                    """
                )
            else:
                max_analysis = max(analyses, key=lambda x: float(x.get("occupancy_pct", 0.0)))
                min_analysis = min(analyses, key=lambda x: float(x.get("occupancy_pct", 0.0)))
                latest_analysis = analyses[0]

                peak_time_str = str(max_analysis.get("created_at", "N/A"))[:16]
                min_time_str = str(min_analysis.get("created_at", "N/A"))[:16]

                render_html(
                    f"""
                    <div style="display: flex; align-items: flex-start; gap: 12px; background: rgba(2, 6, 18, 0.90); border: 1.5px solid rgba(16, 185, 129, 0.35); box-shadow: 0 0 12px rgba(16, 185, 129, 0.12); border-radius: 12px; padding: 12px 14px; margin-bottom: 10px;">
                        <div style="width: 34px; height: 34px; border-radius: 50%; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); color: #34d399; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0;">
                            ↗
                        </div>
                        <div>
                            <div style="color: #34d399; font-weight: 700; font-size: 0.82rem;">Recorded Peak Session</div>
                            <div style="color: #ffffff; font-weight: 700; font-size: 0.88rem; margin: 1px 0;">{peak_time_str}</div>
                            <div style="color: #94a3b8; font-size: 0.72rem;">Peak rate: {max_analysis.get('occupancy_pct', 0.0):.1f}% on {max_analysis.get('image_name', 'lot')}</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 12px; background: rgba(2, 6, 18, 0.90); border: 1.5px solid rgba(168, 85, 247, 0.35); box-shadow: 0 0 12px rgba(168, 85, 247, 0.12); border-radius: 12px; padding: 12px 14px; margin-bottom: 10px;">
                        <div style="width: 34px; height: 34px; border-radius: 50%; background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.35); color: #c084fc; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0;">
                            ⏱️
                        </div>
                        <div>
                            <div style="color: #c084fc; font-weight: 700; font-size: 0.82rem;">Lowest Occupancy Session</div>
                            <div style="color: #ffffff; font-weight: 700; font-size: 0.88rem; margin: 1px 0;">{min_time_str}</div>
                            <div style="color: #94a3b8; font-size: 0.72rem;">Low rate: {min_analysis.get('occupancy_pct', 0.0):.1f}% ({min_analysis.get('available_slots', 0)} bays free)</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 12px; background: rgba(2, 6, 18, 0.90); border: 1.5px solid rgba(0, 140, 255, 0.35); box-shadow: 0 0 12px rgba(0, 140, 255, 0.12); border-radius: 12px; padding: 12px 14px;">
                        <div style="width: 34px; height: 34px; border-radius: 50%; background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.35); color: #60a5fa; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0;">
                            💡
                        </div>
                        <div>
                            <div style="color: #60a5fa; font-weight: 700; font-size: 0.82rem;">Latest Recommendation</div>
                            <div style="color: #cbd5e1; font-size: 0.76rem; line-height: 1.45; margin-top: 2px;">
                                {latest_analysis.get('recommendation', 'Continue regular space monitoring.')}
                            </div>
                        </div>
                    </div>
                    """
                )

    # -------------------------------------------------------------------------
    # 6. BOTTOM ROW: REAL AUDIT TABLE (65%) & DISTRIBUTION DONUT (35%)
    # -------------------------------------------------------------------------
    col_bot_left, col_bot_right = st.columns([1.7, 1])

    with col_bot_left:
        with st.container(border=True):
            render_html(
                """
                <div class="pv-panel-header" style="margin-bottom: 12px;">
                    <div class="pv-panel-title">
                        <span>📋</span>
                        <span>SQLite Analysis History Records</span>
                    </div>
                </div>
                """
            )

            rows_html = ""
            for idx, a in enumerate(analyses):
                t_stamp = str(a.get("created_at", ""))[:19]
                img_n = a.get("image_name", "")
                tot_s = a.get("total_slots", 0)
                occ_s = a.get("occupied_slots", 0)
                pct_s = f"{a.get('occupancy_pct', 0.0):.1f}%"
                cg_s = a.get("congestion", "Low")

                badge_style = "background: rgba(16, 185, 129, 0.14); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35);"
                if cg_s == "High":
                    badge_style = "background: rgba(239, 68, 68, 0.14); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.35);"
                elif cg_s == "Moderate":
                    badge_style = "background: rgba(234, 179, 8, 0.14); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.35);"

                border_bottom = "border-bottom: 1px solid rgba(255, 255, 255, 0.05);" if idx < len(analyses) - 1 else ""
                rows_html += f"""
                <tr style="{border_bottom} color: #f1f5f9;">
                    <td style="padding: 10px 12px; font-weight: 500; font-family: monospace; color: #94a3b8; font-size: 0.78rem;">{t_stamp}</td>
                    <td style="padding: 10px 12px; color: #00d2ff; font-weight: 600;">{img_n}</td>
                    <td style="padding: 10px 12px; text-align: center; color: #cbd5e1;">{tot_s}</td>
                    <td style="padding: 10px 12px; text-align: center; color: #f87171; font-weight: 600;">{occ_s}</td>
                    <td style="padding: 10px 12px; text-align: center; color: #ffffff; font-weight: 700;">{pct_s}</td>
                    <td style="padding: 10px 12px; text-align: right;">
                        <span style="{badge_style} font-size: 0.72rem; font-weight: 700; padding: 2px 10px; border-radius: 5px;">
                            {cg_s}
                        </span>
                    </td>
                </tr>
                """

            render_html(
                f"""
                <div style="overflow-x: auto; max-height: 280px;">
                    <table style="width: 100%; border-collapse: collapse; font-family: Inter, sans-serif; font-size: 0.84rem;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #94a3b8; text-align: left;">
                                <th style="padding: 10px 12px; font-weight: 600;">Timestamp</th>
                                <th style="padding: 10px 12px; font-weight: 600;">Image Source</th>
                                <th style="padding: 10px 12px; font-weight: 600; text-align: center;">Capacity</th>
                                <th style="padding: 10px 12px; font-weight: 600; text-align: center;">Occupied</th>
                                <th style="padding: 10px 12px; font-weight: 600; text-align: center;">Occupancy</th>
                                <th style="padding: 10px 12px; font-weight: 600; text-align: right;">Congestion</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
                """
            )

            df_export = pd.DataFrame(analyses)
            csv_str = df_export.to_csv(index=False)
            st.download_button(
                "📥 Export Full SQLite History CSV",
                data=csv_str,
                file_name="parkvision_history_records.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_export_real_history_csv",
            )

    with col_bot_right:
        with st.container(border=True):
            render_html(
                """
                <div class="pv-panel-header" style="margin-bottom: 10px;">
                    <div class="pv-panel-title">
                        <span>📊</span>
                        <span>Average Saturation</span>
                    </div>
                </div>
                """
            )

            c_pie, c_legend = st.columns([1, 1.1])
            with c_pie:
                st.plotly_chart(
                    create_distribution_donut(avg_occ),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            with c_legend:
                avail_pct_disp = max(0.0, round(100.0 - avg_occ, 1))
                render_html(
                    f"""
                    <div style="padding-top: 18px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="color: #00a8ff; font-size: 0.95rem;">●</span>
                                <span style="color: #f1f5f9; font-weight: 500;">Occupied</span>
                            </div>
                            <div>
                                <b style="color: #ffffff;">{avg_occ:.1f}%</b>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="color: #00e5ff; font-size: 0.95rem;">●</span>
                                <span style="color: #f1f5f9; font-weight: 500;">Available</span>
                            </div>
                            <div>
                                <b style="color: #ffffff;">{avail_pct_disp:.1f}%</b>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="color: {modal_cong_color}; font-size: 0.95rem;">●</span>
                                <span style="color: #f1f5f9; font-weight: 500;">Congestion</span>
                            </div>
                            <div>
                                <b style="color: {modal_cong_color};">{modal_cong}</b>
                            </div>
                        </div>
                    </div>
                    """
                )
