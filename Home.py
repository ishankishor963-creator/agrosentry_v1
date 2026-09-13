import streamlit as st

from utils.auth import logout_button, require_login
from utils.esp_client import get_sensor_data
from utils.theme import inject_theme, topnav

# --- Auth gate: blocks until authenticated ---
require_login()

st.set_page_config(
    page_title="AgroSentry — Farm Ops",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "esp_base_url" not in st.session_state:
    st.session_state["esp_base_url"] = ""

# Inject base theme
inject_theme()


def render_html(html_str: str):
    """Strips all leading/trailing line whitespace so Streamlit never converts nested HTML to code blocks."""
    cleaned = "\n".join(line.strip() for line in html_str.splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def render_custom_css():
    render_html("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

            /* ================= BASE ENVIRONMENT & SEAMLESS BACKGROUND ================= */
            :root {
                --as-bg-black: #050608;
                --as-surface: rgba(14, 18, 26, 0.65);
                --as-surface-hover: rgba(22, 28, 40, 0.85);
                --as-border: rgba(255, 255, 255, 0.07);
                --as-border-hover: rgba(255, 149, 0, 0.35);
                --as-orange: #FF9500;
                --as-orange-glow: rgba(255, 149, 0, 0.25);
                --as-green: #10B981;
                --as-green-glow: rgba(16, 185, 129, 0.25);
                --as-cyan: #06B6D4;
                --as-text-white: #FFFFFF;
                --as-text-muted: #9CA3AF;
            }

            html, body, [data-testid="stAppViewContainer"] {
                background-color: var(--as-bg-black) !important;
                background-image: 
                    /* Subtle ambient amber/orange glow at top */
                    radial-gradient(circle at 50% -80px, rgba(255, 149, 0, 0.08) 0%, transparent 60%),
                    /* Soft cyan/emerald ambient aura in bottom right */
                    radial-gradient(circle at 90% 70%, rgba(6, 182, 212, 0.03) 0%, transparent 45%),
                    /* High-tech subtle grid overlay */
                    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px) !important;
                background-size: 100% 100%, 100% 100%, 48px 48px, 48px 48px !important;
                background-attachment: fixed !important;
                color: #F9FAFB !important;
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
                letter-spacing: -0.01em;
            }

            /* Hide Streamlit default clutter */
            #MainMenu, header, footer { visibility: hidden; }
            [data-testid="stHeader"] { background-color: transparent !important; }
            .stDeployButton { display: none !important; }

            /* ================= SIDEBAR REDESIGN ================= */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #07090E 0%, #050608 100%) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
                box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5) !important;
            }
            [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
                gap: 0.85rem !important;
            }

            /* ================= TOP NAVIGATION POLISH ================= */
            .brand-nav-container {
                background: rgba(10, 13, 20, 0.72) !important;
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-radius: 18px !important;
                padding: 0.75rem 1.4rem !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
                margin-bottom: 0.75rem !important;
                animation: navSlideDown 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
            }

            @keyframes navSlideDown {
                from { opacity: 0; transform: translateY(-12px); }
                to { opacity: 1; transform: translateY(0); }
            }

            /* ================= UNIVERSAL BUTTON ANIMATION SYSTEM ================= */
            div.stButton > button {
                background: rgba(255, 255, 255, 0.04) !important;
                color: #F3F4F6 !important;
                border: 1px solid rgba(255, 255, 255, 0.09) !important;
                border-radius: 12px !important;
                padding: 0.65rem 1.25rem !important;
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                font-weight: 600 !important;
                font-size: 0.88rem !important;
                letter-spacing: 0.01em !important;
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
                transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
                position: relative !important;
                overflow: hidden !important;
                width: 100% !important;
            }

            /* Hover: Smooth upward move + warm orange gradient + glow */
            div.stButton > button:hover {
                background: linear-gradient(135deg, rgba(255, 149, 0, 0.95) 0%, rgba(230, 126, 0, 0.95) 100%) !important;
                color: #000000 !important;
                border-color: #FF9500 !important;
                box-shadow: 0 8px 24px rgba(255, 149, 0, 0.35), 0 0 12px rgba(255, 149, 0, 0.2) !important;
                transform: translateY(-2px) !important;
            }

            /* Active / Pressed: Micro scale-down */
            div.stButton > button:active {
                transform: translateY(0px) scale(0.98) !important;
                box-shadow: 0 2px 8px rgba(255, 149, 0, 0.25) !important;
                transition: all 0.08s ease !important;
            }

            /* Focus State */
            div.stButton > button:focus-visible {
                outline: none !important;
                box-shadow: 0 0 0 2px #050608, 0 0 0 4px rgba(255, 149, 0, 0.6) !important;
            }

            /* ================= TYPOGRAPHY & HERO SECTION ================= */
            .hero-container {
                animation: heroFadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
                padding-top: 0.5rem;
            }

            @keyframes heroFadeIn {
                from { opacity: 0; transform: translateY(18px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .eyebrow-text {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.72rem;
                font-weight: 600;
                letter-spacing: 0.16em;
                text-transform: uppercase;
                color: #FF9500;
                margin-bottom: 0.75rem;
                display: inline-flex;
                align-items: center;
                gap: 0.6rem;
                background: rgba(255, 149, 0, 0.08);
                padding: 4px 12px;
                border-radius: 100px;
                border: 1px solid rgba(255, 149, 0, 0.22);
            }

            .eyebrow-dot {
                width: 6px;
                height: 6px;
                background-color: #FF9500;
                border-radius: 50%;
                box-shadow: 0 0 8px #FF9500;
                animation: pulseGlow 2.5s infinite ease-in-out;
            }

            @keyframes pulseGlow {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.4; transform: scale(0.85); }
            }

            .hero-title {
                font-family: 'Outfit', sans-serif;
                font-size: 3.5rem;
                font-weight: 800;
                line-height: 1.08;
                letter-spacing: -0.035em;
                background: linear-gradient(180deg, #FFFFFF 0%, #E4E4E7 50%, #9CA3AF 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 1.25rem;
            }

            .hero-title span {
                background: linear-gradient(135deg, #FF9500 0%, #F59E0B 50%, #FBBF24 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .hero-desc {
                font-size: 1.02rem;
                color: #9CA3AF;
                line-height: 1.65;
                margin-bottom: 2rem;
                max-width: 540px;
                font-weight: 400;
            }

            /* ================= HIGH-TECH RADAR HUD ================= */
            .radar-box {
                position: relative;
                width: 100%;
                height: 380px;
                background: radial-gradient(circle at center, rgba(20, 26, 38, 0.6) 0%, rgba(7, 9, 14, 0.95) 75%);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 22px;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
                box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6), inset 0 0 50px rgba(0, 0, 0, 0.8);
                animation: radarFadeIn 1s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both;
            }

            @keyframes radarFadeIn {
                from { opacity: 0; transform: scale(0.97); }
                to { opacity: 1; transform: scale(1); }
            }

            .radar-grid {
                position: absolute;
                width: 100%;
                height: 100%;
                background-image: 
                    linear-gradient(rgba(255, 255, 255, 0.025) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.025) 1px, transparent 1px);
                background-size: 26px 26px;
            }

            .radar-crosshair-x {
                position: absolute;
                width: 100%;
                height: 1px;
                background: rgba(255, 255, 255, 0.06);
            }
            .radar-crosshair-y {
                position: absolute;
                height: 100%;
                width: 1px;
                background: rgba(255, 255, 255, 0.06);
            }

            .radar-circle {
                position: absolute;
                border-radius: 50%;
            }

            .radar-circle.c1 {
                width: 100px;
                height: 100px;
                border: 1px dashed rgba(255, 149, 0, 0.35);
            }
            .radar-circle.c2 {
                width: 200px;
                height: 200px;
                border: 1px solid rgba(255, 255, 255, 0.07);
            }
            .radar-circle.c3 {
                width: 300px;
                height: 300px;
                border: 1px dashed rgba(255, 255, 255, 0.08);
            }

            .radar-sweep-beam {
                position: absolute;
                width: 300px;
                height: 300px;
                border-radius: 50%;
                background: conic-gradient(from 0deg, rgba(255, 149, 0, 0.26) 0deg, rgba(255, 149, 0, 0.05) 45deg, transparent 65deg, transparent 360deg);
                animation: radar-spin 7s linear infinite;
            }

            @keyframes radar-spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            .radar-center-dot {
                width: 10px;
                height: 10px;
                background-color: #FF9500;
                border-radius: 50%;
                box-shadow: 0 0 12px #FF9500, 0 0 24px rgba(255, 149, 0, 0.6);
                z-index: 5;
            }

            .radar-center-ping {
                position: absolute;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                border: 1px solid #FF9500;
                animation: pingEffect 3s cubic-bezier(0, 0, 0.2, 1) infinite;
                z-index: 4;
            }

            @keyframes pingEffect {
                0% { transform: scale(1); opacity: 0.9; }
                80%, 100% { transform: scale(4.5); opacity: 0; }
            }

            .hud-badge {
                position: absolute;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.68rem;
                font-weight: 500;
                letter-spacing: 0.04em;
                padding: 6px 12px;
                border-radius: 8px;
                background: rgba(10, 13, 19, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.09);
                color: #E5E7EB;
                display: flex;
                align-items: center;
                gap: 7px;
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
                z-index: 10;
            }

            .hud-badge-dot {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background-color: #10B981;
                box-shadow: 0 0 6px #10B981;
            }

            .hud-pos-1 { top: 20px; left: 20px; }
            .hud-pos-2 { top: 20px; right: 20px; }
            .hud-pos-3 { bottom: 20px; left: 20px; }
            .hud-pos-4 { bottom: 20px; right: 20px; }

            /* ================= CHIPS & BADGES ================= */
            .chip {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.68rem;
                font-weight: 600;
                padding: 3px 10px;
                border-radius: 100px;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                display: inline-flex;
                align-items: center;
                gap: 5px;
            }

            .chip-green {
                background: rgba(16, 185, 129, 0.1);
                color: #10B981;
                border: 1px solid rgba(16, 185, 129, 0.28);
            }

            .chip-amber {
                background: rgba(245, 158, 11, 0.1);
                color: #F59E0B;
                border: 1px solid rgba(245, 158, 11, 0.28);
            }

            .chip-cyan {
                background: rgba(6, 182, 212, 0.1);
                color: #06B6D4;
                border: 1px solid rgba(6, 182, 212, 0.28);
            }

            .chip-pink {
                background: rgba(236, 72, 153, 0.1);
                color: #EC4899;
                border: 1px solid rgba(236, 72, 153, 0.28);
            }

            /* ================= TELEMETRY STAT CARDS ================= */
            .stat-card {
                background: linear-gradient(145deg, rgba(16, 21, 31, 0.65) 0%, rgba(9, 12, 18, 0.85) 100%);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 18px;
                padding: 1.4rem;
                position: relative;
                transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
            }

            .stat-card:hover {
                border-color: rgba(255, 149, 0, 0.3);
                transform: translateY(-3px);
                box-shadow: 0 14px 36px rgba(0, 0, 0, 0.5), 0 0 20px rgba(255, 149, 0, 0.08);
            }

            .stat-label {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.68rem;
                color: #9CA3AF;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                margin-bottom: 0.6rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }

            .stat-val-row {
                display: flex;
                align-items: baseline;
                justify-content: space-between;
            }

            .stat-value {
                font-family: 'Outfit', sans-serif;
                font-size: 2.25rem;
                font-weight: 700;
                color: #FFFFFF;
                letter-spacing: -0.025em;
            }

            .stat-status {
                font-size: 0.76rem;
                font-weight: 600;
                color: #9CA3AF;
                margin-top: 0.5rem;
                display: flex;
                align-items: center;
                gap: 5px;
            }

            /* ================= FARM INTELLIGENCE PANEL ================= */
            .glass-card {
                background: linear-gradient(135deg, rgba(16, 21, 31, 0.6) 0%, rgba(9, 12, 18, 0.85) 100%);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 20px;
                padding: 1.8rem;
                transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                position: relative;
                overflow: hidden;
                box-shadow: 0 12px 36px rgba(0, 0, 0, 0.4);
            }

            .glass-card:hover {
                border-color: rgba(255, 149, 0, 0.28);
                box-shadow: 0 16px 44px rgba(0, 0, 0, 0.5), 0 0 24px rgba(255, 149, 0, 0.06);
            }

            .progress-bar-bg {
                width: 100%;
                height: 6px;
                background: rgba(255, 255, 255, 0.07);
                border-radius: 100px;
                overflow: hidden;
                margin-top: 8px;
            }

            .progress-bar-fill {
                height: 100%;
                border-radius: 100px;
                background: linear-gradient(90deg, #FF9500 0%, #10B981 100%);
                box-shadow: 0 0 10px rgba(255, 149, 0, 0.4);
                transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
            }

            /* ================= MODULE CARDS ================= */
            .module-card {
                background: linear-gradient(145deg, rgba(16, 21, 31, 0.55) 0%, rgba(9, 12, 18, 0.8) 100%);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 18px;
                padding: 1.6rem;
                min-height: 180px;
                transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }

            .module-card:hover {
                border-color: rgba(255, 149, 0, 0.32);
                transform: translateY(-3px);
                box-shadow: 0 14px 36px rgba(0, 0, 0, 0.5), 0 0 20px rgba(255, 149, 0, 0.07);
            }

            .module-card-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 0.9rem;
            }

            .module-icon {
                font-size: 1.85rem;
                filter: drop-shadow(0 0 12px rgba(255, 149, 0, 0.25));
            }

            .module-title {
                font-family: 'Outfit', sans-serif;
                font-size: 1.2rem;
                font-weight: 700;
                color: #FFFFFF;
                margin-bottom: 0.45rem;
                letter-spacing: -0.015em;
            }

            .module-desc {
                font-size: 0.88rem;
                color: #9CA3AF;
                line-height: 1.55;
                margin-bottom: 0.5rem;
            }

            /* ================= HEADINGS & LAYOUT ================= */
            .section-header {
                margin-top: 3.5rem;
                margin-bottom: 1.5rem;
                animation: sectionFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
            }

            @keyframes sectionFade {
                from { opacity: 0; transform: translateY(14px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .section-title {
                font-family: 'Outfit', sans-serif;
                font-size: 1.85rem;
                font-weight: 700;
                color: #FFFFFF;
                letter-spacing: -0.025em;
                margin-top: 0.25rem;
            }

            .section-subtitle {
                font-size: 0.94rem;
                color: #9CA3AF;
                margin-top: 0.3rem;
            }

            /* ================= SYSTEM FOOTER ================= */
            .system-footer {
                margin-top: 5rem;
                padding: 1.8rem 0;
                border-top: 1px solid rgba(255, 255, 255, 0.07);
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 1rem;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.72rem;
                color: #6B7280;
            }

            .footer-status-item {
                display: flex;
                align-items: center;
                gap: 7px;
            }

            .status-dot-active {
                width: 6px;
                height: 6px;
                background-color: #10B981;
                border-radius: 50%;
                box-shadow: 0 0 8px #10B981;
                animation: pulseGlow 2.5s infinite ease-in-out;
            }

            /* ================= REDUCED MOTION SUPPORT ================= */
            @media (prefers-reduced-motion: reduce) {
                *, ::before, ::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }
        </style>
    """)


def render_header():
    topnav("home")


def render_hero():
    col1, col2 = st.columns([1.15, 0.85], gap="large")

    with col1:
        render_html("""
            <div class="hero-container">
                <div class="eyebrow-text">
                    <span class="eyebrow-dot"></span>
                    AI-POWERED FARM INTELLIGENCE
                </div>
                <h1 class="hero-title">
                    Smarter Farming.<br>
                    <span>Powered by AI.</span>
                </h1>
                <p class="hero-desc">
                    Monitor your crops, understand your environmental risks, and respond to micro-climate anomalies before they affect your agricultural yield.
                </p>
            </div>
        """)

        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            if st.button("🤖 OPEN AI ASSISTANT", key="hero_ai_btn"):
                st.switch_page("pages/1_AI_Assistant.py")
        with btn_col2:
            if st.button("🌡️ VIEW SENSORS", key="hero_sensor_btn"):
                st.switch_page("pages/2_Sensor_Dashboard.py")

    with col2:
        render_html("""
            <div class="radar-box">
                <div class="radar-grid"></div>
                <div class="radar-crosshair-x"></div>
                <div class="radar-crosshair-y"></div>
                <div class="radar-circle c1"></div>
                <div class="radar-circle c2"></div>
                <div class="radar-circle c3"></div>
                <div class="radar-sweep-beam"></div>
                <div class="radar-center-dot"></div>
                <div class="radar-center-ping"></div>
                
                <div class="hud-badge hud-pos-1">
                    <span class="hud-badge-dot"></span> SOIL RADAR: OPTIMAL
                </div>
                <div class="hud-badge hud-pos-2">
                    <span class="hud-badge-dot" style="background-color: #FF9500; box-shadow: 0 0 8px #FF9500;"></span> AI ENGINE: ACTIVE
                </div>
                <div class="hud-badge hud-pos-3">
                    <span class="hud-badge-dot"></span> CROP STRESS: 0.02%
                </div>
                <div class="hud-badge hud-pos-4">
                    <span class="hud-badge-dot"></span> EDGE NODE: ONLINE
                </div>
            </div>
        """)


def render_sensor_cards(reading):
    render_html("""
        <div class="section-header">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div class="eyebrow-text">
                        <span class="eyebrow-dot"></span>
                        TELEMETRY DATA
                    </div>
                    <h2 class="section-title">Farm Overview</h2>
                </div>
                <span class="chip chip-green">● LIVE MONITORING</span>
            </div>
        </div>
    """)

    soil = reading.get("soil_moisture", 0)
    humidity = reading.get("humidity", 0)
    temp = reading.get("temperature", 0)
    source = reading.get("source", "demo")

    is_live = source == "device"
    source_str = "LIVE DEVICE" if is_live else "DEMO MODE"
    source_class = "chip-green" if is_live else "chip-amber"

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_html(f"""
            <div class="stat-card">
                <div class="stat-label">
                    <span>SOIL MOISTURE</span>
                    <span style="color: #FF9500;">●</span>
                </div>
                <div class="stat-val-row">
                    <div class="stat-value">{soil}%</div>
                    <svg width="64" height="24" viewBox="0 0 64 24" fill="none">
                        <path d="M0 18 L14 14 L26 16 L38 8 L50 10 L64 4" stroke="#FF9500" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div class="stat-status">
                    <span style="color: #10B981;">● OPTIMAL</span> FIELD HYDRATION
                </div>
            </div>
        """)

    with c2:
        render_html(f"""
            <div class="stat-card">
                <div class="stat-label">
                    <span>HUMIDITY</span>
                    <span style="color: #06B6D4;">●</span>
                </div>
                <div class="stat-val-row">
                    <div class="stat-value">{humidity}%</div>
                    <svg width="64" height="24" viewBox="0 0 64 24" fill="none">
                        <path d="M0 10 L16 12 L32 6 L48 18 L64 8" stroke="#06B6D4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div class="stat-status" style="color: #06B6D4;">
                    ● BALANCED ATMOSPHERE
                </div>
            </div>
        """)

    with c3:
        render_html(f"""
            <div class="stat-card">
                <div class="stat-label">
                    <span>TEMPERATURE</span>
                    <span style="color: #F59E0B;">●</span>
                </div>
                <div class="stat-val-row">
                    <div class="stat-value">{temp}°C</div>
                    <svg width="64" height="24" viewBox="0 0 64 24" fill="none">
                        <path d="M0 14 L16 8 L32 15 L48 5 L64 12" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div class="stat-status" style="color: #F59E0B;">
                    ● STABLE CONDITIONS
                </div>
            </div>
        """)

    with c4:
        render_html(f"""
            <div class="stat-card">
                <div class="stat-label">
                    <span>DATA SOURCE</span>
                    <span style="color: {'#10B981' if is_live else '#F59E0B'};">●</span>
                </div>
                <div class="stat-val-row">
                    <div class="stat-value" style="font-size: 1.35rem; padding-top: 0.4rem;">{source_str}</div>
                </div>
                <div style="margin-top: 0.75rem;">
                    <span class="chip {source_class}">{'ONLINE' if is_live else 'SIMULATED'}</span>
                </div>
            </div>
        """)


def render_farm_intelligence():
    st.write("")
    render_html("""
        <div class="glass-card" style="margin-top: 1rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;">
                <div>
                    <div class="eyebrow-text">
                        <span class="eyebrow-dot"></span>
                        SYNTHETIC ANALYSIS
                    </div>
                    <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.35rem; font-weight: 700; color: #FFFFFF; margin: 0.35rem 0 0 0;">
                        Farm Intelligence Diagnostics
                    </h3>
                </div>
                <span class="chip chip-cyan">AI EVALUATED</span>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.6rem;">
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 6px;">
                        <span style="color: #9CA3AF;">Crop Health</span>
                        <span style="color: #10B981; font-weight: 700;">86% (Excellent)</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: 86%;"></div>
                    </div>
                </div>
                
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 6px;">
                        <span style="color: #9CA3AF;">Water Status</span>
                        <span style="color: #06B6D4; font-weight: 700;">92% (Optimal)</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: 92%; background: linear-gradient(90deg, #06B6D4, #3B82F6);"></div>
                    </div>
                </div>
                
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 6px;">
                        <span style="color: #9CA3AF;">Weather Risk</span>
                        <span style="color: #10B981; font-weight: 700;">14% (Low)</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: 14%; background: #10B981;"></div>
                    </div>
                </div>
                
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 6px;">
                        <span style="color: #9CA3AF;">Pest Risk</span>
                        <span style="color: #10B981; font-weight: 700;">8% (Low)</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: 8%; background: #10B981;"></div>
                    </div>
                </div>
            </div>
        </div>
    """)


def render_module_card(col, icon, title, desc, target, badge_label, badge_class, key):
    with col:
        render_html(f"""
            <div class="module-card">
                <div>
                    <div class="module-card-header">
                        <span class="module-icon">{icon}</span>
                        <span class="chip {badge_class}">{badge_label}</span>
                    </div>
                    <h3 class="module-title">{title}</h3>
                    <p class="module-desc">{desc}</p>
                </div>
            </div>
        """)
        if st.button(f"Launch {title} →", key=key, use_container_width=True):
            st.switch_page(target)


def render_modules():
    render_html("""
        <div class="section-header">
            <div>
                <div class="eyebrow-text">
                    <span class="eyebrow-dot"></span>
                    MODULAR SUITE
                </div>
                <h2 class="section-title">Explore AgroSentry</h2>
            </div>
            <div class="section-subtitle">Everything you need to monitor, analyze, and protect your agricultural ecosystem.</div>
        </div>
    """)

    col_row1 = st.columns(3)
    col_row2 = st.columns(3)

    render_module_card(col_row1[0], "🤖", "AI Assistant", "Ask farming questions and receive intelligent agronomic recommendations.", "pages/1_AI_Assistant.py", "AI", "chip-cyan", "btn_ai")
    render_module_card(col_row1[1], "🌡️", "Sensor Dashboard", "Monitor live soil moisture, humidity, temperature, and environmental conditions.", "pages/2_Sensor_Dashboard.py", "LIVE", "chip-green", "btn_sensor")
    render_module_card(col_row1[2], "🚨", "Flood / Drought Alerts", "Detect climate risks and receive early warnings from sensor trends.", "pages/3_Flood_Drought_Alerts.py", "ALERT", "chip-pink", "btn_alerts")
    render_module_card(col_row2[0], "📷", "Camera Feed", "Monitor your field visually through the connected edge camera feed.", "pages/4_Camera_Feed.py", "VISION", "chip-cyan", "btn_camera")
    render_module_card(col_row2[1], "🔬", "Disease Detection", "Upload crop leaf photos and identify possible diseases with AI vision models.", "pages/5_Disease_Detection.py", "AI MODEL", "chip-amber", "btn_disease")
    render_module_card(col_row2[2], "🐛", "Pest Control", "Monitor environmental pest risks and support integrated pest management.", "pages/6_Pest_Control.py", "IPM", "chip-pink", "btn_pest")


def render_device_status():
    with st.sidebar:
        render_html("""
            <div style="padding-bottom: 0.6rem;">
                <div class="eyebrow-text" style="font-size: 0.65rem; margin-bottom: 0.4rem;">
                    <span class="eyebrow-dot"></span>
                    HARDWARE LINK
                </div>
                <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin: 0;">
                    Device Status
                </h3>
            </div>
        """)

        connected = bool(st.session_state.get("esp_base_url", ""))
        chip = '<span class="chip chip-green">● CONNECTED</span>' if connected else '<span class="chip chip-amber">● DEMO MODE</span>'
        render_html(chip)
        st.write("")

        st.session_state["esp_base_url"] = st.text_input(
            "ESP32 / Raspberry Pi base URL",
            value=st.session_state["esp_base_url"],
            placeholder="http://192.168.1.42",
            help="The IP address your ESP32/Pi prints over serial when it connects to WiFi. Leave blank to run every page in demo mode with sample data.",
        )

        if connected:
            st.success("Pages will fetch live edge data.")
        else:
            st.info("Pages will display demo data.")

        st.divider()
        logout_button()


def render_footer(reading):
    source = reading.get("source", "demo")
    esp_status = "CONNECTED" if source == "device" else "DEMO MODE"

    render_html(f"""
        <div class="system-footer">
            <div>AGROSENTRY AI FARM INTELLIGENCE</div>
            <div class="footer-status-item">
                <span class="status-dot-active"></span>
                SYSTEM STATUS: OPERATIONAL
            </div>
            <div>ESP32: {esp_status}</div>
            <div>AI ENGINE: READY</div>
        </div>
    """)


def home():
    render_custom_css()
    render_device_status()
    render_header()
    render_hero()

    reading = get_sensor_data()

    render_sensor_cards(reading)
    render_farm_intelligence()
    render_modules()
    render_footer(reading)


# --- Explicit page registration ---
home_page = st.Page(home, title="Home", icon="🌾", default=True)
ai_page = st.Page("pages/1_AI_Assistant.py", title="AI Assistant", icon="🤖")
sensor_page = st.Page("pages/2_Sensor_Dashboard.py", title="Sensor Dashboard", icon="🌡️")
alerts_page = st.Page("pages/3_Flood_Drought_Alerts.py", title="Flood/Drought Alerts", icon="🚨")
camera_page = st.Page("pages/4_Camera_Feed.py", title="Camera Feed", icon="📷")
disease_page = st.Page("pages/5_Disease_Detection.py", title="Disease Detection", icon="🔬")
pest_page = st.Page("pages/6_Pest_Control.py", title="Pest Control", icon="🐛")

st.session_state["_pages"] = {
    "home": home_page,
    "ai": "pages/1_AI_Assistant.py",
    "sensor": "pages/2_Sensor_Dashboard.py",
    "alerts": "pages/3_Flood_Drought_Alerts.py",
    "camera": "pages/4_Camera_Feed.py",
    "disease": "pages/5_Disease_Detection.py",
    "pest": "pages/6_Pest_Control.py",
}

pg = st.navigation(
    [home_page, ai_page, sensor_page, alerts_page, camera_page, disease_page, pest_page],
    position="hidden",
)
pg.run()
