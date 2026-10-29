"""
ParkVision AI — Intelligent Urban Parking Analytics & Space Optimisation Platform
UrbanFlow AI Pvt. Ltd. / ParkSmart AI
Modern Glassmorphism Edition

Main application entrypoint and router for Streamlit Community Cloud.
"""

import warnings
from pathlib import Path
import streamlit as st

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*use_container_width.*")

import importlib
from auth.session import init_session_state, logout
from db.database import init_db
import ui.theme
import ui.components
import views.about_view
import views.analytics_view
import views.auth_view
import views.dashboard_view
import views.feedback_view
import views.insights_view

# Force hot-reload of submodules so changes reflect immediately without restarting server
importlib.reload(ui.theme)
importlib.reload(ui.components)
importlib.reload(views.about_view)
importlib.reload(views.analytics_view)
importlib.reload(views.auth_view)
importlib.reload(views.dashboard_view)
importlib.reload(views.feedback_view)
importlib.reload(views.insights_view)

from ui.theme import apply_theme
from views.about_view import render_about_view
from views.analytics_view import render_analytics_view
from views.auth_view import render_auth_view
from views.dashboard_view import render_dashboard_view
from views.feedback_view import render_feedback_view
from views.insights_view import render_insights_view
import streamlit.components.v1 as components
import textwrap

MODEL_PATH = Path("model/parking_classifier.keras")

