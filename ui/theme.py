"""
Design system tokens and responsive stylesheet injection for ParkVision AI.
Includes Google Fonts Inter, sleek dark theme tokens, glassmorphism cards,
micro-animations, and responsive utility classes.
"""

import streamlit as st

# Design Tokens
TOKENS = {
    "colors": {
        "primary": "#3b82f6",
        "primary_hover": "#2563eb",
        "primary_glow": "rgba(59, 130, 246, 0.35)",
        "bg_main": "#0b0f19",
        "bg_card": "rgba(17, 24, 39, 0.75)",
        "bg_card_elevated": "#1e293b",
        "border": "rgba(255, 255, 255, 0.08)",
        "border_glow": "rgba(59, 130, 246, 0.4)",
        "text_primary": "#f9fafb",
        "text_secondary": "#9ca3af",
        "text_muted": "#6b7280",
        "success": "#10b981",
        "success_bg": "rgba(16, 185, 129, 0.15)",
        "warning": "#f59e0b",
        "warning_bg": "rgba(245, 158, 11, 0.15)",
        "danger": "#ef4444",
        "danger_bg": "rgba(239, 68, 68, 0.15)",
    },
    "radius": {
        "sm": "6px",
        "md": "10px",
        "lg": "16px",
        "xl": "24px",
    },
}

