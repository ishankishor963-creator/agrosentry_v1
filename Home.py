import streamlit as st

from utils.auth import logout_button, require_login
from utils.esp_client import get_sensor_data
from utils.theme import inject_theme, topnav

# --- Auth gate: nothing below this line renders until logged in ---
require_login()

st.set_page_config(
    page_title="AgroSentry — Farm Ops",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- One-time session state defaults ---
if "esp_base_url" not in st.session_state:
    st.session_state["esp_base_url"] = ""

inject_theme()


def render_custom_css():
    """Injects high-end dark AI SaaS styles, custom glassmorphism, glowing micro-interactions,
    radar visual keyframes, and custom button styling overrides."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

            /* Global Reset & Futuristic Theme */
            html, body, [data-testid="stAppViewContainer"] {
                background-color: #050608 !important;
                color: #F9FAFB !important;
                font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
            }

            /* Hide Streamlit Chrome */
            #MainMenu, header, footer { visibility: hidden; }
            [data-testid="stHeader"] { background-color: transparent !important; }
            .stDeployButton { display: none !important; }

            /* Sidebar Styling */
            [data-testid="stSidebar"] {
                background-color: #090C12 !important;
                border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
            }

            /* Eyebrow Labels */
            .eyebrow-text {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.72rem;
                font-weight: 600;
                letter-spacing: 0.15em;
                text-transform: uppercase;
                color: #FF9500;
                margin-bottom: 0.5rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .eyebrow-text::before {
                content: '';
                display: inline-block;
                width: 7px;
                height: 7px;
                background-color: #FF9500;
                border-radius: 50%;
                box-shadow: 0 0 10px #FF9500;
            }

            /* Typography */
            .hero-title {
                font-size: 3.4rem;
                font-weight: 800;
                line-height: 1.1;
                letter-spacing: -0.03em;
                background: linear-gradient(180deg, #FFFFFF 0%, #A1A1AA 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 1.25rem;
            }

            .hero-title span {
                background: linear-gradient(135deg, #FF9500 0%, #F59E0B 50%, #EAB308 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .hero-desc {
                font-size: 1.05rem;
                color: #9CA3AF;
                line-height: 1.6;
                margin-bottom: 2rem;
                max-width: 580px;
            }

            /* Glassmorphism Containers */
            .glass-card {
                background: linear-gradient(135deg, rgba(18, 24, 36, 0.6) 0%, rgba(10, 13, 20, 0.85) 100%);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
                padding: 1.5rem;
                transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                position: relative;
                overflow: hidden;
            }

            .glass-card:hover {
                border-color: rgba(255, 149, 0, 0.35);
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6), 0 0 20px rgba(255, 149, 0, 0.08);
            }

            /* Futuristic Radar Visual */
            .radar-box {
                position: relative;
                width: 100%;
                height: 380px;
                background: radial-gradient(circle at center, rgba(18, 24, 36, 0.8) 0%, rgba(5, 6, 8, 0.95) 75%);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
                box-shadow: inset 0 0 60px rgba(0, 0, 0, 0.9);
            }

            .radar-grid {
                position: absolute;
                width: 100%;
                height: 100%;
                background-image: 
                    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
                background-size: 30px 30px;
            }

            .radar-circle {
                position: absolute;
                border: 1px dashed rgba(255, 149, 0, 0.25);
                border-radius: 50%;
            }

            .radar-circle.c1 { width: 110px; height: 110px; }
            .radar-circle.c2 { width: 210px; height: 210px; border-style: solid; border-color: rgba(255, 255, 255, 0.06); }
            .radar-circle.c3 { width: 310px; height: 310px; }

            .radar-sweep-beam {
                position: absolute;
                width: 310px;
                height: 310px;
                border-radius: 50%;
                background: conic-gradient(from 0deg, rgba(255, 149, 0, 0.28) 0deg, transparent 60deg, transparent 360deg);
                animation: radar-spin 6s linear infinite;
            }

            @keyframes radar-spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            .radar-center-dot {
                width: 12px;
                height: 12px;
                background-color: #FF9500;
                border-radius: 50%;
                box-shadow: 0 0 15px #FF9500, 0 0 30px #FF9500;
                z-index: 5;
            }

            .hud-badge {
                position: absolute;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.68rem;
                padding: 5px 12px;
                border-radius: 6px;
                background: rgba(13, 16, 20, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.12);
                color: #E5E7EB;
                display: flex;
                align-items: center;
                gap: 6px;
                backdrop-filter: blur(8px);
                z-index: 10;
            }

            .hud-badge-dot {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background-color: #10B981;
                box-shadow: 0 0 8px #10B981;
            }

            .hud-pos-1 { top: 22px; left: 22px; }
            .hud-pos-2 { top: 22px; right: 22px; }
            .hud-pos-3 { bottom: 22px; left: 22px; }
            .hud-pos-4 { bottom: 22px; right: 22px; }

            /* Custom Badges & Chips */
            .chip {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.68rem;
                font-weight: 600;
                padding: 3px 10px;
                border-radius: 100px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                display: inline-block;
            }

            .chip-green, .badge-green {
                background: rgba(16, 185, 129, 0.12);
                color: #10B981;
                border: 1px solid rgba(16, 185, 129, 0.3);
            }

            .chip-amber, .badge-amber {
                background: rgba(245, 158, 11, 0.12);
                color: #F59E0B;
                border: 1px solid rgba(245, 158, 11, 0.3);
            }

            .chip-cyan, .badge-cyan {
                background: rgba(6, 182, 212, 0.12);
                color: #06B6D4;
                border: 1px solid rgba(6, 182, 212, 0.3);
            }

            .chip-pink, .badge-pink {
                background: rgba(236, 72, 153, 0.12);
                color: #EC4899;
                border: 1px solid rgba(236, 72, 153, 0.3);
            }

            /* Metric Cards */
            .stat-card {
                background: linear-gradient(180deg, rgba(18, 24, 36, 0.7) 0%, rgba(13, 16, 22, 0.9) 100%);
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 14px;
                padding: 1.25rem;
                position: relative;
            }

            .stat-label {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.68rem;
                color: #9CA3AF;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
            }

            .stat-val-row {
                display: flex;
                align-items: baseline;
                justify-content: space-between;
            }

            .stat-value {
                font-size: 2.1rem;
                font-weight: 700;
                color: #FFFFFF;
                letter-spacing: -0.02em;
            }

            .stat-status {
                font-size: 0.75rem;
                font-weight: 600;
                color: #10B981;
                margin-top: 0.35rem;
            }

            /* Progress Bar Visualizer */
            .progress-bar-bg {
                width: 100%;
                height: 6px;
                background: rgba(255, 255, 255, 0.08);
                border-radius: 100px;
                overflow: hidden;
                margin-top: 8px;
            }

            .progress-bar-fill {
                height: 100%;
                border-radius: 100px;
                background: linear-gradient(90deg, #FF9500 0%, #10B981 100%);
                box-shadow: 0 0 10px rgba(255, 149, 0, 0.4);
            }

            /* Module Cards */
            .module-card {
                background: linear-gradient(135deg, rgba(18, 24, 36, 0.5) 0%, rgba(10, 13, 20, 0.8) 100%);
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 16px;
                padding: 1.5rem;
                min-height: 180px;
            }

            .module-card-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 0.85rem;
            }

            .module-icon {
                font-size: 1.8rem;
            }

            .module-title {
                font-size: 1.15rem;
                font-weight: 700;
                color: #FFFFFF;
                margin-bottom: 0.4rem;
            }

            .module-desc {
                font-size: 0.88rem;
                color: #9CA3AF;
                line-height: 1.5;
                margin-bottom: 1rem;
            }

            /* Streamlit Native Buttons Override */
            div.stButton > button {
                background: rgba(255, 255, 255, 0.05) !important;
                color: #F3F4F6 !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                border-radius: 10px !important;
                padding: 0.5rem 1rem !important;
                font-weight: 600 !important;
                font-size: 0.88rem !important;
                transition: all 0.2s ease !important;
                width: 100%;
            }

            div.stButton > button:hover {
                background: linear-gradient(135deg, #FF9500 0%, #E67E00 100%) !important;
                color: #000000 !important;
                border-color: #FF9500 !important;
                box-shadow: 0 4px 15px rgba(255, 149, 0, 0.35) !important;
                transform: translateY(-1px);
            }

            .section-header {
                margin-top: 2.5rem;
                margin-bottom: 1.5rem;
            }

            .section-title {
                font-size: 1.75rem;
                font-weight: 700;
                color: #FFFFFF;
                letter-spacing: -0.02em;
            }

            .section-subtitle {
                font-size: 0.92rem;
                color: #9CA3AF;
            }

            /* System Footer */
            .system-footer {
                margin-top: 4rem;
                padding: 1.5rem 0;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
                display: flex;
                align-items: center;
                justify-content: space-between;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.72rem;
                color: #6B7280;
            }

            .footer-status-item {
                display: flex;
                align-items: center;
                gap: 6px;
            }

            .status-dot-active {
                width: 6px;
                height: 6px;
                background-color: #10B981;
                border-radius: 50%;
                box-shadow: 0 0 6px #10B981;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    """Renders top navigation bar using custom theme utility."""
    topnav("home")


def render_hero():
    """Renders high-impact cinematic hero section with dual action buttons and CSS visual HUD."""
    col1, col2 = st.columns([1.15, 0.85], gap="large")

    with col1:
        st.markdown(
            """
            <div style="padding-top: 0.5rem;">
                <div class="eyebrow-text">AI-POWERED FARM INTELLIGENCE</div>
                <h1 class="hero-title">Smarter Farming.<br><span>Powered by AI.</span></h1>
                <p class="hero-desc">
                    Monitor your crops, understand your environmental risks, and respond to micro-climate anomalies before they affect your agricultural yield.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            if st.button("🤖 OPEN AI ASSISTANT", key="hero_ai_btn"):
                st.switch_page("pages/1_AI_Assistant.py")
        with btn_col2:
            if st.button("🌡️ VIEW SENSORS", key="hero_sensor_btn"):
                st.switch_page("pages/2_Sensor_Dashboard.py")

    with col2:
        st.markdown(
            """
            <div class="radar-box">
                <div class="radar-grid"></div>
                <div class="radar-circle c1"></div>
                <div class="radar-circle c2"></div>
                <div class="radar-circle c3"></div>
                <div class="radar-sweep-beam"></div>
                <div class="radar-center-dot"></div>
                
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
            """,
            unsafe_allow_html=True,
        )


def render_sensor_cards(reading):
    """Renders 4 custom statistics cards using actual live/demo reading values from get_sensor_data()."""
    st.markdown(
        """
        <div class="section-header">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div class="eyebrow-text">TELEMETRY DATA</div>
                    <h2 class="section-title">Farm Overview</h2>
                </div>
                <span class="chip chip-green">● LIVE MONITORING</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    soil = reading.get("soil_moisture", 0)
    humidity = reading.get("humidity", 0)
    temp = reading.get("temperature", 0)
    source = reading.get("source", "demo")

    is_live = source == "device"
    source_str = "LIVE DEVICE" if is_live else "DEMO MODE"
    source_class = "chip-green" if is_live else "chip-amber"

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">SOIL MOISTURE</div>
                <div class="stat-val-row">
                    <div class="stat-value">{soil}%</div>
                    <svg width="60" height="24" viewBox="0 0 60 24" fill="none">
                        <path d="M0 18 L12 14 L24 16 L36 8 L48 10 L60 4" stroke="#FF9500" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
                <div class="stat-status">
                    <span style="color: #10B981;">OPTIMAL</span> FIELD HYDRATION
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">HUMIDITY</div>
                <div class="stat-val-row">
                    <div class="stat-value">{humidity}%</div>
                    <svg width="60" height="24" viewBox="0 0 60 24" fill="none">
                        <path d="M0 10 L15 12 L30 6 L45 18 L60 8" stroke="#06B6D4" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
                <div class="stat-status" style="color: #06B6D4;">
                    BALANCED ATMOSPHERE
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">TEMPERATURE</div>
                <div class="stat-val-row">
                    <div class="stat-value">{temp}°C</div>
                    <svg width="60" height="24" viewBox="0 0 60 24" fill="none">
                        <path d="M0 14 L15 8 L30 15 L45 5 L60 12" stroke="#F59E0B" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
                <div class="stat-status" style="color: #F59E0B;">
                    STABLE CONDITIONS
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">SYSTEM DATA SOURCE</div>
                <div class="stat-val-row">
                    <div class="stat-value" style="font-size: 1.4rem; padding-top: 0.4rem;">{source_str}</div>
                </div>
                <div style="margin-top: 0.65rem;">
                    <span class="chip {source_class}">{"ONLINE" if is_live else "SIMULATED"}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_farm_intelligence():
    """Renders main dashboard diagnostic panel with multi-variable glowing progress bars."""
    st.write("")
    st.markdown(
        """
        <div class="glass-card" style="margin-top: 1rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem;">
                <div>
                    <div class="eyebrow-text">SYNTHETIC ANALYSIS</div>
                    <h3 style="font-size: 1.3rem; font-weight: 700; color: #FFFFFF; margin: 0;">Farm Intelligence Diagnostics</h3>
                </div>
                <span class="chip chip-cyan">AI EVALUATED</span>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <span style="color: #9CA3AF;">Crop Health</span>
                        <span style="color: #10B981; font-weight: 700;">86% (Excellent)</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: 86%;"></div>
                    </div>
                </div>
                
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <span style="color: #9CA3AF;">Water Status</span>
                        <span style="color: #06B6D4; font-weight: 700;">92% (Optimal)</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: 92%; background: linear-gradient(90deg, #06B6D4, #3B82F6);"></div>
                    </div>
                </div>
                
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <span style="color: #9CA3AF;">Weather Risk</span>
                        <span style="color: #10B981; font-weight: 700;">14% (Low)</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: 14%; background: #10B981;"></div>
                    </div>
                </div>
                
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <span style="color: #9CA3AF;">Pest Risk</span>
                        <span style="color: #10B981; font-weight: 700;">8% (Low)</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: 8%; background: #10B981;"></div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_module_card(col, icon, title, desc, target, badge_label, badge_class, key):
    """Reusable helper for rendering individual module cards in the dashboard grid."""
    with col:
        st.markdown(
            f"""
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
            """,
            unsafe_allow_html=True,
        )
        if st.button(f"Launch {title} →", key=key, use_container_width=True):
            st.switch_page(target)


def render_modules():
    """Renders the 6 module cards arranged in a sleek 2x3 grid."""
    st.markdown(
        """
        <div class="section-header">
            <div>
                <div class="eyebrow-text">MODULAR SUITE</div>
                <h2 class="section-title">Explore AgroSentry</h2>
            </div>
            <div class="section-subtitle">Everything you need to monitor, analyze, and protect your farm.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_row1 = st.columns(3)
    col_row2 = st.columns(3)

    render_module_card(
        col_row1[0],
        "🤖",
        "AI Assistant",
        "Ask farming questions and receive intelligent recommendations.",
        "pages/1_AI_Assistant.py",
        "AI",
        "chip-cyan",
        "btn_ai",
    )

    render_module_card(
        col_row1[1],
        "🌡️",
        "Sensor Dashboard",
        "Monitor live soil moisture, humidity, temperature, and environmental conditions.",
        "pages/2_Sensor_Dashboard.py",
        "LIVE",
        "chip-green",
        "btn_sensor",
    )

    render_module_card(
        col_row1[2],
        "🚨",
        "Flood / Drought Alerts",
        "Detect climate risks and receive early warnings from sensor trends.",
        "pages/3_Flood_Drought_Alerts.py",
        "ALERT",
        "chip-pink",
        "btn_alerts",
    )

    render_module_card(
        col_row2[0],
        "📷",
        "Camera Feed",
        "Monitor your field visually through the connected camera.",
        "pages/4_Camera_Feed.py",
        "VISION",
        "chip-cyan",
        "btn_camera",
    )

    render_module_card(
        col_row2[1],
        "🔬",
        "Disease Detection",
        "Upload crop leaf photos and identify possible diseases with AI.",
        "pages/5_Disease_Detection.py",
        "AI MODEL",
        "chip-amber",
        "btn_disease",
    )

    render_module_card(
        col_row2[2],
        "🐛",
        "Pest Control",
        "Monitor environmental pest risks and support integrated pest management.",
        "pages/6_Pest_Control.py",
        "IPM",
        "chip-pink",
        "btn_pest",
    )


def render_device_status():
    """Sidebar hardware device connection panel preserving st.session_state['esp_base_url'] logic."""
    with st.sidebar:
        st.markdown(
            """
            <div style="padding-bottom: 0.5rem;">
                <div class="eyebrow-text" style="font-size: 0.65rem;">HARDWARE LINK</div>
                <h3 style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF; margin: 0;">Device Status</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        connected = bool(st.session_state.get("esp_base_url", ""))
        chip = (
            '<span class="chip chip-green">CONNECTED</span>'
            if connected
            else '<span class="chip chip-amber">DEMO MODE</span>'
        )
        st.markdown(chip, unsafe_allow_html=True)
        st.write("")

        st.session_state["esp_base_url"] = st.text_input(
            "ESP32 / Raspberry Pi base URL",
            value=st.session_state["esp_base_url"],
            placeholder="http://192.168.1.42",
            help=(
                "The IP address your ESP32/Pi prints over serial when it connects "
                "to WiFi. Leave blank to run every page in demo mode with sample data."
            ),
        )

        if connected:
            st.success("Pages will fetch live edge data.")
        else:
            st.info("Pages will display demo data.")

        st.divider()
        logout_button()


def render_footer(reading):
    """Renders bottom minimal system operational footer."""
    source = reading.get("source", "demo")
    esp_status = "CONNECTED" if source == "device" else "DEMO MODE"

    st.markdown(
        f"""
        <div class="system-footer">
            <div>AGROSENTRY AI FARM INTELLIGENCE</div>
            <div class="footer-status-item">
                <span class="status-dot-active"></span>
                SYSTEM STATUS: OPERATIONAL
            </div>
            <div>ESP32: {esp_status}</div>
            <div>AI ENGINE: READY</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def home():
    """Homepage entry point assembling all dark AI SaaS UI components."""
    render_custom_css()
    render_device_status()
    render_header()
    render_hero()

    # Pull real or simulated sensor data
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

# Registry for custom top nav switch_page() mapping
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
