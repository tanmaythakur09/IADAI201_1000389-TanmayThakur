"""
Calibration & User Feedback view for ParkVision AI.
High-fidelity dark glassmorphic model validation and continuous learning center.
Allows users to evaluate inference accuracy, log misclassified slot IDs,
provide environmental notes, and view the authentic community feedback registry.
All metrics derive strictly from the SQLite feedback table.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

from datetime import datetime
from db.database import save_feedback, get_user_feedback_by_email
from ui.theme import get_dash_banner_base64, render_html


def render_feedback_view() -> None:
    """Renders the Calibration & Feedback operations view using only real SQLite feedback records."""
    user = st.session_state.get("user") or {}
    is_guest = st.session_state.get("is_guest", False)
    user_id = user.get("id") if (user and not is_guest) else None
    user_email = user.get("email") if (user and not is_guest) else None

    banner_b64 = get_dash_banner_base64()
    banner_bg_css = ""
    if banner_b64:
        banner_bg_css = f"background-image: linear-gradient(90deg, rgba(7, 16, 38, 0.95) 0%, rgba(7, 18, 44, 0.85) 45%, rgba(6, 14, 32, 0.40) 100%), url('data:image/jpeg;base64,{banner_b64}');"

    # -------------------------------------------------------------------------
    # 1. TOP PANORAMIC HERO BANNER (NO FAKE DATE STAMP)
    # -------------------------------------------------------------------------
    render_html(
        f"""
        <div class="pv-hero-banner" style="{banner_bg_css}">
            <div style="display: flex; align-items: center; gap: 16px; z-index: 2;">
                <div class="pv-hero-icon-box" style="background: rgba(16, 185, 129, 0.16); border-color: rgba(16, 185, 129, 0.45); color: #34d399;">
                    💬
                </div>
                <div>
                    <div style="font-size: 1.55rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                        Calibration & Continuous Feedback
                    </div>
                    <div style="color: #94a3b8; font-size: 0.84rem; margin-top: 3px; font-weight: 500;">
                        Ground-truth verification loop and SQLite model fine-tuning registry.
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 14px; z-index: 2;">
                <div class="pv-header-chip">
                    <span style="font-size: 1.05rem;">📝</span>
                    <div>
                        <div style="font-size: 0.80rem; font-weight: 700; color: #34d399;">SQLite Feedback Store</div>
                        <div style="font-size: 0.65rem; color: #94a3b8;">Stored locally in SQLite</div>
                    </div>
                </div>
            </div>
        </div>
        """
    )

    # -------------------------------------------------------------------------
    # 2. FETCH REAL FEEDBACK (SCOPED PER USER, GUEST IN-SESSION ONLY)
    # -------------------------------------------------------------------------
    if is_guest:
        records = list(st.session_state.get("guest_feedback", []))
    elif user_email:
        records = get_user_feedback_by_email(user_email, limit=100)
    else:
        records = []
    total_feedback = len(records)
    if total_feedback > 0:
        ratings = [r["rating"] for r in records if "rating" in r and r["rating"] is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        avg_rating_str = f"{avg_rating:.1f} / 5.0"
    else:
        avg_rating_str = "No ratings yet"

    # -------------------------------------------------------------------------
    # 3. KPI METRIC CARDS (REAL DATA ONLY, NO DELTAS, NO SPARKLINES)
    # -------------------------------------------------------------------------
    render_html(
        f"""
        <div class="pv-kpi-v2-grid" style="grid-template-columns: repeat(2, 1fr);">
            <div class="pv-kpi-v2-card">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="pv-kpi-icon-circle" style="background: rgba(0, 140, 255, 0.14); border: 1px solid rgba(0, 180, 255, 0.35); color: #00d2ff;">
                        👥
                    </div>
                    <div>
                        <div class="pv-kpi-v2-title">FEEDBACK SUBMISSIONS</div>
                        <div class="pv-kpi-v2-val" style="color: #ffffff;">{total_feedback}</div>
                        <div class="pv-kpi-v2-sub">Recorded in SQLite database</div>
                    </div>
                </div>
            </div>
            <div class="pv-kpi-v2-card">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="pv-kpi-icon-circle" style="background: rgba(245, 158, 11, 0.14); border: 1px solid rgba(245, 158, 11, 0.35); color: #fbbf24;">
                        ⭐
                    </div>
                    <div>
                        <div class="pv-kpi-v2-title">AVERAGE USER RATING</div>
                        <div class="pv-kpi-v2-val" style="color: #fbbf24;">{avg_rating_str}</div>
                        <div class="pv-kpi-v2-sub">Average of submitted ratings</div>
                    </div>
                </div>
            </div>
        </div>
        """
    )

    # -------------------------------------------------------------------------
    # 4. SUBMISSION FORM (60%) & RECENT SUBMISSIONS TABLE (40%)
    # -------------------------------------------------------------------------
    col_form, col_list = st.columns([1.2, 1])

    with col_form:
        with st.container(border=True):
            render_html(
                """
                <div class="pv-panel-header" style="margin-bottom: 12px;">
                    <div class="pv-panel-title">
                        <span>✍️</span>
                        <span>Submit Calibration Feedback</span>
                    </div>
                </div>
                """
            )

            with st.form("feedback_form", clear_on_submit=True):
                if is_guest:
                    st.write("Logged in as: **Guest Visitor (in-session only)**")
                    btn_label = "💾 Save Feedback"
                else:
                    st.write(f"Logged in as: **{user_email}**")
                    btn_label = "💾 Save Feedback to SQLite"

                rating = st.slider(
                    "Overall Model Performance Rating",
                    min_value=1,
                    max_value=5,
                    value=5,
                    step=1,
                    help="1 = Poor classification, 5 = Flawless detection",
                )

                prediction_correct = st.radio(
                    "Were the predictions on your last analysed image accurate?",
                    options=["Yes, all slots were classified correctly", "Mostly correct (1-2 errors)", "No, multiple incorrect slots"],
                    index=0,
                )

                wrong_slots = st.text_input(
                    "Misclassified Slot IDs (Optional)",
                    placeholder="e.g. Bay 04, Bay 12",
                    help="Enter specific slot numbers that were misclassified under current lighting/shadow conditions.",
                )

                comments = st.text_area(
                    "Notes & Environmental Context",
                    placeholder="Describe lighting, camera angle, heavy rainfall, specular glare, or vehicle occlusion...",
                    height=100,
                )

                submitted = st.form_submit_button(btn_label, type="primary", use_container_width=True)
                if submitted:
                    if is_guest:
                        if "guest_feedback" not in st.session_state:
                            st.session_state["guest_feedback"] = []
                        guest_fb = {
                            "id": len(st.session_state["guest_feedback"]) + 1,
                            "rating": rating,
                            "prediction_correct": prediction_correct,
                            "wrong_slots": wrong_slots,
                            "comments": comments,
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                        st.session_state["guest_feedback"].insert(0, guest_fb)
                        st.success("Feedback recorded for your guest session!")
                        st.rerun()
                    else:
                        save_feedback(
                            user_id=user_id,
                            user_email=user_email,
                            rating=rating,
                            prediction_correct=prediction_correct,
                            wrong_slots=wrong_slots,
                            comments=comments,
                        )
                        st.success("Feedback successfully saved to SQLite registry!")
                        st.rerun()

    with col_list:
        with st.container(border=True):
            render_html(
                """
                <div class="pv-panel-header" style="margin-bottom: 12px;">
                    <div class="pv-panel-title">
                        <span>📜</span>
                        <span>Recent SQLite Submissions</span>
                    </div>
                </div>
                """
            )

            if records:
                df = pd.DataFrame(records)
                # Never display other users' emails in any table
                disp_cols = [c for c in ["id", "rating", "prediction_correct", "wrong_slots", "created_at"] if c in df.columns]
                st.dataframe(df[disp_cols], use_container_width=True, hide_index=True)

                csv_bytes = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Export Feedback Records CSV",
                    data=csv_bytes,
                    file_name="parkvision_feedback_records.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="btn_download_real_feedback_csv",
                )
            else:
                render_html(
                    """
                    <div style="background: rgba(2, 6, 18, 0.80); border: 1.5px dashed rgba(255, 255, 255, 0.12); border-radius: 10px; padding: 28px 18px; text-align: center; margin: 10px 0;">
                        <span style="font-size: 1.8rem;">💬</span>
                        <div style="color: #ffffff; font-weight: 700; font-size: 0.88rem; margin-top: 8px;">No Feedback Records Yet</div>
                        <div style="color: #94a3b8; font-size: 0.76rem; margin-top: 4px; line-height: 1.4;">
                            Submit a rating using the form on the left to start recording verification telemetry.
                        </div>
                    </div>
                    """
                )