CUSTOM_CSS = """
<style>
/* Import Inter and JetBrains Mono fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #f9fafb;
}

code, pre {
    font-family: 'JetBrains Mono', monospace;
}

/* Base App Background & Pitch Black Cyber Theme */
html, body, .stApp {
    background-color: #01040a !important;
    background: #01040a !important;
    color: #f8fafc !important;
}

/* Smooth Scrolling */
html {
    scroll-behavior: smooth;
}

/* Glassmorphism Card Utilities */
.pv-card {
    background: rgba(4, 11, 26, 0.72) !important;
    backdrop-filter: blur(20px) saturate(190%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(190%) !important;
    border: 1.5px solid rgba(0, 140, 255, 0.32) !important;
    border-radius: 14px !important;
    padding: 22px !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.55), 0 0 20px rgba(0, 140, 255, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.14) !important;
    margin-bottom: 16px !important;
    transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease !important;
}

.pv-card:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(0, 190, 255, 0.6) !important;
    box-shadow: 0 20px 48px rgba(0, 0, 0, 0.65), 0 0 28px rgba(0, 160, 255, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.22) !important;
}

.pv-card-highlight {
    background: linear-gradient(135deg, rgba(30, 58, 138, 0.35) 0%, rgba(4, 11, 26, 0.75) 100%) !important;
    border: 1.5px solid rgba(0, 180, 255, 0.55) !important;
    backdrop-filter: blur(20px) saturate(190%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(190%) !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.55), 0 0 30px rgba(0, 140, 255, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.18) !important;
}

/* Hero Branding Box with Animated Mesh */
.pv-hero-box {
    background: linear-gradient(-45deg, #0f172a, #1e1b4b, #172554, #0f172a);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
    border-radius: 20px;
    padding: 36px 30px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6);
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Benefit Pill in Hero */
.pv-benefit-pill {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 12px;
    transition: all 0.25s ease;
}

.pv-benefit-pill:hover {
    background: rgba(59, 130, 246, 0.1);
    border-color: rgba(59, 130, 246, 0.3);
    transform: translateX(4px);
}

/* KPI Card Grid */
.pv-kpi-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 16px;
    margin-bottom: 20px;
}

.pv-kpi-card {
    background: rgba(17, 24, 39, 0.85);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 14px;
    padding: 20px;
    text-align: left;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.pv-kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
}

.pv-kpi-label {
    font-size: 0.85rem;
    font-weight: 500;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}

.pv-kpi-val {
    font-size: 2.1rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.1;
    font-feature-settings: "tnum";
}

.pv-kpi-sub {
    font-size: 0.8rem;
    color: #6b7280;
    margin-top: 6px;
}

/* Badges for Congestion */
.pv-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.03em;
}

.pv-badge-low {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.35);
}

.pv-badge-moderate {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.35);
}

.pv-badge-high {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
}

/* Schematic Slot Map Tile Grid */
.pv-slot-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    max-height: 280px;
    overflow-y: auto;
    padding: 12px;
    background: rgba(0, 0, 0, 0.25);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.pv-slot-chip {
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: transform 0.15s ease;
}

.pv-slot-chip:hover {
    transform: scale(1.06);
}

.pv-slot-empty {
    background: rgba(16, 185, 129, 0.2);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.4);
}

.pv-slot-occupied {
    background: rgba(239, 68, 68, 0.2);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.4);
}

/* User Avatar Chip in Sidebar */
.pv-user-chip {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: rgba(3, 9, 24, 0.75);
    border: 1.5px solid rgba(0, 140, 255, 0.32);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.pv-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    color: white;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    box-shadow: 0 0 12px rgba(59, 130, 246, 0.4);
}

/* Interactive Tabs Styling */
div[data-testid="stTabs"] button[role="tab"] {
    font-size: 0.95rem;
    font-weight: 600;
    color: #9ca3af;
    padding: 10px 18px;
}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #60a5fa !important;
    border-bottom-color: #3b82f6 !important;
}

/* Buttons - Small Rectangular Boxes with Slight Glowing Effect */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    background: rgba(2, 6, 18, 0.90) !important;
    border: 1.5px solid rgba(0, 140, 255, 0.35) !important;
    color: #f1f5f9 !important;
    box-shadow: 0 0 14px rgba(0, 140, 255, 0.14) !important;
    transition: all 0.22s ease !important;
}

.stButton > button:hover {
    background: rgba(0, 110, 255, 0.18) !important;
    border-color: #00d2ff !important;
    color: #ffffff !important;
    box-shadow: 0 0 22px rgba(0, 180, 255, 0.45) !important;
    transform: translateY(-1px) !important;
}

/* Primary Form Submit Button */
button[kind="primaryFormSubmit"],
button[type="submit"],
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #0056d6 0%, #0088ff 100%) !important;
    border: 1.5px solid rgba(0, 220, 255, 0.7) !important;
    box-shadow: 0 0 22px rgba(0, 140, 255, 0.6) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
}

button[kind="primaryFormSubmit"]:hover,
button[type="submit"]:hover,
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(90deg, #0066ff 0%, #00a2ff 100%) !important;
    border-color: #ffffff !important;
    box-shadow: 0 0 30px rgba(0, 170, 255, 0.85) !important;
}

/* All Inputs & Select Dropdowns as Glowing Rectangular Boxes */
input[type="text"],
input[type="password"],
input[type="number"],
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
textarea,
div[data-testid="stFileUploader"] section {
    background: rgba(2, 6, 18, 0.90) !important;
    border: 1.5px solid rgba(0, 140, 255, 0.35) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    box-shadow: 0 0 12px rgba(0, 140, 255, 0.10) !important;
    transition: all 0.2s ease !important;
}

input[type="text"]:focus,
input[type="password"]:focus,
input[type="number"]:focus,
div[data-baseweb="input"]:focus-within > div,
div[data-baseweb="select"]:focus-within > div,
textarea:focus {
    border-color: #00d2ff !important;
    box-shadow: 0 0 18px rgba(0, 210, 255, 0.45) !important;
    outline: none !important;
}

/* Streamlit Header & Sidebar Controls (Expand & Collapse) */
header[data-testid="stHeader"],
[data-testid="stHeader"] {
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
    pointer-events: none !important;
    z-index: 999990 !important;
}

/* Ensure toolbar container is active but only unwanted controls hidden */
[data-testid="stToolbar"] {
    display: flex !important;
    background: transparent !important;
    pointer-events: none !important;
    z-index: 999990 !important;
}

[data-testid="stDeployButton"],
[data-testid="stDecoration"],
[data-testid="stMainMenu"],
#MainMenu {
    display: none !important;
    visibility: hidden !important;
}

/* Expand Sidebar Button (glowing cyber button when sidebar is collapsed/closed) */
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[aria-label="Expand sidebar"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    z-index: 999999 !important;
    position: relative !important;
}

[data-testid="stExpandSidebarButton"] button,
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button,
button[aria-label="Expand sidebar"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    background: rgba(3, 9, 24, 0.92) !important;
    border: 1.5px solid rgba(0, 190, 255, 0.65) !important;
    border-radius: 9px !important;
    color: #00d2ff !important;
    box-shadow: 0 0 18px rgba(0, 140, 255, 0.5), 0 4px 14px rgba(0, 0, 0, 0.85) !important;
    cursor: pointer !important;
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    margin: 6px 0 0 8px !important;
    padding: 6px 10px !important;
    min-height: 36px !important;
}

[data-testid="stExpandSidebarButton"] button:hover,
[data-testid="stSidebarCollapsedControl"] button:hover,
[data-testid="collapsedControl"] button:hover,
button[aria-label="Expand sidebar"]:hover {
    background: rgba(0, 110, 255, 0.3) !important;
    border-color: #00d2ff !important;
    box-shadow: 0 0 26px rgba(0, 210, 255, 0.85), 0 4px 18px rgba(0, 0, 0, 0.9) !important;
    transform: scale(1.08) !important;
    color: #ffffff !important;
}

[data-testid="stExpandSidebarButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg,
button[aria-label="Expand sidebar"] svg {
    fill: #00d2ff !important;
    color: #00d2ff !important;
    stroke: #00d2ff !important;
    filter: drop-shadow(0 0 6px rgba(0, 210, 255, 0.85)) !important;
}

/* Collapse Sidebar Button (inside sidebar header when sidebar is open) */
[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}

[data-testid="stSidebarCollapseButton"] button,
button[aria-label="Collapse sidebar"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    background: rgba(3, 9, 24, 0.75) !important;
    border: 1.5px solid rgba(0, 140, 255, 0.35) !important;
    border-radius: 8px !important;
    color: #00d2ff !important;
    box-shadow: 0 0 12px rgba(0, 140, 255, 0.25) !important;
    cursor: pointer !important;
    padding: 5px 8px !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebarCollapseButton"] button:hover,
button[aria-label="Collapse sidebar"]:hover {
    background: rgba(0, 110, 255, 0.22) !important;
    border-color: #00d2ff !important;
    box-shadow: 0 0 20px rgba(0, 210, 255, 0.7) !important;
    transform: scale(1.08) !important;
}

[data-testid="stSidebarCollapseButton"] svg,
button[aria-label="Collapse sidebar"] svg {
    fill: #00d2ff !important;
    color: #00d2ff !important;
    stroke: #00d2ff !important;
    filter: drop-shadow(0 0 6px rgba(0, 210, 255, 0.7)) !important;
}

.block-container {
    padding-top: 0.9rem !important;
    padding-bottom: 2.0rem !important;
    max-width: 1280px !important;
}

footer {
    display: none !important;
    visibility: hidden !important;
}

/* Mobile Responsive Optimization */
@media (max-width: 768px) {
    .pv-kpi-container {
        grid-template-columns: 1fr 1fr;
    }
    .pv-hero-box {
        padding: 20px 16px;
    }
    .pv-card {
        padding: 16px;
    }
}

/* Sidebar Styling to Match Cyber Dark Operations Aesthetic with Frosted Glassmorphism */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebarContent"] {
    background-color: rgba(1, 4, 12, 0.84) !important;
    background: rgba(1, 4, 12, 0.84) !important;
    backdrop-filter: blur(24px) saturate(190%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(190%) !important;
    border-right: 1.5px solid rgba(0, 140, 255, 0.25) !important;
    box-shadow: 6px 0 32px rgba(0, 0, 0, 0.85), inset -1px 0 0 rgba(255, 255, 255, 0.06) !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.6rem !important;
    padding-bottom: 0.6rem !important;
}

[data-testid="stSidebarContent"] {
    position: relative !important;
}

[data-testid="stSidebarUserContent"],
[data-testid="stSidebarUserContent"] > div,
[data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"],
[data-testid="stSidebarUserContent"] [data-testid="stElementContainer"] {
    position: static !important;
    transform: none !important;
    filter: none !important;
}

.pv-sidebar-top {
    position: absolute !important;
    top: 66px !important;
    left: 14px !important;
    right: 14px !important;
    z-index: 50 !important;
}

[data-testid="stSidebarNav"] {
    padding-top: 0 !important;
    margin-top: 194px !important;
    margin-bottom: 14px !important;
}

[data-testid="stSidebarHeader"] {
    padding-top: 8px !important;
    padding-bottom: 0 !important;
    padding-right: 12px !important;
    z-index: 1000 !important;
    background: transparent !important;
}

[data-testid="stSidebarCollapseButton"] {
    z-index: 1000 !important;
}

[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarHeader"] button {
    background: rgba(2, 6, 18, 0.85) !important;
    border: 1.5px solid rgba(0, 140, 255, 0.35) !important;
    border-radius: 8px !important;
    color: #38bdf8 !important;
    box-shadow: 0 0 10px rgba(0, 140, 255, 0.15) !important;
    cursor: pointer !important;
}

[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stSidebarHeader"] button:hover {
    background: rgba(12, 30, 60, 0.95) !important;
    border-color: rgba(0, 210, 255, 0.6) !important;
    color: #ffffff !important;
    box-shadow: 0 0 14px rgba(0, 210, 255, 0.3) !important;
}

[data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"] button {
    z-index: 1000 !important;
    cursor: pointer !important;
    background: rgba(2, 6, 18, 0.85) !important;
    border: 1.5px solid rgba(0, 140, 255, 0.35) !important;
    border-radius: 8px !important;
    color: #38bdf8 !important;
    box-shadow: 0 0 10px rgba(0, 140, 255, 0.2) !important;
}

/* Keep component iframe invisible but rendered so helper scripts execute */
[data-testid="stSidebar"] iframe {
    position: absolute !important;
    opacity: 0 !important;
    pointer-events: none !important;
    height: 1px !important;
    width: 1px !important;
    border: none !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.22rem !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
    margin-bottom: 0 !important;
}

[data-testid="stSidebarNav"] ul {
    gap: 4px !important;
    padding: 0 2px !important;
}

[data-testid="stSidebarNav"] li {
    margin-bottom: 3px !important;
}

/* Sidebar Navigation Items - Compact, Sleek, Enterprise Grade Rectangular Boxes */
[data-testid="stSidebar"]:not([data-collapsed="true"]):not([aria-expanded="false"]) {
    min-width: 255px !important;
    max-width: 270px !important;
    width: 265px !important;
}

[data-testid="stSidebar"][data-collapsed="true"],
[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 0 !important;
    width: 0 !important;
    max-width: 0 !important;
    margin-left: -320px !important;
    transform: translateX(-100%) !important;
    display: none !important;
}

[data-testid="stSidebarNav"] a,
[data-testid="stSidebarNav"] li div {
    border-radius: 9px !important;
    padding: 9px 13px !important;
    margin: 2px 2px !important;
    color: #f1f5f9 !important;
    font-weight: 600 !important;
    font-size: 0.94rem !important;
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: 1.5px solid transparent !important;
    background: transparent !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
}

[data-testid="stSidebarNav"] a span:first-child,
[data-testid="stSidebarNav"] a svg {
    filter: none !important;
    font-size: 1.15rem !important;
    transition: transform 0.2s ease !important;
}

[data-testid="stSidebarNav"] a span:last-child {
    font-size: 0.94rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    color: #f1f5f9 !important;
}

/* Hover: glowing rectangular box forms around it, crisp icon */
[data-testid="stSidebarNav"] a:hover {
    background: rgba(0, 110, 255, 0.16) !important;
    border: 1.5px solid rgba(0, 200, 255, 0.75) !important;
    box-shadow: 0 0 16px rgba(0, 140, 255, 0.40), inset 0 0 8px rgba(0, 140, 255, 0.16) !important;
    color: #ffffff !important;
    transform: translateX(2px) !important;
}

[data-testid="stSidebarNav"] a:hover span:first-child,
[data-testid="stSidebarNav"] a:hover svg {
    filter: none !important;
    transform: scale(1.06) !important;
}

/* Active / Mousedown click state - instant glowing box */
[data-testid="stSidebarNav"] a:active,
[data-testid="stSidebarNav"] a:focus-visible {
    background: rgba(0, 130, 255, 0.28) !important;
    border: 1.5px solid #00d2ff !important;
    box-shadow: 0 0 20px rgba(0, 210, 255, 0.6), inset 0 0 10px rgba(0, 210, 255, 0.25) !important;
}

/* Selected Active Page - Vibrant Electric Blue Rounded Rectangular Pill matching image */
[data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebarNav"] a:has([aria-current="page"]) {
    background: linear-gradient(90deg, #0056d6 0%, #007cf8 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border: 1.5px solid rgba(0, 220, 255, 0.85) !important;
    box-shadow: 0 0 20px rgba(0, 140, 255, 0.75), inset 0 0 10px rgba(255, 255, 255, 0.22) !important;
    transform: none !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] span:first-child,
[data-testid="stSidebarNav"] a[aria-current="page"] svg {
    filter: none !important;
    font-size: 1.18rem !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] span:last-child {
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    text-shadow: 0 0 8px rgba(255, 255, 255, 0.4) !important;
}

/* View All & View Details Interactive Header Buttons */
div.st-key-view_all_live,
div.st-key-view_all_activity,
div.st-key-view_details_section,
div.st-key-live_view_all_activity,
div.st-key-feedback_view_all {
    display: flex !important;
    justify-content: flex-end !important;
    align-items: center !important;
    margin: 0 !important;
}

div.st-key-view_all_live button,
div.st-key-view_all_activity button,
div.st-key-view_details_section button,
div.st-key-live_view_all_activity button,
div.st-key-feedback_view_all button {
    background: transparent !important;
    border: none !important;
    color: #00a8ff !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    padding: 0 !important;
    margin: 0 !important;
    min-height: unset !important;
    height: auto !important;
    line-height: normal !important;
    box-shadow: none !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

div.st-key-view_all_live button:hover,
div.st-key-view_all_activity button:hover,
div.st-key-view_details_section button:hover,
div.st-key-live_view_all_activity button:hover,
div.st-key-feedback_view_all button:hover {
    color: #38bdf8 !important;
    text-decoration: underline !important;
    text-shadow: 0 0 10px rgba(0, 180, 255, 0.75) !important;
    background: transparent !important;
}

/* Modal Dialog Dark Glassmorphism */
div[data-testid="stDialog"] div[role="dialog"] {
    background: #020714 !important;
    border: 1.5px solid rgba(0, 140, 255, 0.45) !important;
    border-radius: 16px !important;
    box-shadow: 0 0 40px rgba(0, 140, 255, 0.25), 0 20px 60px rgba(0, 0, 0, 0.95) !important;
    color: #ffffff !important;
}

div[data-testid="stDialog"] div[role="dialog"] h2 {
    color: #ffffff !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
}

/* Header Chips - Small Rectangular Boxes */
.pv-header-chip {
    background: rgba(3, 9, 24, 0.78) !important;
    border: 1.5px solid rgba(0, 140, 255, 0.35) !important;
    border-radius: 10px !important;
    padding: 7px 14px !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    backdrop-filter: blur(16px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45), 0 0 14px rgba(0, 140, 255, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
    transition: all 0.2s ease !important;
}

.pv-header-chip:hover {
    border-color: rgba(0, 190, 255, 0.6) !important;
    box-shadow: 0 0 18px rgba(0, 180, 255, 0.28) !important;
}

.pv-avatar-chip {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0284c7 0%, #0266d6 100%);
    color: #ffffff;
    font-weight: 800;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 15px rgba(2, 132, 199, 0.45);
    border: 1.5px solid rgba(255, 255, 255, 0.2);
}

/* Hero Panoramic Banner - Sleek Glowing Cyber Box with Frosted Glassmorphism */
.pv-hero-banner {
    position: relative !important;
    background-color: rgba(3, 9, 24, 0.75) !important;
    border-radius: 14px !important;
    border: 1.5px solid rgba(0, 150, 255, 0.38) !important;
    backdrop-filter: blur(22px) saturate(190%) !important;
    -webkit-backdrop-filter: blur(22px) saturate(190%) !important;
    box-shadow: 0 16px 42px rgba(0, 0, 0, 0.6), 0 0 26px rgba(0, 140, 255, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.16) !important;
    overflow: hidden !important;
    min-height: 120px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    padding: 20px 26px !important;
    margin-bottom: 20px !important;
    background-size: cover !important;
    background-position: right center !important;
    background-repeat: no-repeat !important;
}

.pv-hero-icon-box {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: rgba(0, 140, 255, 0.16);
    border: 1.5px solid rgba(0, 210, 255, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    color: #00d2ff;
    box-shadow: 0 0 20px rgba(0, 180, 255, 0.3);
    flex-shrink: 0;
}

.pv-banner-hud {
    background: rgba(3, 9, 24, 0.78);
    border: 1.5px solid rgba(0, 140, 255, 0.35);
    backdrop-filter: blur(18px) saturate(180%);
    -webkit-backdrop-filter: blur(18px) saturate(180%);
    border-radius: 12px;
    padding: 10px 18px;
    display: flex;
    align-items: center;
    gap: 18px;
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.5), 0 0 16px rgba(0, 140, 255, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.14);
}

.pv-pulsing-dot {
    width: 8px;
    height: 8px;
    background-color: #10b981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px #10b981;
    animation: pulseDot 2s infinite ease-in-out;
}

.pv-pulsing-dot-red {
    width: 8px;
    height: 8px;
    background-color: #ef4444;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px #ef4444;
    animation: pulseDot 1.5s infinite ease-in-out;
}

@keyframes pulseDot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.35; transform: scale(0.85); }
}

/* KPI V2 Grid & Cards - Small Rectangular Boxes with Slight Glowing Effect */
.pv-kpi-v2-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 22px;
}

.pv-kpi-v2-card,
.pv-kpi-card {
    background: rgba(4, 11, 26, 0.72) !important;
    border: 1.5px solid rgba(0, 140, 255, 0.32) !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    backdrop-filter: blur(20px) saturate(190%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(190%) !important;
    box-shadow: 0 14px 36px rgba(0, 0, 0, 0.55), 0 0 20px rgba(0, 140, 255, 0.16), inset 0 1px 0 rgba(255, 255, 255, 0.14) !important;
    transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease !important;
}

.pv-kpi-v2-card:hover,
.pv-kpi-card:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(0, 200, 255, 0.65) !important;
    box-shadow: 0 18px 42px rgba(0, 0, 0, 0.65), 0 0 28px rgba(0, 160, 255, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.24) !important;
}

.pv-kpi-icon-circle {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
}

.pv-kpi-v2-title {
    font-size: 0.72rem;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.pv-kpi-v2-val {
    font-size: 1.85rem;
    font-weight: 800;
    line-height: 1.15;
    margin: 4px 0 2px 0;
    font-feature-settings: "tnum";
}

.pv-kpi-v2-sub {
    font-size: 0.74rem;
    color: #64748b;
}

.pv-trend-pill {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
}

.pv-trend-up-cyan {
    background: rgba(0, 210, 255, 0.12);
    color: #00d2ff;
    border: 1px solid rgba(0, 210, 255, 0.28);
}

.pv-trend-up-red {
    background: rgba(239, 68, 68, 0.12);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.28);
}

.pv-trend-up-green {
    background: rgba(16, 185, 129, 0.12);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.28);
}

.pv-trend-up-purple {
    background: rgba(168, 85, 247, 0.12);
    color: #c084fc;
    border: 1px solid rgba(168, 85, 247, 0.28);
}

/* Dashboard Panels & Container Wrappers - Frosted Glass with Specular Edge */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border: none !important;
    background: transparent !important;
}

.pv-dash-panel,
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: rgba(4, 11, 26, 0.72) !important;
    border: 1.5px solid rgba(0, 140, 255, 0.32) !important;
    border-radius: 14px !important;
    padding: 20px 22px !important;
    backdrop-filter: blur(20px) saturate(190%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(190%) !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.60), 0 0 22px rgba(0, 130, 255, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.14) !important;
    position: relative !important;
    margin-bottom: 20px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.pv-dash-panel:hover,
div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    border-color: rgba(0, 200, 255, 0.60) !important;
    box-shadow: 0 20px 48px rgba(0, 0, 0, 0.70), 0 0 30px rgba(0, 180, 255, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.22) !important;
}

.pv-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}

.pv-panel-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.05rem;
    font-weight: 700;
    color: #ffffff;
}

.pv-panel-link {
    font-size: 0.8rem;
    font-weight: 600;
    color: #00a8ff;
    text-decoration: none;
    cursor: pointer;
    transition: color 0.2s ease;
}

.pv-panel-link:hover {
    color: #38bdf8;
    text-decoration: underline;
}

.pv-filter-pill-container {
    display: inline-flex;
    background: rgba(7, 14, 28, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 3px;
    gap: 2px;
}

.pv-filter-pill {
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 0.74rem;
    font-weight: 600;
    color: #94a3b8;
    background: transparent;
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
}

.pv-filter-pill.active {
    background: #0266d6;
    color: #ffffff;
    box-shadow: 0 2px 8px rgba(2, 102, 214, 0.45);
}

/* Streamlit Native Segmented Control & Button Group Styling */
div[data-testid="stSegmentedControl"],
div[data-testid="stButtonGroup"] {
    background: rgba(4, 11, 26, 0.78) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1.5px solid rgba(0, 140, 255, 0.35) !important;
    border-radius: 20px !important;
    padding: 2px 4px !important;
    box-shadow: 0 0 14px rgba(0, 140, 255, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    display: inline-flex !important;
    align-items: center !important;
    margin: 0 !important;
}

div[data-testid="stSegmentedControl"] > div,
div[data-testid="stButtonGroup"] > div {
    background: transparent !important;
    border: none !important;
    gap: 3px !important;
}

div[data-testid="stSegmentedControl"] button,
div[data-testid="stButtonGroup"] button {
    border-radius: 16px !important;
    font-size: 0.74rem !important;
    font-weight: 600 !important;
    color: #94a3b8 !important;
    background: transparent !important;
    border: none !important;
    padding: 3px 12px !important;
    min-height: unset !important;
    height: 26px !important;
    line-height: 20px !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

div[data-testid="stSegmentedControl"] button:hover,
div[data-testid="stButtonGroup"] button:hover {
    color: #ffffff !important;
    background: rgba(0, 140, 255, 0.16) !important;
}

div[data-testid="stSegmentedControl"] button[aria-checked="true"],
div[data-testid="stSegmentedControl"] button[aria-selected="true"],
div[data-testid="stSegmentedControl"] button[data-selected="true"],
div[data-testid="stButtonGroup"] button[aria-checked="true"],
div[data-testid="stButtonGroup"] button[aria-selected="true"],
div[data-testid="stButtonGroup"] button[data-selected="true"] {
    background: #0266d6 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 10px rgba(2, 102, 214, 0.65) !important;
}

.pv-feed-frame {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(0, 180, 255, 0.2);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
}

.pv-feed-badge-cam {
    position: absolute;
    top: 10px;
    left: 10px;
    background: rgba(7, 14, 28, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(8px);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #f1f5f9;
    z-index: 10;
}

.pv-feed-badge-live {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(220, 38, 38, 0.85);
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 800;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 5px;
    z-index: 10;
    box-shadow: 0 0 10px rgba(220, 38, 38, 0.6);
}

.pv-activity-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 11px 4px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.pv-activity-item:last-child {
    border-bottom: none;
}

.pv-section-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 7px 0;
    font-size: 0.84rem;
}

.pv-global-footer {
    text-align: center;
    padding: 24px 0 10px 0;
    color: #64748b;
    font-size: 0.78rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

@media (max-width: 900px) {
    .pv-kpi-v2-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .pv-hero-banner {
        flex-direction: column;
        gap: 16px;
        align-items: flex-start;
    }
}
</style>
"""