# Streamlit Page Configuration
st.set_page_config(
    page_title="ParkVision AI — Smart Parking Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Database & Demo Account (cached once per server process)
@st.cache_resource
def setup_database():
    return init_db()

db_ready = setup_database()
if not db_ready:
    st.warning("Accounts are temporarily unavailable. Guest mode still works.")

# Initialize Session State
init_session_state()


# Cached Model Loader (lazy-load TensorFlow to save RAM & fast cold start)
@st.cache_resource
def load_model():
    """Loads and caches the trained MobileNetV2 Keras model."""
    if not MODEL_PATH.exists():
        return None
    try:
        import tensorflow as tf

        return tf.keras.models.load_model(MODEL_PATH)
    except Exception as e:
        st.sidebar.error(f"Error loading model: {e}")
        return None


# --------------------------------------------------------------------------
# Main Execution Flow
# --------------------------------------------------------------------------
is_authenticated = st.session_state.get("authenticated", False)

if not is_authenticated:
    # AUTHENTICATION GATE
    apply_theme(is_auth_page=True)
    render_auth_view()
else:
    # AUTHENTICATED APP SHELL
    apply_theme(is_auth_page=False)

    model = load_model()
    demo_mode = model is None

    user = st.session_state.get("user") or {}
    is_guest = st.session_state.get("is_guest", False)
    if is_guest:
        user_name = "Guest Visitor"
        user_email = "guest@parkvision.ai"
        initials = "G"
    else:
        user_name = user.get("full_name") or user.get("email") or "User"
        user_email = user.get("email") or ""
        name_parts = user_name.split()
        initials = "".join([p[0].upper() for p in name_parts[:2]]) if name_parts else "U"

    # Top Sidebar: Logo, Brand Tag, and User Profile Card (placed above Dashboard navigation)
    with st.sidebar:
        role_badge = (
            '<div><span style="background: rgba(234, 179, 8, 0.14); color: #fbbf24; border: 1.5px solid rgba(245, 158, 11, 0.50); font-size: 0.68rem; font-weight: 800; padding: 3px 8px; border-radius: 5px; letter-spacing: 0.04em; box-shadow: 0 0 8px rgba(245, 158, 11, 0.2);">GUEST</span></div>'
            if is_guest
            else ""
        )

        top_sidebar_html = (
            '<div class="pv-sidebar-top" style="padding: 2px 2px 8px 2px;">'
            '<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px; padding-left: 2px;">'
            '<svg width="30" height="24" viewBox="0 0 48 36" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 0 8px rgba(244, 63, 94, 0.7)); flex-shrink: 0;">'
            '<path d="M6 22C6 20.5 7.2 19 9 18.5L16 13C17.5 10 20 8.5 24 8.5H35C38.5 8.5 41 10.5 42 13.5L44.5 18C46 19 47 20.5 47 22.5V26C47 27.5 46 28.5 44.5 28.5H43C42 25.5 39 23.5 36 23.5C33 23.5 30 25.5 29 28.5H19C18 25.5 15 23.5 12 23.5C9 23.5 6 25.5 5 28.5H3.5C2 28.5 1 27.5 1 26V22.5C1 21 2 20 3.5 19.5L6 22Z" fill="#f43f5e"/>'
            '<path d="M17.5 13.5L13 18.5H23V11H20C18.8 11 18 12 17.5 13.5Z" fill="#38bdf8"/>'
            '<path d="M25 11V18.5H34L39 18.5L35.5 13C35 12 34 11 32.5 11H25Z" fill="#38bdf8"/>'
            '<circle cx="45" cy="22" r="2.5" fill="#00d2ff"/>'
            '<circle cx="12" cy="28.5" r="5" fill="#090d16" stroke="#00d2ff" stroke-width="2"/>'
            '<circle cx="12" cy="28.5" r="1.8" fill="#ffffff"/>'
            '<circle cx="36" cy="28.5" r="5" fill="#090d16" stroke="#00d2ff" stroke-width="2"/>'
            '<circle cx="36" cy="28.5" r="1.8" fill="#ffffff"/>'
            '</svg>'
            '<div style="font-size: 1.28rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em; line-height: 1;">'
            'ParkVision <span style="color: #00d2ff; text-shadow: 0 0 12px rgba(0, 210, 255, 0.75);">AI</span>'
            '</div>'
            '</div>'
            '<div style="font-size: 0.65rem; color: #7094b8; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; line-height: 1.2; margin-left: 2px; margin-bottom: 11px; text-shadow: 0 0 6px rgba(0, 140, 255, 0.3);">'
            'SMART PARKING ANALYTICS'
            '</div>'
            '<div style="background: rgba(2, 6, 18, 0.90); border: 1.5px solid rgba(0, 140, 255, 0.35); box-shadow: 0 0 14px rgba(0, 140, 255, 0.14); border-radius: 10px; padding: 7px 11px; margin-bottom: 0px; display: flex; align-items: center; gap: 10px;">'
            f'<div style="width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #0056d6 0%, #0088ff 100%); color: #ffffff; font-weight: 800; font-size: 0.90rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 12px rgba(0, 140, 255, 0.6); flex-shrink: 0; border: 1.5px solid rgba(0, 210, 255, 0.6);">{initials}</div>'
            '<div style="flex: 1; min-width: 0;">'
            f'<div style="font-size: 0.94rem; font-weight: 800; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; letter-spacing: -0.01em;">{user_name}</div>'
            f'<div style="font-size: 0.74rem; color: #94a3b8; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 1px;">{user_email}</div>'
            '</div>'
            f'{role_badge}'
            '</div>'
            '</div>'
        )

        st.markdown(top_sidebar_html, unsafe_allow_html=True)


    # Page wrappers for st.navigation
    def view_dashboard():
        render_dashboard_view(model, demo_mode)

    def view_analytics():
        render_analytics_view()

    def view_insights():
        render_insights_view()

    def view_feedback():
        render_feedback_view()

    def view_about():
        render_about_view()

    # Define Flat Navigation Structure matching reference exactly
    p_dash = st.Page(view_dashboard, title="Dashboard", icon="🏠", default=True)
    p_analytics = st.Page(view_analytics, title="Historical Analytics", icon="📈")
    p_insights = st.Page(view_insights, title="Model Insights", icon="🧠")
    p_feedback = st.Page(view_feedback, title="Calibration & Feedback", icon="💬")
    p_about = st.Page(view_about, title="About Platform", icon="ℹ️")

    st.session_state["nav_pages"] = {
        "dashboard": p_dash,
        "analytics": p_analytics,
        "insights": p_insights,
        "feedback": p_feedback,
        "about": p_about,
    }

    nav = st.navigation([p_dash, p_analytics, p_insights, p_feedback, p_about])

    # Render Active Page
    nav.run()

    with st.sidebar:
        if demo_mode:
            st.markdown(
                '<div style="background: rgba(2, 6, 18, 0.90); border: 1.5px solid rgba(245, 158, 11, 0.35); box-shadow: 0 0 12px rgba(245, 158, 11, 0.14); border-radius: 9px; padding: 8px 11px; margin-top: 8px; margin-bottom: 8px;">'
                '<div style="display: flex; align-items: center; gap: 6px; color: #fbbf24; font-weight: 800; font-size: 0.78rem;"><span>⚠️</span> Demo mode (heuristic) - trained model not found</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="background: rgba(2, 6, 18, 0.90); border: 1.5px solid rgba(16, 185, 129, 0.35); box-shadow: 0 0 12px rgba(16, 185, 129, 0.16); border-radius: 9px; padding: 8px 11px; margin-top: 8px; margin-bottom: 8px;">'
                '<div style="display: flex; align-items: center; gap: 6px; color: #34d399; font-weight: 800; font-size: 0.78rem;"><span>☑</span> MobileNetV2 trained on PKLot crops - loaded</div>'
                '</div>',
                unsafe_allow_html=True,
            )

        if st.button("⟲ Sign Out", use_container_width=True):
            logout()
            st.rerun()

        st.markdown(
            '<div style="color: #64748b; font-size: 0.70rem; line-height: 1.4; margin-top: 8px; text-align: left; padding-left: 2px;">'
            'UrbanFlow AI Pvt. Ltd. • ParkVision AI v2.0<br/>'
            'SA-1 Machine Learning & Deep Learning'
            '</div>',
            unsafe_allow_html=True,
        )

