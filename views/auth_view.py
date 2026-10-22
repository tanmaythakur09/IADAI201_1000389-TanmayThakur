"""
Split-screen Authentication Gate view for ParkVision AI.
High-fidelity cybernetic glassmorphism theme matching the UI design specification.
Includes brand hero on the left with vector graphics and Sign In / Sign Up / Guest Access on the right.
"""

import textwrap
import streamlit as st
import streamlit.components.v1 as components
from auth.security import verify_password, hash_password, PBKDF2_ITERATIONS
from auth.validation import validate_email, evaluate_password_strength, validate_signup
from auth.session import (
    check_lockout,
    record_failed_login,
    reset_failed_login,
    login_user,
    login_as_guest,
)
from db.database import get_user_by_email, create_user
from ui.theme import render_html


def render_auth_view() -> None:
    """Renders the split-screen landing page and auth card."""
    col_hero, col_auth = st.columns([1.22, 0.88], gap="large")

    with col_hero:
        hero_html = textwrap.dedent(
            """
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
            <style>
                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }
                body {
                    background: transparent !important;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    color: #f9fafb;
                    overflow: visible;
                }
                .pv-benefit-pill {
                    display: flex;
                    align-items: flex-start;
                    gap: 16px;
                    background: rgba(8, 20, 42, 0.78);
                    border: 1px solid rgba(56, 189, 248, 0.25);
                    border-radius: 14px;
                    padding: 13px 18px;
                    backdrop-filter: blur(16px);
                    -webkit-backdrop-filter: blur(16px);
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 15px rgba(0, 140, 255, 0.08);
                    transition: all 0.25s ease;
                }
                .pv-benefit-pill:hover {
                    background: rgba(14, 34, 70, 0.85);
                    border-color: rgba(56, 189, 248, 0.5);
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 180, 255, 0.2);
                    transform: translateX(4px);
                }
                .pv-benefit-icon-box {
                    width: 44px;
                    height: 44px;
                    min-width: 44px;
                    border-radius: 11px;
                    background: rgba(12, 30, 60, 0.85);
                    border: 1.5px solid rgba(56, 189, 248, 0.38);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 0 12px rgba(0, 180, 255, 0.18);
                }
                .pv-pipeline-card {
                    background: rgba(8, 20, 42, 0.78);
                    border: 1px solid rgba(56, 189, 248, 0.25);
                    border-radius: 14px;
                    padding: 14px 20px 16px 20px;
                    backdrop-filter: blur(16px);
                    -webkit-backdrop-filter: blur(16px);
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 15px rgba(0, 140, 255, 0.08);
                    margin-top: 12px;
                }
                .pv-flow-step {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                }
                .pv-flow-icon {
                    width: 40px;
                    height: 40px;
                    border-radius: 10px;
                    border: 1.5px solid rgba(56, 189, 248, 0.35);
                    background: rgba(12, 30, 60, 0.85);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 6px;
                    box-shadow: 0 0 12px rgba(0, 180, 255, 0.16);
                }
                .pv-demo-bar {
                    background: rgba(8, 20, 42, 0.82);
                    border: 1px solid rgba(56, 189, 248, 0.28);
                    border-radius: 14px;
                    padding: 10px 14px;
                    margin-top: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    flex-wrap: nowrap;
                    gap: 10px;
                    backdrop-filter: blur(16px);
                    -webkit-backdrop-filter: blur(16px);
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 15px rgba(0, 140, 255, 0.08);
                }
            </style>
            </head>
            <body>
            <div style="position: relative; width: 100%; min-width: 600px;">
                <!-- Total Spaces HUD Telemetry Card: Moved to the right with vertical line and glowing dot -->
                <div style="position: absolute; left: 395px; top: 12px; width: 156px; background: rgba(8, 20, 42, 0.88); border: 1.5px solid rgba(56, 189, 248, 0.40); border-radius: 14px; padding: 11px 14px; box-shadow: 0 12px 30px rgba(0,0,0,0.7), 0 0 20px rgba(0,180,255,0.22); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); z-index: 10;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="background: #0284c7; color: #fff; width: 25px; height: 25px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.82rem; box-shadow: 0 0 10px rgba(2, 132, 199, 0.6);">P</span>
                        <div>
                            <div style="font-size: 0.65rem; color: #38bdf8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em; margin-bottom: 2px;">TOTAL SPACES</div>
                            <div style="font-size: 1.25rem; font-weight: 800; color: #fff; line-height: 1.1;">40</div>
                        </div>
                    </div>
                    <div style="height: 1px; background: rgba(56, 189, 248, 0.22); margin: 8px 0;"></div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.74rem; color: #cbd5e1; margin-bottom: 4px;">
                        <span><span style="color: #10b981; font-size: 0.80rem; margin-right: 5px;">●</span>Available</span>
                        <b style="color: #fff; font-weight: 700;">12</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.74rem; color: #cbd5e1;">
                        <span><span style="color: #3b82f6; font-size: 0.80rem; margin-right: 5px;">●</span>Occupied</span>
                        <b style="color: #fff; font-weight: 700;">28</b>
                    </div>
                    <!-- Indicator Line pointing straight down into the lot -->
                    <div style="position: absolute; bottom: -52px; left: 50%; transform: translateX(-50%); width: 1.5px; height: 52px; background: linear-gradient(180deg, rgba(0, 180, 255, 0.85) 0%, rgba(0, 180, 255, 0.15) 100%);"></div>
                    <!-- Glowing Dot at the tip -->
                    <div style="position: absolute; bottom: -56px; left: 50%; transform: translateX(-50%); width: 6px; height: 6px; border-radius: 50%; background: #00d2ff; box-shadow: 0 0 10px #00d2ff, 0 0 4px #ffffff;"></div>
                </div>

                <!-- Left Content Column -->
                <div style="max-width: 440px;">
                    <!-- Brand Title & Subtitle -->
                    <div style="margin-bottom: 20px;">
                        <!-- Logo & Wordmark with Car Emoji -->
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                            <span style="font-size: 2.35rem; line-height: 1; display: inline-flex; align-items: center; filter: drop-shadow(0 0 14px rgba(239, 68, 68, 0.5));">🚗</span>
                            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.02em; line-height: 1; display: inline-flex; align-items: center; gap: 8px;">
                                <span style="color: #ffffff; text-shadow: 0 2px 14px rgba(0, 0, 0, 0.95), 0 0 24px rgba(0, 0, 0, 0.9);">ParkVision</span>
                                <span style="color: #00d2ff; text-shadow: 0 0 16px rgba(0, 210, 255, 0.65), 0 2px 14px rgba(0, 0, 0, 0.95);">AI</span>
                            </h1>
                        </div>

                        <p style="font-size: 0.95rem; color: #cbd5e1; font-weight: 500; margin-top: 6px; margin-bottom: 0; line-height: 1.4; max-width: 320px; text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);">
                            Intelligent Urban Parking Analytics &amp; Space Optimisation Platform
                        </p>
                    </div>

                    <!-- 3 Benefit Pills -->
                    <div style="margin-bottom: 12px; display: flex; flex-direction: column; gap: 10px;">
                        <div class="pv-benefit-pill">
                            <div class="pv-benefit-icon-box" style="font-size: 1.25rem;">
                                🖼️
                            </div>
                            <div>
                                <div style="color: #ffffff; font-size: 0.94rem; font-weight: 700;">Instant Analysis of Uploaded Images</div>
                                <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 3px; line-height: 1.35;">
                                    MobileNetV2 transfer learning architecture delivers high-throughput slot classification with 99.2% test accuracy.
                                </div>
                            </div>
                        </div>

                        <div class="pv-benefit-pill">
                            <div class="pv-benefit-icon-box" style="font-size: 1.25rem;">
                                📊
                            </div>
                            <div>
                                <div style="color: #ffffff; font-size: 0.94rem; font-weight: 700;">Multi-Tier Congestion Analytics</div>
                                <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 3px; line-height: 1.35;">
                                    Dynamic occupancy thresholds (Low &lt;40%, Moderate 40-75%, High &gt;75%) with smart routing recommendations.
                                </div>
                            </div>
                        </div>

                        <div class="pv-benefit-pill">
                            <div class="pv-benefit-icon-box" style="font-size: 1.25rem;">
                                🛡️
                            </div>
                            <div>
                                <div style="color: #ffffff; font-size: 0.94rem; font-weight: 700;">Salted PBKDF2 Password Hashing</div>
                                <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 3px; line-height: 1.35;">
                                    PBKDF2 + HMAC-SHA256 salted credentials with __PBKDF2_ITERATIONS__ iterations, rate-limiting lockout protection, and local SQLite session persistence.
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Pipeline Workflow Card -->
                    <div class="pv-pipeline-card">
                        <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.12em; color: #00d2ff; font-weight: 700; margin-bottom: 14px;">
                            Pipeline Workflow
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div class="pv-flow-step">
                                <div class="pv-flow-icon" style="font-size: 1.15rem;">
                                    📷
                                </div>
                                <span style="font-size: 0.76rem; color: #cbd5e1; font-weight: 500; text-align: center; line-height: 1.2;">Ingest Lot<br>Image</span>
                            </div>
                            <span style="color: #0284c7; font-size: 1.15rem; margin-bottom: 18px;">➔</span>
                            <div class="pv-flow-step">
                                <div class="pv-flow-icon" style="font-size: 1.15rem;">
                                    ✂️
                                </div>
                                <span style="font-size: 0.76rem; color: #cbd5e1; font-weight: 500; text-align: center; line-height: 1.2;">Crop<br>Slots</span>
                            </div>
                            <span style="color: #0284c7; font-size: 1.15rem; margin-bottom: 18px;">➔</span>
                            <div class="pv-flow-step">
                                <div class="pv-flow-icon" style="font-size: 1.15rem;">
                                    🧠
                                </div>
                                <span style="font-size: 0.76rem; color: #cbd5e1; font-weight: 500; text-align: center; line-height: 1.2;">AI<br>Classification</span>
                            </div>
                            <span style="color: #0284c7; font-size: 1.15rem; margin-bottom: 18px;">➔</span>
                            <div class="pv-flow-step">
                                <div class="pv-flow-icon" style="font-size: 1.15rem;">
                                    📍
                                </div>
                                <span style="font-size: 0.76rem; color: #cbd5e1; font-weight: 500; text-align: center; line-height: 1.2;">Space<br>Guidance</span>
                            </div>
                        </div>
                    </div>

                    <!-- Pre-Seeded Demo Account Bar -->
                    <div class="pv-demo-bar">
                        <div style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0;">
                            <div style="width: 32px; height: 32px; border-radius: 50%; background: rgba(12, 30, 60, 0.85); border: 1.5px solid rgba(56, 189, 248, 0.4); display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px rgba(0, 180, 255, 0.2); flex-shrink: 0;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                    <circle cx="12" cy="7" r="4"></circle>
                                </svg>
                            </div>
                            <div style="min-width: 0; flex: 1;">
                                <div style="color: #38bdf8; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; line-height: 1.2;">
                                    Pre-Seeded Demo Account
                                </div>
                                <div style="color: #f1f5f9; font-size: 0.72rem; font-family: 'JetBrains Mono', monospace; margin-top: 2px; white-space: nowrap;">
                                    demo@parkvision.ai &nbsp;<span style="color: rgba(255,255,255,0.25);">|</span>&nbsp; <span style="white-space: nowrap;"><span style="color: #94a3b8;">Password:</span> <span style="color: #93c5fd;">Demo@1234</span></span>
                                </div>
                            </div>
                        </div>
                        <span style="background: #0284c7; color: #ffffff; font-size: 0.70rem; font-weight: 700; padding: 4px 10px; border-radius: 6px; letter-spacing: 0.06em; box-shadow: 0 0 14px rgba(2, 132, 199, 0.6); flex-shrink: 0; align-self: center;">
                            READY
                        </span>
                    </div>
                </div>
            </div>
            </body>
            </html>
            """
        )
        hero_html = hero_html.replace("__PBKDF2_ITERATIONS__", f"{PBKDF2_ITERATIONS:,}")
        components.html(hero_html, height=680, scrolling=False)

    with col_auth:
        auth_tab1, auth_tab2 = st.tabs(["Sign In", "Create Account"])

        # -----------------------------
        # SIGN IN TAB
        # -----------------------------
        with auth_tab1:
            is_locked, remaining_sec = check_lockout()

            if is_locked:
                mins = remaining_sec // 60
                secs = remaining_sec % 60
                st.error(
                    f"⛔ Account access locked due to 5 consecutive failed attempts. "
                    f"Please wait **{mins:02d}:{secs:02d}** before trying again.",
                    icon="🔒",
                )
            else:
                with st.form("signin_form", clear_on_submit=False, border=False):
                    email_in = st.text_input(
                        "Work Email",
                        placeholder="analyst@company.com",
                        key="signin_email",
                    )
                    pwd_in = st.text_input(
                        "Password",
                        type="default" if st.session_state.get("signin_show_pwd") else "password",
                        placeholder="Enter password",
                        key="signin_pwd",
                    )
                    show_pwd = st.checkbox("Show password", key="signin_show_pwd")

                    submit_signin = st.form_submit_button("→   Sign In to Console", use_container_width=True, type="primary")

                    if submit_signin:
                        if not email_in or not pwd_in:
                            st.warning("Please provide both email and password.", icon="⚠️")
                        else:
                            user = get_user_by_email(email_in)
                            if user and verify_password(pwd_in, user["password_hash"], user["salt"]):
                                login_user(user)
                                st.toast(f"Welcome back, {user['full_name']}!", icon="👋")
                                st.rerun()
                            else:
                                attempts, lockout_dur = record_failed_login()
                                if lockout_dur:
                                    st.error("Too many failed attempts. Locked for 5 minutes.", icon="🔒")
                                    st.rerun()
                                else:
                                    remaining = 5 - attempts
                                    st.error(
                                        f"Invalid email or password. ({remaining} attempt{'s' if remaining != 1 else ''} remaining before temporary lockout)",
                                        icon="❌",
                                    )

        # -----------------------------
        # SIGN UP TAB
        # -----------------------------
        with auth_tab2:
            with st.form("signup_form", clear_on_submit=False, border=False):
                new_name = st.text_input("Full Name", placeholder="Jane Doe", key="signup_name")
                new_email = st.text_input("Work Email", placeholder="jane@company.com", key="signup_email")

                new_pwd = st.text_input(
                    "Password (min. 8 characters)",
                    type="default" if st.session_state.get("signup_show_pwd") else "password",
                    placeholder="Create a strong password",
                    key="signup_pwd",
                )
                new_pwd_confirm = st.text_input(
                    "Confirm Password",
                    type="default" if st.session_state.get("signup_show_pwd") else "password",
                    placeholder="Re-enter password",
                    key="signup_pwd_confirm",
                )
                show_signup_pwd = st.checkbox("Show passwords", key="signup_show_pwd")

                # Real-time password strength indicator
                if new_pwd:
                    eval_res = evaluate_password_strength(new_pwd)
                    strength_html = textwrap.dedent(
                        f"""
                        <div style="margin: 8px 0 12px 0;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
                                <span style="color: #9ca3af;">Strength: <b style="color: {eval_res['color']}">{eval_res['label']}</b></span>
                                <span style="color: #9ca3af;">{eval_res['percentage']}%</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; overflow: hidden;">
                                <div style="background: {eval_res['color']}; width: {eval_res['percentage']}%; height: 100%; transition: width 0.3s ease;"></div>
                            </div>
                        </div>
                        """
                    )
                    render_html(strength_html)

                submit_signup = st.form_submit_button("Create Account", use_container_width=True, type="primary")

                if submit_signup:
                    is_valid, err_msg = validate_signup(new_name, new_email, new_pwd, new_pwd_confirm)
                    if not is_valid:
                        st.error(err_msg, icon="⚠️")
                    else:
                        existing = get_user_by_email(new_email)
                        if existing:
                            st.error("An account with this email address already exists. Please sign in instead.", icon="❌")
                        else:
                            p_hash, salt = hash_password(new_pwd)
                            user_id = create_user(new_name, new_email, p_hash, salt)
                            st.success("Account created successfully! You can now sign in.", icon="🎉")
                            st.balloons()

        # Clean "OR" divider matching reference mockup
        or_divider_html = textwrap.dedent(
            """
            <div style="display: flex; align-items: center; text-align: center; margin: 20px 0 16px 0;">
                <div style="flex-grow: 1; border-bottom: 1px solid rgba(255, 255, 255, 0.1);"></div>
                <span style="padding: 0 14px; color: #64748b; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.05em;">OR</span>
                <div style="flex-grow: 1; border-bottom: 1px solid rgba(255, 255, 255, 0.1);"></div>
            </div>
            """
        )
        render_html(or_divider_html)

        # Prominent Guest Access Button
        if st.button("👤   Continue as Guest", use_container_width=True):
            login_as_guest()
            st.toast("Entered as Guest Analyst", icon="👋")
            st.rerun()

        footer_info_html = textwrap.dedent(
            """
            <div style="display: flex; align-items: flex-start; gap: 10px; margin-top: 16px;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0; margin-top: 2px;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                <span style="color: #94a3b8; font-size: 0.78rem; line-height: 1.45;">
                    Guest sessions enjoy full vision detection and reporting features, but historical analyses are not saved.
                </span>
            </div>
            """
        )
        render_html(footer_info_html)