import base64
from pathlib import Path

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
AUTH_BG_PATH = _ASSETS_DIR / "auth_background.jpg"
DASH_BANNER_PATH = _ASSETS_DIR / "dashboard_banner.jpg"
TECH_BG_PATH = _ASSETS_DIR / "tech_parking_bg.jpg"


def get_auth_bg_base64() -> str:
    """Loads base64-encoded background artwork for the auth gate."""
    if AUTH_BG_PATH.exists():
        with open(AUTH_BG_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


@st.cache_data
def get_dash_banner_base64() -> str:
    """Loads and caches base64-encoded artwork for the dashboard hero banner."""
    if DASH_BANNER_PATH.exists():
        with open(DASH_BANNER_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


@st.cache_data
def get_tech_bg_base64() -> str:
    """Loads and caches base64-encoded tech parking background."""
    if TECH_BG_PATH.exists():
        with open(TECH_BG_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


def apply_theme(is_auth_page: bool = False) -> None:
    """Injects custom CSS tokens and conditional styling."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    if is_auth_page:
        bg_b64 = get_auth_bg_base64()
        bg_css = ""
        if bg_b64:
            bg_css = f"""
            .stApp {{
                background-color: #020612 !important;
                background-image: 
                    radial-gradient(circle at 18% 18%, rgba(1, 4, 12, 0.35) 0%, transparent 60%),
                    linear-gradient(135deg, rgba(2, 6, 18, 0.30) 0%, rgba(2, 6, 18, 0.45) 100%),
                    url('data:image/jpeg;base64,{bg_b64}') !important;
                background-size: cover !important;
                background-position: center center !important;
                background-attachment: fixed !important;
                background-repeat: no-repeat !important;
            }}
            """
        else:
            bg_css = """
            .stApp {
                background-color: #01040a !important;
                background: #01040a !important;
            }
            """
        st.markdown(
            f"""
            <style>
            {bg_css}
            [data-testid="stSidebar"] {{
                display: none !important;
            }}
            header[data-testid="stHeader"] {{
                display: none !important;
            }}
            .block-container {{
                padding-top: 1.5rem !important;
                padding-bottom: 2rem !important;
                max-width: 1320px !important;
            }}

            /* Left Hero Styling - Small Rectangular Boxes with Slight Glowing Effect */
            .pv-benefit-pill {{
                display: flex !important;
                align-items: flex-start !important;
                gap: 16px !important;
                background: rgba(8, 20, 42, 0.78) !important;
                border: 1px solid rgba(56, 189, 248, 0.25) !important;
                border-radius: 14px !important;
                padding: 13px 18px !important;
                backdrop-filter: blur(16px) !important;
                -webkit-backdrop-filter: blur(16px) !important;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 15px rgba(0, 140, 255, 0.08) !important;
                transition: all 0.25s ease !important;
            }}
            .pv-benefit-pill:hover {{
                background: rgba(14, 34, 70, 0.85) !important;
                border-color: rgba(56, 189, 248, 0.5) !important;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 180, 255, 0.2) !important;
                transform: translateX(4px) !important;
            }}
            .pv-benefit-icon-box {{
                width: 44px !important;
                height: 44px !important;
                min-width: 44px !important;
                border-radius: 11px !important;
                background: rgba(12, 30, 60, 0.85) !important;
                border: 1.5px solid rgba(56, 189, 248, 0.38) !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                box-shadow: 0 0 12px rgba(0, 180, 255, 0.18) !important;
            }}

            .pv-pipeline-card {{
                background: rgba(8, 20, 42, 0.78) !important;
                border: 1px solid rgba(56, 189, 248, 0.25) !important;
                border-radius: 14px !important;
                padding: 14px 20px 16px 20px !important;
                backdrop-filter: blur(16px) !important;
                -webkit-backdrop-filter: blur(16px) !important;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 15px rgba(0, 140, 255, 0.08) !important;
                margin-top: 12px !important;
            }}
            .pv-flow-step {{
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                text-align: center !important;
            }}
            .pv-flow-icon {{
                width: 40px !important;
                height: 40px !important;
                border-radius: 10px !important;
                border: 1.5px solid rgba(56, 189, 248, 0.35) !important;
                background: rgba(12, 30, 60, 0.85) !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                margin-bottom: 6px !important;
                box-shadow: 0 0 12px rgba(0, 180, 255, 0.16) !important;
            }}

            .pv-demo-bar {{
                background: rgba(8, 20, 42, 0.82) !important;
                border: 1px solid rgba(56, 189, 248, 0.28) !important;
                border-radius: 14px !important;
                padding: 12px 18px !important;
                margin-top: 12px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: space-between !important;
                backdrop-filter: blur(16px) !important;
                -webkit-backdrop-filter: blur(16px) !important;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 15px rgba(0, 140, 255, 0.08) !important;
            }}

            /* Right Auth Column Monolithic Glass Card - Glowing Cyber Box */
            div[data-testid="stColumn"]:last-child,
            div[data-testid="stColumn"]:nth-of-type(2) {{
                background: rgba(8, 20, 42, 0.80) !important;
                border: 1px solid rgba(56, 189, 248, 0.28) !important;
                border-radius: 20px !important;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.75), 0 0 35px rgba(0, 140, 255, 0.16) !important;
                padding: 32px 30px !important;
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
            }}

            div[data-testid="stColumn"]:last-child > div[data-testid="stVerticalBlock"],
            div[data-testid="stColumn"]:nth-of-type(2) > div[data-testid="stVerticalBlock"] {{
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
            }}

            div[data-testid="stColumn"]:last-child div[data-testid="stForm"],
            div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stForm"] {{
                background: transparent !important;
                border: none !important;
                padding: 0 !important;
                box-shadow: none !important;
            }}

            /* Tab styling in Auth */
            div[data-testid="stColumn"]:last-child div[data-testid="stTabs"],
            div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stTabs"] {{
                margin-bottom: 16px !important;
            }}
            div[data-testid="stColumn"]:last-child div[data-testid="stTabs"] [data-baseweb="tab-list"],
            div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
                gap: 28px !important;
                background: transparent !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.12) !important;
                padding-bottom: 0px !important;
                margin-bottom: 22px !important;
            }}
            div[data-testid="stColumn"]:last-child div[data-testid="stTabs"] button[role="tab"],
            div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stTabs"] button[role="tab"] {{
                font-size: 1.05rem !important;
                font-weight: 600 !important;
                color: #94a3b8 !important;
                padding: 8px 4px 12px 4px !important;
                border: none !important;
                background: transparent !important;
                border-bottom: 3px solid transparent !important;
                transition: all 0.2s ease !important;
            }}
            div[data-testid="stColumn"]:last-child div[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
            div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
                color: #38bdf8 !important;
                font-weight: 700 !important;
                border-bottom: 3px solid #0284c7 !important;
                box-shadow: 0 4px 14px rgba(2, 132, 199, 0.5) !important;
            }}

            /* Labels */
            div[data-testid="stColumn"]:last-child label,
            div[data-testid="stColumn"]:nth-of-type(2) label {{
                color: #e2e8f0 !important;
                font-size: 0.92rem !important;
                font-weight: 600 !important;
                margin-bottom: 6px !important;
            }}
            div[data-testid="stColumn"]:last-child div[data-testid="stCheckbox"] label,
            div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stCheckbox"] label {{
                color: #cbd5e1 !important;
                font-size: 0.88rem !important;
                font-weight: 500 !important;
            }}

            /* Inputs - Glowing Rectangular Boxes */
            div[data-testid="stColumn"]:last-child input,
            div[data-testid="stColumn"]:nth-of-type(2) input {{
                background: rgba(6, 16, 36, 0.85) !important;
                border: 1px solid rgba(56, 189, 248, 0.28) !important;
                border-radius: 10px !important;
                color: #ffffff !important;
                font-size: 0.95rem !important;
                padding: 12px 14px !important;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3) !important;
            }}
            div[data-testid="stColumn"]:last-child input:focus,
            div[data-testid="stColumn"]:nth-of-type(2) input:focus {{
                border-color: #38bdf8 !important;
                box-shadow: 0 0 16px rgba(56, 189, 248, 0.35) !important;
            }}

            /* Mail and Lock icons inside inputs matching reference design */
            div[data-testid="stColumn"]:last-child input[aria-label="Work Email"],
            div[data-testid="stColumn"]:nth-of-type(2) input[aria-label="Work Email"] {{
                padding-left: 42px !important;
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='2' y='4' width='20' height='16' rx='2'/%3E%3Cpath d='m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7'/%3E%3C/svg%3E") !important;
                background-repeat: no-repeat !important;
                background-position: 14px center !important;
            }}
            div[data-testid="stColumn"]:last-child input[aria-label="Password"],
            div[data-testid="stColumn"]:nth-of-type(2) input[aria-label="Password"],
            div[data-testid="stColumn"]:last-child input[aria-label="Password (min. 8 characters)"],
            div[data-testid="stColumn"]:nth-of-type(2) input[aria-label="Password (min. 8 characters)"] {{
                padding-left: 42px !important;
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='11' width='18' height='11' rx='2' ry='2'/%3E%3Cpath d='M7 11V7a5 5 0 0 1 10 0v4'/%3E%3C/svg%3E") !important;
                background-repeat: no-repeat !important;
                background-position: 14px center !important;
            }}

            /* Primary Sign In Button */
            div[data-testid="stColumn"]:last-child button[kind="primaryFormSubmit"],
            div[data-testid="stColumn"]:last-child button[type="submit"],
            div[data-testid="stColumn"]:nth-of-type(2) button[kind="primaryFormSubmit"],
            div[data-testid="stColumn"]:nth-of-type(2) button[type="submit"] {{
                background: linear-gradient(90deg, #0284c7 0%, #0070f3 100%) !important;
                border: 1px solid rgba(56, 189, 248, 0.4) !important;
                border-radius: 12px !important;
                height: 48px !important;
                font-size: 1.0rem !important;
                font-weight: 700 !important;
                color: #ffffff !important;
                box-shadow: 0 4px 20px rgba(0, 112, 243, 0.45) !important;
                letter-spacing: 0.02em !important;
                transition: all 0.22s ease !important;
                margin-top: 14px !important;
            }}
            div[data-testid="stColumn"]:last-child button[kind="primaryFormSubmit"]:hover,
            div[data-testid="stColumn"]:last-child button[type="submit"]:hover,
            div[data-testid="stColumn"]:nth-of-type(2) button[kind="primaryFormSubmit"]:hover,
            div[data-testid="stColumn"]:nth-of-type(2) button[type="submit"]:hover {{
                box-shadow: 0 6px 26px rgba(0, 112, 243, 0.65) !important;
                transform: translateY(-1px) !important;
            }}

            /* Guest Button */
            div[data-testid="stColumn"]:last-child .stButton > button,
            div[data-testid="stColumn"]:nth-of-type(2) .stButton > button {{
                background: rgba(8, 20, 42, 0.70) !important;
                border: 1px solid rgba(255, 255, 255, 0.16) !important;
                border-radius: 12px !important;
                height: 48px !important;
                color: #ffffff !important;
                font-weight: 600 !important;
                font-size: 0.95rem !important;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
                transition: all 0.2s ease !important;
            }}
            div[data-testid="stColumn"]:last-child .stButton > button:hover,
            div[data-testid="stColumn"]:nth-of-type(2) .stButton > button:hover {{
                background: rgba(14, 32, 64, 0.90) !important;
                border-color: rgba(56, 189, 248, 0.4) !important;
                box-shadow: 0 0 22px rgba(0, 210, 255, 0.3) !important;
                color: #ffffff !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        tech_bg_b64 = get_tech_bg_base64()
        if tech_bg_b64:
            st.markdown(
                f"""
                <style>
                html, body, .stApp {{
                    background-color: #01040a !important;
                    background-image: 
                        radial-gradient(circle at 50% 8%, rgba(0, 140, 255, 0.12) 0%, transparent 60%),
                        linear-gradient(180deg, rgba(1, 4, 10, 0.85) 0%, rgba(1, 4, 10, 0.72) 35%, rgba(1, 4, 10, 0.90) 100%),
                        url('data:image/jpeg;base64,{tech_bg_b64}') !important;
                    background-size: cover !important;
                    background-position: center top !important;
                    background-attachment: fixed !important;
                    background-repeat: no-repeat !important;
                }}
                </style>
                """,
                unsafe_allow_html=True,
            )


def render_html(html_str: str) -> None:
    """
    Renders an HTML snippet safely without Markdown parser treating child indentation as code blocks.
    Strips leading whitespace from every line, removes blank lines, and omits HTML comments.
    Uses st.html for native HTML, CSS, and inline SVG rendering without DOMPurify stripping.
    """
    clean_lines = [
        line.strip()
        for line in html_str.splitlines()
        if line.strip() and not line.strip().startswith("<!--")
    ]
    cleaned = "\n".join(clean_lines)
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)
