"""
Core Dashboard view for ParkVision AI.
High-fidelity dark glassmorphic operations center.
Provides instant analysis of uploaded images with computer vision inference.
Includes real-time system clock greeting, calibrated inference KPI cards,
side-by-side original vs annotated visual inspection, open slot guidance chips,
interactive slot grid schematic, detailed per-slot status table, and executive exports.
"""

import base64
import datetime
import hashlib
import io
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

import cv2
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st

from db.database import save_analysis
from ui.components import (
    render_congestion_badge,
    render_recommendation_card,
    render_slot_map,
)
from ui.theme import get_dash_banner_base64, render_html
from utils.detection import run_inference, draw_overlay
from utils.export import generate_csv_report, generate_pdf_report
from utils.insights import summarize_lot, LotSummary, SlotResult

ASSETS_DIR = Path("assets")
REAL_IMAGE_PATH = ASSETS_DIR / "real_lot.jpg"
REAL_POS_PATH = ASSETS_DIR / "real_slot_positions.json"
DEMO_IMAGE_PATH = ASSETS_DIR / "demo_parking_lot.jpg"
DEMO_POS_PATH = ASSETS_DIR / "slot_positions_demo.json"


@st.cache_data
def get_image_hash(image_bytes: bytes) -> str:
    """Computes SHA-256 hash of an image for inference caching."""
    return hashlib.sha256(image_bytes).hexdigest()


def pil_to_base64_jpg(img: Image.Image, quality: int = 88) -> str:
    """Encodes a PIL image to base64 JPEG string for fast inline HTML rendering."""
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=quality)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def render_dashboard_view(model: Any, demo_mode: bool) -> None:
    """Renders the main high-fidelity parking analytics dashboard."""
    is_guest = st.session_state.get("is_guest", False)
    user = st.session_state.get("user") or {}

    if is_guest:
        display_name = "Guest"
        initials = "G"
    else:
        display_name = user.get("full_name") or user.get("email") or "User"
        name_parts = display_name.split()
        initials = "".join([p[0].upper() for p in name_parts[:2]]) if name_parts else "U"

    # -------------------------------------------------------------------------
    # 1. REAL CURRENT TIME GREETING & CLOCK
    # -------------------------------------------------------------------------
    now = datetime.datetime.now()
    hour = now.hour
    if hour < 12:
        greeting = "Good Morning"
    elif hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    formatted_date = now.strftime("%a, %d %b %Y")
    formatted_time = now.strftime("%I:%M %p")

    render_html(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 14px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.65rem;">👋</span>
                    <span style="font-size: 1.65rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                        {greeting}, {display_name}
                    </span>
                </div>
                <div style="color: #94a3b8; font-size: 0.88rem; margin-top: 3px; font-weight: 500;">
                    Smart parking. Smarter cities.
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div class="pv-header-chip">
                    <span style="font-size: 1.05rem;">🕒</span>
                    <div>
                        <div style="font-size: 0.82rem; font-weight: 700; color: #f1f5f9;">{formatted_date}</div>
                        <div style="font-size: 0.68rem; color: #94a3b8;">{formatted_time}</div>
                    </div>
                </div>
                <div class="pv-avatar-chip">
                    {initials}
                </div>
            </div>
        </div>
        """
    )

    # -------------------------------------------------------------------------
    # 2. IMAGE SELECTION & INFERENCE CONTROLS
    # -------------------------------------------------------------------------
    with st.expander("⚙️ Image Ingestion & Detection Sensitivity Controls", expanded=False):
        c_in1, c_in2, c_in3 = st.columns([1.5, 1.2, 1.3])
        with c_in1:
            uploaded_file = st.file_uploader(
                "Upload Custom Lot Image (JPG/PNG)",
                type=["jpg", "jpeg", "png"],
                key="custom_uploader_dash",
            )
        with c_in2:
            sample_choice = st.selectbox(
                "Or Select Benchmark Sample",
                options=["Real Lot (40 Slots, PKLot perspective)", "Synthetic Demo Lot (12 Slots)"],
                index=0,
                key="sample_selector_dash",
            )
        with c_in3:
            custom_pos_file = st.file_uploader(
                "Custom slot_positions.json (Optional)",
                type=["json"],
                key="custom_positions_dash",
            )

        st.divider()

        conf_threshold = st.session_state.get("conf_threshold", 0.50)
        show_ids = st.session_state.get("show_ids", True)
        show_conf_labels = st.session_state.get("show_conf_labels", False)

        c_sl1, c_sl2, c_sl3 = st.columns([1.5, 1, 1])
        with c_sl1:
            new_conf = st.slider(
                "Decision Threshold",
                min_value=0.30,
                max_value=0.90,
                value=conf_threshold,
                step=0.05,
                key="threshold_slider_dash",
            )
            if new_conf != conf_threshold:
                st.session_state["conf_threshold"] = new_conf
                st.rerun()
        with c_sl2:
            new_show_ids = st.checkbox("Show Slot IDs on Overlay", value=show_ids, key="cb_show_ids_dash")
            if new_show_ids != show_ids:
                st.session_state["show_ids"] = new_show_ids
                st.rerun()
        with c_sl3:
            new_show_conf = st.checkbox("Show Confidence % on Overlay", value=show_conf_labels, key="cb_show_conf_dash")
            if new_show_conf != show_conf_labels:
                st.session_state["show_conf_labels"] = new_show_conf
                st.rerun()

    # -------------------------------------------------------------------------
    # 3. LOAD IMAGE & RUN INFERENCE
    # -------------------------------------------------------------------------
    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        image_name = uploaded_file.name
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        if custom_pos_file is not None:
            try:
                positions = json.load(custom_pos_file)
            except Exception:
                with open(REAL_POS_PATH, "r", encoding="utf-8") as f:
                    positions = json.load(f)
        else:
            with open(REAL_POS_PATH, "r", encoding="utf-8") as f:
                positions = json.load(f)
    elif "Synthetic Demo" in sample_choice:
        image_name = "demo_parking_lot.jpg"
        with open(DEMO_IMAGE_PATH, "rb") as f:
            image_bytes = f.read()
        pil_image = Image.open(DEMO_IMAGE_PATH).convert("RGB")
        with open(DEMO_POS_PATH, "r", encoding="utf-8") as f:
            positions = json.load(f)
    else:
        image_name = "real_lot.jpg"
        with open(REAL_IMAGE_PATH, "rb") as f:
            image_bytes = f.read()
        pil_image = Image.open(REAL_IMAGE_PATH).convert("RGB")
        with open(REAL_POS_PATH, "r", encoding="utf-8") as f:
            positions = json.load(f)

    img_np = np.array(pil_image)
    image_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    conf_threshold = st.session_state.get("conf_threshold", 0.50)
    show_ids = st.session_state.get("show_ids", True)
    show_conf_labels = st.session_state.get("show_conf_labels", False)

    img_hash = get_image_hash(image_bytes)
    cache_key = f"{img_hash}_{conf_threshold}_{len(positions)}_{demo_mode}"

    if "inference_cache" not in st.session_state:
        st.session_state["inference_cache"] = {}

    if cache_key in st.session_state["inference_cache"]:
        results = st.session_state["inference_cache"][cache_key]
    else:
        results = run_inference(image_bgr, positions, model=model, conf_threshold=conf_threshold)
        st.session_state["inference_cache"][cache_key] = results

    summary: LotSummary = summarize_lot(results)
    available_slot_ids = [r.slot_id for r in sorted(results, key=lambda x: x.slot_id) if not r.occupied]

    # Generate Annotated Overlay Image
    annotated_bgr = draw_overlay(
        image_bgr,
        positions,
        results,
        show_ids=show_ids,
        show_conf=show_conf_labels,
    )
    annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
    annotated_pil = Image.fromarray(annotated_rgb)

    # Auto-save analysis:
    # Authenticated registered users -> save to SQLite with their user_email
    # Guest users -> keep only in st.session_state (never written to SQLite)
    if is_guest:
        if "guest_analyses" not in st.session_state:
            st.session_state["guest_analyses"] = []
        last_saved_key = f"saved_{cache_key}_guest"
        if not st.session_state.get(last_saved_key, False):
            guest_rec = {
                "id": len(st.session_state["guest_analyses"]) + 1,
                "user_id": None,
                "user_email": "guest@parkvision.ai",
                "image_name": image_name,
                "total_slots": summary.total_slots,
                "occupied_slots": summary.occupied_slots,
                "available_slots": summary.available_slots,
                "occupancy_pct": summary.occupancy_pct,
                "congestion": summary.congestion,
                "recommendation": summary.recommendation,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            st.session_state["guest_analyses"].insert(0, guest_rec)
            st.session_state[last_saved_key] = True
    else:
        user_email = user.get("email") if user else None
        user_id_for_db = user.get("id") if user else None
        last_saved_key = f"saved_{cache_key}_{user_email}"
        if not st.session_state.get(last_saved_key, False) and user_email:
            try:
                save_analysis(
                    user_id=user_id_for_db,
                    user_email=user_email,
                    image_name=image_name,
                    total_slots=summary.total_slots,
                    occupied_slots=summary.occupied_slots,
                    available_slots=summary.available_slots,
                    occupancy_pct=summary.occupancy_pct,
                    congestion=summary.congestion,
                    recommendation=summary.recommendation,
                )
                st.session_state[last_saved_key] = True
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # 4. PANORAMIC HERO BANNER
    # -------------------------------------------------------------------------
    banner_b64 = get_dash_banner_base64()
    bg_style = (
        f"background-image: linear-gradient(90deg, rgba(3, 9, 24, 0.92) 0%, rgba(3, 9, 24, 0.85) 35%, rgba(3, 9, 24, 0.60) 60%, rgba(3, 9, 24, 0.30) 100%), url('data:image/jpeg;base64,{banner_b64}');"
        if banner_b64
        else "background: rgba(3, 9, 24, 0.85);"
    )

    render_html(
        f"""
        <div class="pv-hero-banner" style="{bg_style}">
            <div style="display: flex; align-items: center; gap: 16px; z-index: 2;">
                <div class="pv-hero-icon-box" style="background: linear-gradient(135deg, rgba(0, 140, 255, 0.35) 0%, rgba(0, 70, 180, 0.6) 100%); border: 1.8px solid #00d2ff; box-shadow: 0 0 22px rgba(0, 210, 255, 0.6), inset 0 0 10px rgba(0, 210, 255, 0.3); display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 1.55rem; filter: drop-shadow(0 0 8px rgba(0, 210, 255, 0.8)); line-height: 1;">📷</span>
                </div>
                <div>
                    <div style="font-size: 0.82rem; font-weight: 700; color: #38bdf8; letter-spacing: 0.04em;">ParkVision AI</div>
                    <div style="font-size: 1.45rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em; margin: 2px 0 3px 0;">
                        Instant analysis of uploaded images
                    </div>
                    <div style="font-size: 0.82rem; color: #94a3b8; font-weight: 500;">
                        Monitor. Analyse. Optimise. — Smarter parking for a better tomorrow.
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 14px; z-index: 2;">
                <div style="background: rgba(2, 6, 18, 0.88); border: 1.5px solid rgba(0, 140, 255, 0.35); border-radius: 10px; padding: 7px 14px; font-size: 0.78rem; color: #cbd5e1;">
                    Target: <b style="color: #00d2ff;">{image_name}</b>
                </div>
            </div>
        </div>
        """
    )

    # -------------------------------------------------------------------------
    # 5. 4 KPI METRIC CARDS COMPUTED FROM CURRENT ANALYSIS
    # -------------------------------------------------------------------------
    total_val = summary.total_slots
    occ_val = summary.occupied_slots
    avail_val = summary.available_slots
    rate_val = f"{summary.occupancy_pct:.1f}%"

    render_html(
        f"""
        <div class="pv-kpi-v2-grid">
            <div class="pv-kpi-v2-card">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="pv-kpi-icon-circle" style="background: rgba(0, 140, 255, 0.14); border: 1px solid rgba(0, 180, 255, 0.35); color: #00d2ff;">
                        🚗
                    </div>
                    <div>
                        <div class="pv-kpi-v2-title">TOTAL CAPACITY</div>
                        <div class="pv-kpi-v2-val" style="color: #ffffff;">{total_val}</div>
                        <div class="pv-kpi-v2-sub">Total calibrated bays</div>
                    </div>
                </div>
            </div>
            <div class="pv-kpi-v2-card">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="pv-kpi-icon-circle" style="background: rgba(239, 68, 68, 0.14); border: 1px solid rgba(239, 68, 68, 0.35); color: #f87171;">
                        🚗
                    </div>
                    <div>
                        <div class="pv-kpi-v2-title">OCCUPIED BAYS</div>
                        <div class="pv-kpi-v2-val" style="color: #f87171;">{occ_val}</div>
                        <div class="pv-kpi-v2-sub">Vehicles detected</div>
                    </div>
                </div>
            </div>
            <div class="pv-kpi-v2-card">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="pv-kpi-icon-circle" style="background: rgba(16, 185, 129, 0.14); border: 1px solid rgba(16, 185, 129, 0.35); color: #34d399;">
                        🅿️
                    </div>
                    <div>
                        <div class="pv-kpi-v2-title">AVAILABLE BAYS</div>
                        <div class="pv-kpi-v2-val" style="color: #34d399;">{avail_val}</div>
                        <div class="pv-kpi-v2-sub">Open for parking</div>
                    </div>
                </div>
            </div>
            <div class="pv-kpi-v2-card">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="pv-kpi-icon-circle" style="background: rgba(168, 85, 247, 0.14); border: 1px solid rgba(168, 85, 247, 0.35); color: #c084fc;">
                        %
                    </div>
                    <div>
                        <div class="pv-kpi-v2-title">OCCUPANCY RATE</div>
                        <div class="pv-kpi-v2-val" style="color: #c084fc;">{rate_val}</div>
                        <div class="pv-kpi-v2-sub">Current lot saturation</div>
                    </div>
                </div>
            </div>
        </div>
        """
    )

    # -------------------------------------------------------------------------
    # 6. SIDE-BY-SIDE ORIGINAL VS ANNOTATED IMAGES
    # -------------------------------------------------------------------------
    render_html(
        """
        <div style="margin-top: 14px; margin-bottom: 8px;">
            <div class="pv-panel-title">
                <span>🔍</span>
                <span>Visual Inference Inspection • Original vs. Classified Overlay</span>
            </div>
        </div>
        """
    )

    col_img_orig, col_img_anno = st.columns(2)

    with col_img_orig:
        with st.container(border=True):
            render_html(
                """
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #f1f5f9;">
                        📷 Original Camera Frame
                    </div>
                    <span style="font-size: 0.72rem; color: #94a3b8; background: rgba(255,255,255,0.06); padding: 2px 8px; border-radius: 4px;">
                        Raw Input
                    </span>
                </div>
                """
            )
            st.image(pil_image, use_container_width=True)

    with col_img_anno:
        with st.container(border=True):
            render_html(
                """
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #00d2ff;">
                        🎯 Annotated Classification Overlay
                    </div>
                    <span style="font-size: 0.72rem; color: #34d399; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); padding: 2px 8px; border-radius: 4px;">
                        MobileNetV2
                    </span>
                </div>
                """
            )
            st.image(annotated_pil, use_container_width=True)

    # -------------------------------------------------------------------------
    # 7. CONGESTION STATUS, RECOMMENDATION & OPEN-SLOT CHIPS
    # -------------------------------------------------------------------------
    col_cong, col_chips = st.columns([1.1, 1.4])

    with col_cong:
        with st.container(border=True):
            render_html("<div class='pv-panel-title' style='margin-bottom: 10px;'><span>🚦</span><span>Congestion & Routing Policy</span></div>")
            render_congestion_badge(summary.congestion)
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            render_recommendation_card(summary)

    with col_chips:
        with st.container(border=True):
            render_html(
                f"""
                <div class="pv-panel-header" style="margin-bottom: 10px;">
                    <div class="pv-panel-title">
                        <span>🅿️</span>
                        <span>Available Parking Bays ({len(available_slot_ids)})</span>
                    </div>
                    <span style="font-size: 0.74rem; color: #34d399; font-weight: 600;">Ready to Park</span>
                </div>
                """
            )
            if available_slot_ids:
                chips_html = "".join(
                    f'<span class="pv-slot-chip">Bay {sid:02d}</span>'
                    for sid in available_slot_ids
                )
                render_html(f'<div class="pv-slot-chips-wrap">{chips_html}</div>')
            else:
                render_html('<div style="color: #f87171; font-size: 0.85rem; padding: 12px 0;">⚠️ No vacant bays currently available. Facility is at 100% capacity.</div>')

    # -------------------------------------------------------------------------
    # 8. INTERACTIVE SCHEMATIC SLOT GRID
    # -------------------------------------------------------------------------
    with st.container(border=True):
        render_html(
            """
            <div class="pv-panel-header" style="margin-bottom: 8px;">
                <div class="pv-panel-title">
                    <span>🗺️</span>
                    <span>Interactive Bay Schematic Grid</span>
                </div>
                <div style="display: flex; gap: 14px; font-size: 0.76rem;">
                    <span><span style="color: #10b981;">●</span> Vacant</span>
                    <span><span style="color: #ef4444;">●</span> Occupied</span>
                </div>
            </div>
            """
        )
        render_slot_map(results)

    # -------------------------------------------------------------------------
    # 9. PER-SLOT DETAILED RESULTS TABLE
    # -------------------------------------------------------------------------
    with st.container(border=True):
        render_html(
            """
            <div class="pv-panel-header" style="margin-bottom: 10px;">
                <div class="pv-panel-title">
                    <span>📋</span>
                    <span>Per-Slot Classification Audit Table</span>
                </div>
            </div>
            """
        )

        filter_sel = st.segmented_control(
            "Filter Slots",
            options=["All Slots", "Available Only", "Occupied Only"],
            default="All Slots",
            key="slot_table_filter",
            label_visibility="collapsed",
        ) or "All Slots"

        table_data = []
        for r in sorted(results, key=lambda x: x.slot_id):
            if filter_sel == "Available Only" and r.occupied:
                continue
            if filter_sel == "Occupied Only" and not r.occupied:
                continue

            status_str = "Occupied" if r.occupied else "Available"
            badge_color = "#ef4444" if r.occupied else "#10b981"
            bg_color = "rgba(239, 68, 68, 0.12)" if r.occupied else "rgba(16, 185, 129, 0.12)"

            table_data.append({
                "Slot ID": f"Bay {r.slot_id:02d}",
                "Status": status_str,
                "Confidence": f"{r.confidence * 100:.1f}%",
                "Occupied Flag": r.occupied,
                "Badge Color": badge_color,
                "Bg Color": bg_color,
            })

        if table_data:
            rows_html = ""
            for item in table_data:
                rows_html += f"""
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); color: #f1f5f9;">
                    <td style="padding: 9px 12px; font-weight: 700; color: #00d2ff;">{item['Slot ID']}</td>
                    <td style="padding: 9px 12px;">
                        <span style="background: {item['Bg Color']}; color: {item['Badge Color']}; border: 1px solid {item['Badge Color']}40; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;">
                            {item['Status']}
                        </span>
                    </td>
                    <td style="padding: 9px 12px; font-weight: 600; color: #cbd5e1;">{item['Confidence']}</td>
                </tr>
                """

            render_html(
                f"""
                <div style="overflow-x: auto; max-height: 280px;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.82rem;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(0, 140, 255, 0.25); color: #94a3b8; text-align: left;">
                                <th style="padding: 8px 12px;">Slot ID</th>
                                <th style="padding: 8px 12px;">Status</th>
                                <th style="padding: 8px 12px;">Confidence</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
                """
            )
        else:
            st.info("No slots match the selected filter.")

    # -------------------------------------------------------------------------
    # 10. EXPORT REPORT CENTER
    # -------------------------------------------------------------------------
    with st.container(border=True):
        render_html(
            """
            <div class="pv-panel-header" style="margin-bottom: 12px;">
                <div class="pv-panel-title">
                    <span>📄</span>
                    <span>Executive Exports & Verification Artifacts</span>
                </div>
            </div>
            """
        )

        buf = io.BytesIO()
        annotated_pil.save(buf, format="PNG")
        annotated_bytes = buf.getvalue()

        c_dl_img, c_dl_pdf, c_dl_csv = st.columns(3)
        with c_dl_img:
            st.download_button(
                "📥 Download Annotated PNG",
                data=annotated_bytes,
                file_name=f"annotated_{Path(image_name).stem}.png",
                mime="image/png",
                use_container_width=True,
                key="btn_dl_annotated_png",
            )
        with c_dl_pdf:
            try:
                pdf_bytes = generate_pdf_report(summary, annotated_pil, image_name)
                st.download_button(
                    "📄 Download 1-Page PDF Audit",
                    data=pdf_bytes,
                    file_name=f"ParkVision_Audit_{Path(image_name).stem}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="btn_dl_pdf_report",
                )
            except Exception as e:
                st.button(f"PDF Export Error: {e}", disabled=True, use_container_width=True)
        with c_dl_csv:
            csv_str = generate_csv_report(results, positions)
            st.download_button(
                "📊 Export Slot Results CSV",
                data=csv_str,
                file_name=f"slots_{Path(image_name).stem}.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_dl_csv_report",
            )

    # -------------------------------------------------------------------------
    # 11. GLOBAL FOOTER
    # -------------------------------------------------------------------------
    render_html(
        """
        <div class="pv-global-footer">
            <span>⚙️ Powered by AI</span>
            <span style="color: #334155;">|</span>
            <span>Instant analysis of uploaded images</span>
        </div>
        """
    )
