import streamlit as st
import requests
import random
import math

API_URL = "https://disaster-response-system-ppci.onrender.com"

# Page config
st.set_page_config(
    page_title="Disaster Response System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SESSION STATE ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'active_panel' not in st.session_state:
    st.session_state.active_panel = None

if 'medical_stats' not in st.session_state:
    st.session_state.medical_stats = {"Critical": 0, "Serious": 0, "Minor": 0, "Deceased": 0, "Total": 0}

if 'med_checklist' not in st.session_state:
    st.session_state.med_checklist = [False] * 7

if 'med_inventory' not in st.session_state:
    st.session_state.med_inventory = {
        "Bandages": "Stocked", "Tourniquets": "Stocked", "IV Fluids": "Stocked",
        "Morphine": "Low", "Oxygen Masks": "Stocked", "Defibrillator": "Stocked"
    }

if 'protocol_responses' not in st.session_state:
    st.session_state.protocol_responses = {}

if 'evacuation_request' not in st.session_state:
    st.session_state.evacuation_request = None

if 'nav_ai_res' not in st.session_state:
    st.session_state.nav_ai_res = None
if 'user_coords' not in st.session_state:
    st.session_state.user_coords = [28.6600, 77.2300]
if 'nav_speech' not in st.session_state:
    st.session_state.nav_speech = ''

OLLAMA_URL = "http://localhost:11434/api/generate"

def query_ollama(prompt):
    try:
        payload = {"model": "gemma4:e4b", "prompt": prompt, "stream": False}
        res = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if res.status_code == 200:
            return res.json().get("response", "Error: No response")
        return f"Error: Server returned {res.status_code}"
    except Exception as e:
        return f"Offline Error: {e}"

# --- DARK MODE TOGGLE (top-right) ---
col_title, col_spacer, col_toggle = st.columns([6, 3, 1])
with col_toggle:
    new_dark = st.toggle("🌙 Dark", value=st.session_state.dark_mode)
    if new_dark != st.session_state.dark_mode:
        st.session_state.dark_mode = new_dark
        st.rerun()

# --- THEME COLORS ---
if st.session_state.dark_mode:
    bg_color = "#0F172A"
    card_bg = "#1E293B"
    text_color = "#F8FAFC"
    sub_text = "#94A3B8"
    border_color = "#334155"
    primary_btn = "#38BDF8"
    expander_bg = "#1E293B"
    expander_text = "#F8FAFC"
    browse_bg = "#38BDF8"
    browse_text = "#FFFFFF"
else:
    bg_color = "#F4F7F9"
    card_bg = "#FFFFFF"
    text_color = "#1E293B"
    sub_text = "#64748B"
    border_color = "#E2E8F0"
    primary_btn = "#1D6B99"
    expander_bg = "#E0F2FE"
    expander_text = "#1E293B"
    browse_bg = "#1D6B99"
    browse_text = "#FFFFFF"

# --- CSS ---
css_code = """
<style>
    html, body, p, span, div, label, h1, h2, h3, h4, h5, h6, [class*="css"] {
        font-family: 'Times New Roman', Times, serif;
        color: {text_color} !important;
    }

    /* Keep code block text visible on dark backgrounds */
    [data-testid="stCode"] code,
    [data-testid="stCode"] pre,
    [data-testid="stCode"] span,
    pre code, pre span {
        color: #E2E8F0 !important;
    }

    .stApp, [data-testid="stHeader"] {
        background-color: {bg_color} !important;
    }

    /* Toggle pill */
    label[data-baseweb="checkbox"] {
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 20px;
        padding: 5px 12px;
    }

    /* CRITICAL FIX: Force all selectbox components to follow theme */
    div[data-testid="stSelectbox"] *, 
    div[data-baseweb="select"] *, 
    div[data-baseweb="popover"] *,
    div[data-testid="stVirtualDropdown"] * {
        background-color: {card_bg} !important;
        color: {text_color} !important;
    }
    
    /* Input Widgets (Textarea, Input, FileUploader) */
    [data-baseweb="textarea"] textarea,
    [data-baseweb="input"] input,
    [data-testid="stFileUploaderDropzone"] {
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border: 1.5px solid {border_color} !important;
        border-radius: 6px !important;
    }
    textarea {
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
    }

    /* CRITICAL SELECTBOX FIX: Force white/dark contrast */
    div.stSelectbox div, div.stSelectbox span, div.stSelectbox svg {
        background-color: {card_bg} !important;
        color: {text_color} !important;
    }
    div[data-baseweb="popover"] *, div[role="listbox"] *, div[role="option"] * {
        background-color: {card_bg} !important;
        color: {text_color} !important;
    }
    div[role="option"]:hover {
        background-color: {primary_btn}20 !important;
        color: {primary_btn} !important;
    }

    /* Expander header */
    [data-testid="stExpander"] summary {
        background-color: {expander_bg} !important;
        color: {expander_text} !important;
        padding: 0.6rem 1rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stExpander"] summary:hover {
        filter: brightness(0.95);
    }

    /* Browse files button */
    div[data-testid="stFileUploader"] button {
        background-color: {browse_bg} !important;
        color: {browse_text} !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        padding: 0.5rem 1.5rem !important;
    }

    /* Hero */
    .hero-container {
        text-align: center;
        padding: 2rem 1rem 1rem;
    }
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }
    .hero-title span { color: {primary_btn}; }
    .hero-subtitle {
        font-size: 1.1rem;
        color: {sub_text} !important;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Feature buttons & boxes - Unified Look */
    .stat-box, div.stButton > button {
        border: 1px solid {border_color} !important;
        border-radius: 16px !important;
        padding: 1.2rem !important;
        background-color: {card_bg} !important;
        color: {text_color} !important;
        text-align: center !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.3s ease !important;
        font-weight: 600 !important;
        width: 100% !important;
        display: block !important;
        height: auto !important;
        line-height: 1.5 !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08) !important;
        border-color: {primary_btn} !important;
    }

    /* Primary buttons (Get Response Plan, etc.) */
    div.stButton > button[kind="primary"] {
        background-color: {primary_btn} !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #155A8A !important;
        transform: translateY(-2px) !important;
    }

    /* Specific accents */
    .med-accent { border-top: 5px solid #EF4444 !important; border-radius: 16px 16px 0 0; position: relative; z-index: 10; margin-bottom: -5px; }
    .map-accent { border-top: 5px solid #3B82F6 !important; border-radius: 16px 16px 0 0; position: relative; z-index: 10; margin-bottom: -5px; }
    .vision-accent { border-top: 5px solid #8B5CF6 !important; border-radius: 16px 16px 0 0; position: relative; z-index: 10; margin-bottom: -5px; }
    .feat-btn:hover {
        border-color: {primary_btn};
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
</style>
"""

# Replace variables in CSS
for var_name in ["text_color", "bg_color", "card_bg", "border_color", "primary_btn", "sub_text", "expander_bg", "expander_text", "browse_bg", "browse_text"]:
    if var_name in locals():
        css_code = css_code.replace("{" + var_name + "}", locals()[var_name])

st.markdown(css_code, unsafe_allow_html=True)

if 'nav_transcription' not in st.session_state:
    st.session_state.nav_transcription = ""
if 'nav_ai_res' not in st.session_state:
    st.session_state.nav_ai_res = None
if 'user_coords' not in st.session_state:
    st.session_state.user_coords = (28.66, 77.23) # Default Delhi

# --- THEME COLORS ---
# (already defined above, just making sure the CSS block starts correctly)

# --- MORE CSS ---
css_code_2 = """
<style>
    /* Mic Button & Pulse Animation */
    .mic-nav-container {
        text-align: center;
        padding: 2rem;
    }
    .mic-nav-btn {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background-color: #EF4444;
        border: none;
        color: white;
        font-size: 32px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        position: relative;
        z-index: 1;
        transition: all 0.3s ease;
    }
    .mic-nav-btn.recording {
        animation: pulse-red 1.5s infinite;
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    /* Soundwave animation */
    .soundwave {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        height: 40px;
        margin-top: 15px;
    }
    .soundwave span {
        width: 4px;
        height: 10px;
        background: #EF4444;
        border-radius: 2px;
        animation: wave 1s infinite alternate;
    }
    .soundwave span:nth-child(2) { animation-delay: 0.2s; }
    .soundwave span:nth-child(3) { animation-delay: 0.4s; }
    .soundwave span:nth-child(4) { animation-delay: 0.6s; }
    @keyframes wave {
        from { height: 10px; }
        to { height: 30px; }
    }

    /* Smaller Command Center Title */
    .med-title {
        font-size: 18px !important;
        font-weight: 500 !important;
        text-align: left !important;
        margin-top: -10px !important;
        margin-bottom: 15px !important;
        color: {text_color} !important;
    }

    /* Mobile-friendly Inputs (44px height) */
    div[data-testid="stNumberInput"] div,
    div[data-testid="stNumberInput"] input,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="input"] input,
    [data-testid="stFileUploaderDropzone"] {
        min-height: 44px !important;
        height: 44px !important;
        font-size: 16px !important;
    }

    /* Protocol Buttons (Problem 2) */
    div[data-testid="column"] button[key^="prot_"] {
        min-height: 100px !important;
        padding: 10px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        text-align: left !important;
    }

    /* Supply Inventory Cards (Problem 1) */
    .supply-card {
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        padding: 12px !important;
        background: {card_bg} !important;
        margin-bottom: 5px !important;
        text-align: center !important;
        color: {text_color} !important;
        font-weight: 600 !important;
    }

    /* REDESIGN: Panic-Proof UI */
    .panic-sos-btn {
        width: 100%;
        height: 80px !important;
        background-color: #EF4444 !important;
        color: white !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        border-radius: 16px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
        margin-bottom: 2rem;
    }

    .category-row {
        display: flex;
        gap: 12px;
        margin-bottom: 2rem;
    }
    .panic-card {
        flex: 1;
        height: 140px;
        border-radius: 16px;
        padding: 1.2rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        cursor: pointer;
        transition: transform 0.2s;
        border: 1px solid rgba(0,0,0,0.05);
    }
    .panic-card:active { transform: scale(0.95); }
    .panic-card i { font-size: 40px; margin-bottom: 8px; }
    .panic-card-title { font-weight: 800; font-size: 18px; margin: 0; }
    .panic-card-sub { font-size: 13px; opacity: 0.8; margin-top: 4px; }

    .protocol-list-btn {
        width: 100%;
        height: 56px !important;
        background: white !important;
        color: #1E293B !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: 0 1.2rem !important;
        margin-bottom: 8px !important;
        font-weight: 600 !important;
    }

    .checklist-progress {
        background: #F1F5F9;
        border-radius: 99px;
        padding: 8px 16px;
        font-weight: 800;
        font-size: 18px;
        color: #0F172A;
        display: inline-block;
        margin-bottom: 1rem;
    }

    /* Checklist Gap Fix */
    [data-testid="stCheckbox"] {
        padding: 12px 0 !important;
        min-height: 56px !important;
        border-bottom: 1px solid #F1F5F9;
    }
</style>
"""

for var_name in ["text_color", "bg_color", "card_bg", "border_color", "primary_btn", "sub_text"]:
    if var_name in locals():
        css_code_2 = css_code_2.replace("{" + var_name + "}", locals()[var_name])

st.markdown(css_code_2, unsafe_allow_html=True)

# ============================================================
#  LANDING PAGE
# ============================================================
if not st.session_state.analyzed:
    # Hide hero if a panel is active to focus on the tool
    if st.session_state.active_panel is None:
        st.markdown(f"""
        <div class="hero-container">
            <div class="hero-title">Disaster <span>Response</span> System</div>
            <div class="hero-subtitle">Coordinate emergency response with AI-powered triage and real-time monitoring.</div>
        </div>
        """, unsafe_allow_html=True)

    # --- TWO FEATURE BUTTONS ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="med-accent"></div>', unsafe_allow_html=True)
        if st.button("🩺 Medical Emergency", use_container_width=True, key="med_btn_main"):
            st.session_state.active_panel = 'medical' if st.session_state.active_panel != 'medical' else None
            st.rerun()

    with col_b:
        st.markdown('<div class="map-accent"></div>', unsafe_allow_html=True)
        if st.button("🗺 Navigation to safe place", use_container_width=True, key="map_btn_main"):
            st.session_state.active_panel = 'offline_map' if st.session_state.active_panel != 'offline_map' else None
            st.rerun()

    # --- PANEL: Medical Emergency (Full Suite Redesign) ---
    if st.session_state.active_panel == 'medical':
        # Initialize internal state if missing
        if 'expanded_section' not in st.session_state:
            st.session_state.expanded_section = None
        if 'sos_response' not in st.session_state:
            st.session_state.sos_response = None

        st.markdown(f'<div style="padding: 1.5rem; border-radius: 12px; background: {card_bg}; margin-top: 1rem;">', unsafe_allow_html=True)
        
        # SECTION 1: Big SOS Button
        if st.button("🆘 SOS — Get Emergency Help", key="panic_sos", use_container_width=True, type="primary"):
            with st.spinner("Requesting SOS guidance..."):
                prompt = "Generate an emergency medical evacuation request as a radio transmission message. Include: situation summary, number of critical patients, supplies urgently needed. Be concise."
                st.session_state.sos_response = query_ollama(prompt)
        
        if st.session_state.sos_response:
            with st.expander("🚨 SOS RESPONSE DATA", expanded=True):
                st.code(st.session_state.sos_response, language="markdown")
                if st.button("🗑 Clear SOS"):
                    st.session_state.sos_response = None
                    st.rerun()

        st.markdown('<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True)

        # SECTION: Emergency Helplines
        helpline_html = """
        <style>
            .helpline-container { text-align: left; font-family: 'Inter', sans-serif; }
            .h-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
            .h-dot { width: 10px; height: 10px; border-radius: 50%; background: #64748B; }
            .h-status { font-size: 12px; color: #64748B; font-weight: 500; margin-bottom: 12px; }
            
            .h-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
            .h-card {
                height: 80px;
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 12px;
                transition: all 0.2s;
            }
            .h-card:hover { border-color: #CBD5E1; }
            .h-left { display: flex; align-items: center; gap: 10px; }
            .h-icon { font-size: 24px; }
            .h-name { font-weight: 700; font-size: 14px; color: #334155; }
            .h-right { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
            .h-num { font-weight: 800; font-size: 18px; color: #1E293B; }
            .h-call-btn {
                background: #10B981;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 4px 14px;
                font-weight: 800;
                font-size: 11px;
                text-transform: uppercase;
                cursor: pointer;
            }
            .h-card.offline { filter: grayscale(1); opacity: 0.6; pointer-events: none; }
        </style>

        <div class="helpline-container">
            <div class="h-header">
                <h4 style="margin:0; font-size:18px; color:#1E293B;">🚨 Emergency Helplines</h4>
                <div id="net-dot" class="h-dot"></div>
            </div>
            <div id="net-status" class="h-status">Checking network...</div>

            <div id="h-grid" class="h-grid">
                <div class="h-card" style="border-left: 4px solid #3B82F6;">
                    <div class="h-left"><span class="h-icon">🛡</span><span class="h-name">Police</span></div>
                    <div class="h-right"><span class="h-num">112</span><button class="h-call-btn" onclick="makeCall('112')">CALL</button></div>
                </div>
                <div class="h-card" style="border-left: 4px solid #EF4444;">
                    <div class="h-left"><span class="h-icon">🩺</span><span class="h-name">Ambulance</span></div>
                    <div class="h-right"><span class="h-num">108</span><button class="h-call-btn" onclick="makeCall('108')">CALL</button></div>
                </div>
                <div class="h-card" style="border-left: 4px solid #F59E0B;">
                    <div class="h-left"><span class="h-icon">🔥</span><span class="h-name">Fire</span></div>
                    <div class="h-right"><span class="h-num">101</span><button class="h-call-btn" onclick="makeCall('101')">CALL</button></div>
                </div>
                <div class="h-card" style="border-left: 4px solid #8B5CF6;">
                    <div class="h-left"><span class="h-icon">⚠</span><span class="h-name">Disaster</span></div>
                    <div class="h-right"><span class="h-num">1078</span><button class="h-call-btn" onclick="makeCall('1078')">CALL</button></div>
                </div>
                <div class="h-card" style="border-left: 4px solid #EC4899;">
                    <div class="h-left"><span class="h-icon">👩</span><span class="h-name">Women</span></div>
                    <div class="h-right"><span class="h-num">1091</span><button class="h-call-btn" onclick="makeCall('1091')">CALL</button></div>
                </div>
                <div class="h-card" style="border-left: 4px solid #EAB308;">
                    <div class="h-left"><span class="h-icon">👶</span><span class="h-name">Child</span></div>
                    <div class="h-right"><span class="h-num">1098</span><button class="h-call-btn" onclick="makeCall('1098')">CALL</button></div>
                </div>
            </div>
        </div>

        <script>
            function updateNet() {
                const isOn = navigator.onLine;
                const dot = document.getElementById('net-dot');
                const stat = document.getElementById('net-status');
                if(isOn) {
                    dot.style.background = '#10B981';
                    stat.innerText = "Network available • Calls active";
                    document.querySelectorAll('.h-card').forEach(c => c.classList.remove('offline'));
                } else {
                    dot.style.background = '#EF4444';
                    stat.innerText = "No network • Calls unavailable";
                    document.querySelectorAll('.h-card').forEach(c => c.classList.add('offline'));
                }
            }
            window.addEventListener('online', updateNet);
            window.addEventListener('offline', updateNet);
            updateNet();
            function makeCall(n) {
                window.location.href = 'tel:' + n;
            }
        </script>
        """
        st.components.v1.html(helpline_html, height=330)

        st.markdown('<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True)

        # SECTION 2: What do you need? (3 Big Cards)
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("""
                <div class="panic-card" style="background: #FEE2E2; color: #991B1B;">
                    <i>🩹</i>
                    <div class="panic-card-title">First Aid</div>
                    <div class="panic-card-sub">CPR, Bleeding, Burns</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open First Aid", key="btn_expand_fa", use_container_width=True):
                st.session_state.expanded_section = 'first_aid' if st.session_state.expanded_section != 'first_aid' else None
                st.rerun()

        with c2:
            st.markdown("""
                <div class="panic-card" style="background: #E0F2FE; color: #0369A1;">
                    <i>📍</i>
                    <div class="panic-card-title">I am Lost</div>
                    <div class="panic-card-sub">Find Safe Place</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open Navigator", key="btn_expand_map", use_container_width=True):
                st.session_state.active_panel = 'offline_map'
                st.rerun()

        with c3:
            st.markdown("""
                <div class="panic-card" style="background: #DCFCE7; color: #166534;">
                    <i>✅</i>
                    <div class="panic-card-title">Checklist</div>
                    <div class="panic-card-sub">Responder Steps</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open Checklist", key="btn_expand_chk", use_container_width=True):
                st.session_state.expanded_section = 'checklist' if st.session_state.expanded_section != 'checklist' else None
                st.rerun()

        st.markdown('<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True)

        # SECTION 3: Expanded First Aid
        if st.session_state.expanded_section == 'first_aid':
            st.markdown("### 📖 First Aid Protocols")
            protocols = [
                ("CPR", "â¤"), ("Bleeding", "🩸"), ("Spinal Injury", "🦴"),
                ("Burns", "🔥"), ("Shock", "📉"), ("Crush Injury", "🏗️")
            ]
            p_prompts = {
                "CPR": "Give step by step CPR instructions for adult, child, and infant. Concise numbered list.",
                "Bleeding": "How to stop severe bleeding and apply a tourniquet. Numbered steps.",
                "Spinal Injury": "Suspected spinal injury dos and don'ts. Be brief.",
                "Burns": "Burns treatment without hospital access. Cooling and covering.",
                "Shock": "Shock first aid — positioning and care. Numbered steps.",
                "Crush Injury": "Trapped under debris — rescue breathing and crush syndrome first aid."
            }

            for name, icon in protocols:
                if st.button(f"{icon} {name}", key=f"pbtn_{name}", use_container_width=True):
                    with st.spinner(f"Getting {name} steps..."):
                        st.session_state.protocol_responses[name] = query_ollama(p_prompts[name])
                
                if name in st.session_state.protocol_responses:
                    st.info(st.session_state.protocol_responses[name])

        # SECTION 4: Expanded Checklist
        if st.session_state.expanded_section == 'checklist':
            st.markdown("### ✅ Responder Steps")
            chk_items = [
                "Scene safe — hazards assessed", "Gloves and PPE worn", "Patient conscious and responsive",
                "Airway open and clear", "Bleeding controlled", "Triage tag assigned", "Patient moved to safe zone"
            ]
            completed = 0
            for idx, item in enumerate(chk_items):
                st.session_state.med_checklist[idx] = st.checkbox(item, value=st.session_state.med_checklist[idx], key=f"panic_chk_{idx}")
                if st.session_state.med_checklist[idx]: completed += 1
            
            st.markdown(f'<div class="checklist-progress">{completed} / 7 DONE</div>', unsafe_allow_html=True)
            if st.button("♻️ Reset Checklist", use_container_width=True):
                st.session_state.med_checklist = [False] * 7
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # --- PANEL: Navigation to Safe Place (Voice Navigator) ---
    if st.session_state.active_panel == 'offline_map':
        st.markdown('<div class="med-title">🧭 Voice to Safe Place Navigator</div>', unsafe_allow_html=True)
        nav_html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
        <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
        <style>
            body{font-family:Inter,sans-serif;margin:0;padding:0;background:transparent}
            .nav-container{text-align:center;padding:10px}
            .lang-toggle{display:flex;justify-content:center;gap:8px;margin-bottom:1rem}
            .lang-btn{padding:6px 16px;border-radius:20px;border:1px solid #E2E8F0;background:white;font-weight:700;font-size:13px;cursor:pointer;color:#64748B}
            .lang-btn.active{background:#991B1B;color:white;border-color:#991B1B}
            .mic-btn-wrapper{margin:1.5rem auto 1rem;width:120px}
            .mic-nav-btn{width:120px;height:120px;border-radius:50%;background:#991B1B;border:none;color:white;font-size:48px;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 6px 20px rgba(153,27,27,0.5);margin:0 auto}
            .mic-nav-btn.recording{animation:pulse-red 1.5s infinite}
            @keyframes pulse-red{0%{box-shadow:0 0 0 0 rgba(153,27,27,0.8)}70%{box-shadow:0 0 0 35px rgba(153,27,27,0)}100%{box-shadow:0 0 0 0 rgba(153,27,27,0)}}
            .ask-me-label{color:#991B1B;font-weight:800;font-size:24px;margin-top:12px;display:block;letter-spacing:1px}
            .status-text{margin-top:10px;font-size:15px;color:#64748B;font-weight:500}
            .lang-badge{display:inline-block;margin-top:8px;padding:4px 10px;border-radius:12px;font-size:13px;font-weight:700;background:#F1F5F9;color:#475569}
            #map{height:350px;width:100%;border-radius:12px;border:1px solid #e0e0e0;margin:1.5rem 0;position:relative;z-index:1}
            .card{display:none;background:white;border:1px solid #E2E8F0;padding:1.5rem;border-radius:16px;text-align:left;margin-bottom:2rem}
            .badge{background:#EF4444;color:white;padding:4px 12px;border-radius:99px;font-weight:800;font-size:12px}
            .instruction-title{color:#475569;font-weight:700;font-size:14px;margin:1rem 0 0.5rem}
            .instruction-text{font-size:18px;font-weight:700;color:#1E293B;line-height:1.4}
            .avoid-box{background:#FFF7ED;border:1px solid #FED7AA;padding:12px;border-radius:10px;margin:1rem 0}
            .avoid-title{color:#9A3412;font-weight:800;font-size:13px;margin-bottom:4px}
            .avoid-text{color:#C2410C;font-weight:600;font-size:14px}
            .dist-text{color:#94A3B8;font-size:13px;font-weight:600;text-align:right}
            .speaker-btn{background:#F1F5F9;border:none;border-radius:50%;width:44px;height:44px;cursor:pointer;font-size:22px}
        </style>
        <div class="nav-container">
            <div class="lang-toggle">
                <button id="btn-en" class="lang-btn" onclick="setLang('en')">EN</button>
                <button id="btn-hi" class="lang-btn" onclick="setLang('hi')">HI</button>
                <button id="btn-auto" class="lang-btn active" onclick="setLang('auto')">AUTO</button>
            </div>
            <div class="mic-btn-wrapper">
                <button id="nav-mic-btn" class="mic-nav-btn">🎤</button>
                <span class="ask-me-label">ASK ME</span>
            </div>
            <div id="nav-status" class="status-text">Tap to speak your emergency</div>
            <div id="detected-lang-badge" class="lang-badge" style="display:none"></div>
            <div id="map"></div>
            <div id="instruction-card" class="card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span id="card-disaster" class="badge">EMERGENCY</span>
                    <button class="speaker-btn" onclick="replaySpeech()">🔊</button>
                </div>
                <div class="instruction-title">INSTRUCTION:</div>
                <div id="card-instruction" class="instruction-text">...</div>
                <div class="avoid-box">
                    <div class="avoid-title">⚠️ AVOID:</div>
                    <div id="card-avoid" class="avoid-text">...</div>
                </div>
                <div id="card-distance" class="dist-text"></div>
            </div>
        </div>
        <script>
            var map=null,userMarker=null,safeMarkers=[],routeLine=null;
            var userLat=28.6600,userLng=77.2300;
            var lastInstruction='',detectedLang='english';
            var currentLangMode='auto',recognition,recording=false;

            function setLang(m){
                currentLangMode=m;
                document.querySelectorAll('.lang-btn').forEach(function(b){b.classList.remove('active')});
                document.getElementById('btn-'+m).classList.add('active');
                if(recognition){
                    if(m==='hi') recognition.lang='hi-IN';
                    else if(m==='en') recognition.lang='en-IN';
                    else recognition.lang='';
                }
            }

            function detectLang(t){
                var hindiChars=/[ऀ-ॿ]/;
                if(hindiChars.test(t)) return 'hindi';
                var hw=['hai','mera','meri','ghar','paani','aag','madad','karo','nahi','haan','kahan','jao','aa','gaya','raha','ka','ki','ke'];
                var c=t.toLowerCase().split(' ').filter(function(w){return hw.indexOf(w)>-1}).length;
                if(c>=2) return 'hinglish';
                return 'english';
            }

            function speak(text){
                if('speechSynthesis' in window){
                    window.speechSynthesis.cancel();
                    var s=new SpeechSynthesisUtterance();
                    s.text=text; s.rate=0.85; s.volume=1;
                    s.lang=(detectedLang==='hindi'||detectedLang==='hinglish')?'hi-IN':'en-IN';
                    window.speechSynthesis.speak(s);
                }
            }

            function replaySpeech(){if(lastInstruction) speak(lastInstruction)}

            function waitForLeaflet(){
                if(typeof L!=='undefined') initMap();
                else setTimeout(waitForLeaflet,100);
            }

            function initMap(){
                if(map!==null){map.remove();map=null}
                map=L.map('map',{zoomControl:true,scrollWheelZoom:false}).setView([28.6600,77.2300],13);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
                    attribution:'© OpenStreetMap',
                    maxZoom:18
                }).addTo(map);
                
                // Force size recalculation multiple times because Streamlit iframes can resize after load
                setTimeout(function(){ map.invalidateSize(); }, 200);
                setTimeout(function(){ map.invalidateSize(); }, 800);
                setTimeout(function(){ map.invalidateSize(); }, 1500);

                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        function(pos){
                            userLat=pos.coords.latitude; userLng=pos.coords.longitude;
                            if(userMarker) map.removeLayer(userMarker);
                            userMarker=L.circleMarker([userLat,userLng],{radius:10,fillColor:'#378ADD',color:'#fff',weight:3,fillOpacity:1}).addTo(map).bindPopup('You are here');
                            map.setView([userLat,userLng],15);
                        },
                        function(){
                            L.circleMarker([28.6600,77.2300],{radius:10,fillColor:'#378ADD',color:'#fff',weight:3,fillOpacity:1}).addTo(map).bindPopup('Default: Delhi');
                        }
                    );
                } else {
                    L.circleMarker([28.6600,77.2300],{radius:10,fillColor:'#378ADD',color:'#fff',weight:3,fillOpacity:1}).addTo(map).bindPopup('Default: Delhi');
                }
            }

            function addSafeMarkers(uLat,uLng,places){
                safeMarkers.forEach(function(m){map.removeLayer(m)});
                safeMarkers=[];
                if(routeLine) map.removeLayer(routeLine);
                var offsets=[[0.008,0.006],[-0.007,0.010],[0.012,-0.005]];
                var positions=[];
                places.forEach(function(place,i){
                    if(i>2) return;
                    var lat=uLat+offsets[i][0],lng=uLng+offsets[i][1];
                    positions.push([lat,lng]);
                    var mk=L.circleMarker([lat,lng],{radius:10,fillColor:'#639922',color:'#fff',weight:3,fillOpacity:1}).addTo(map).bindPopup(place.trim());
                    safeMarkers.push(mk);
                });
                if(positions.length>0){
                    routeLine=L.polyline([[uLat,uLng],positions[0]],{color:'#378ADD',weight:3,dashArray:'8,8'}).addTo(map);
                    var bounds=L.latLngBounds([[uLat,uLng]].concat(positions));
                    map.fitBounds(bounds,{padding:[40,40]});
                }
            }

            async function callGemma(text){
                var status=document.getElementById('nav-status');
                status.innerText='Finding safe routes...';
                detectedLang=detectLang(text);
                var badge=document.getElementById('detected-lang-badge');
                var icons={hindi:'🇮🇳 Hindi',hinglish:'🔤 Hinglish',english:'🇬🇧 English'};
                badge.innerText=icons[detectedLang]+' detected';
                badge.style.display='inline-block';
                try{
                    var res=await fetch('http://localhost:11434/api/generate',{
                        method:'POST',
                        headers:{'Content-Type':'application/json'},
                        body:JSON.stringify({
                            model:'gemma4:e4b',
                            prompt:`You are emergency AI. Victim said: "${text}". Detected language: ${detectedLang}. Reply SAME language as victim. STRICT FORMAT ONLY:\nDISASTER: [type]\nSAFE PLACES: [p1], [p2], [p3]\nINSTRUCTION: [one sentence]\nAVOID: [one sentence]`,
                            stream:false
                        })
                    });
                    var data=await res.json();
                    parseAndDisplay(data.response);
                    status.innerText='Safe route found ✅';
                }catch(e){
                    status.innerText='AI offline. Check Ollama.';
                }
            }

            function parseAndDisplay(raw){
                var lines=raw.split(/\\r?\\n/);
                var p={};
                lines.forEach(function(line){
                    var idx=line.indexOf(':');
                    if(idx>-1){
                        var k=line.substring(0,idx).trim().toUpperCase();
                        var v=line.substring(idx+1).trim();
                        p[k]=v;
                    }
                });
                var disaster=p['DISASTER']||'Emergency';
                var places=(p['SAFE PLACES']||'School,Camp,Police').split(',');
                var instruction=p['INSTRUCTION']||'Move to nearest safe area';
                var avoid=p['AVOID']||'Avoid dangerous zones';
                addSafeMarkers(userLat,userLng,places);
                document.getElementById('card-disaster').innerText=disaster;
                document.getElementById('card-instruction').innerText=instruction;
                document.getElementById('card-avoid').innerText=avoid;
                document.getElementById('instruction-card').style.display='block';
                var dlat=(userLat+0.008-userLat)*111000;
                var dlng=(userLng+0.006-userLng)*111000;
                var dist=Math.round(Math.sqrt(dlat*dlat+dlng*dlng));
                document.getElementById('card-distance').innerText=(dist>1000?(dist/1000).toFixed(1)+'km':dist+'m')+' away';
                lastInstruction=instruction;
                speak(instruction);
            }

            var btn=document.getElementById('nav-mic-btn');
            var status=document.getElementById('nav-status');

            if('webkitSpeechRecognition' in window||'SpeechRecognition' in window){
                var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
                recognition=new SR();
                recognition.continuous=false;
                recognition.interimResults=true;
                recognition.lang='';
                recognition.onstart=function(){recording=true;btn.classList.add('recording');status.innerText='Listening...'};
                recognition.onend=function(){recording=false;btn.classList.remove('recording')};
                recognition.onerror=function(e){status.innerText='Mic error: '+e.error+'. Allow mic access.';recording=false;btn.classList.remove('recording')};
                recognition.onresult=function(e){
                    var final='',interim='';
                    for(var i=e.resultIndex;i<e.results.length;i++){
                        if(e.results[i].isFinal) final+=e.results[i][0].transcript;
                        else interim+=e.results[i][0].transcript;
                    }
                    if(final){status.innerText=final;callGemma(final)}
                    else status.innerText=interim;
                };
                btn.onclick=function(){if(!recording) recognition.start(); else recognition.stop()};
            } else {
                status.innerText='Speech not supported. Use Chrome.';
            }

            waitForLeaflet();
        </script>
        </body>
        </html>
        """
        st.components.v1.html(nav_html_template, height=1000)
    #  MAIN AREA: Write-up box (Full Width)
    # ============================================================
    if st.session_state.active_panel is None:
        st.markdown("---")
        st.write("### 📝 Report an Incident")
        
        # Severity Selector (New Triage Options)
        incident_severity = st.selectbox(
            "Select Incident Severity",
            ["Normal", "Serious", "Critical"],
            index=0
        )
        
        # Voice mic
        mic_html_template = """
        <div style="display:flex;align-items:center;gap:12px;margin:10px 0;padding:12px;background:{card_bg};border-radius:10px;border:1px solid {border_color};">
            <button id="mic-btn" style="border:none;background:{primary_btn};color:#fff;border-radius:50%;width:42px;height:42px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:18px;">🎤</button>
            <span id="status-text" style="font-size:0.9rem;color:red;font-weight:500;">Ask me..</span>
        </div>
        <script>
            const btn=document.getElementById('mic-btn'), status=document.getElementById('status-text');
            let rec=false;
            if('webkitSpeechRecognition' in window){
                const r=new webkitSpeechRecognition();
                r.continuous=true;
                r.onresult=(e)=>{
                    let t='';
                    for(let i=e.resultIndex; i<e.results.length; ++i){
                        t += e.results[i][0].transcript;
                    }
                    if(t) status.innerText="Captured: "+t;
                };
                btn.onclick=()=>{
                    if(!rec){
                        r.start();
                        btn.style.background='#EF4444';
                        status.innerText="Listening...";
                        rec=true;
                    } else {
                        r.stop();
                        btn.style.background='{primary_btn}';
                        rec=false;
                    }
                };
            } else {
                status.innerText="Speech API not supported";
                btn.disabled=true;
            }
        </script>
        """
        mic_html = mic_html_template.replace("{card_bg}", card_bg).replace("{border_color}", border_color).replace("{primary_btn}", primary_btn)
        st.components.v1.html(mic_html, height=80)

        symptoms = st.text_area(
            "Emergency Description",
            placeholder=f"Describe the {incident_severity} incident here...",
            height=140,
            key="emergency_desc",
            label_visibility="collapsed"
        )
        
        # Store for context
        st.session_state.incident_severity = incident_severity

        uploaded_image = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded_image:
            st.session_state.persisted_image = uploaded_image
        analyze_btn = st.button("🚀 Get AI Response Plan", type="primary", use_container_width=True)

        # --- SUBMIT LOGIC ---
        if analyze_btn:
            if not st.session_state.emergency_desc.strip():
                st.warning("⚠ Please describe the emergency before submitting.")
            else:
                # Update Medical Stats
                sev_map = {"Critical": "Critical", "Serious": "Serious", "Normal": "Minor"}
                stat_key = sev_map.get(incident_severity, "Minor")
                st.session_state.medical_stats[stat_key] += 1
                st.session_state.medical_stats["Total"] += 1
                
                st.session_state.analyzed = True
                st.session_state.persisted_desc = st.session_state.emergency_desc
                st.session_state.last_result = None
                st.rerun()

    # End of landing page


# ============================================================
#  RESULTS PAGE
# ============================================================
if st.session_state.analyzed and st.session_state.get('persisted_desc', '').strip():
    # Fetch result once
    if 'last_result' not in st.session_state or st.session_state.last_result is None:
        with st.spinner("🔄 AI agents are analyzing the situation…"):
            files = {}
            uploaded_image = st.session_state.get('persisted_image')
            if uploaded_image:
                files["image"] = (uploaded_image.name, uploaded_image.getvalue(), uploaded_image.type)
            try:
                # Prefix the severity so the AI knows the triage level
                full_context = f"SEVERITY LEVEL: {st.session_state.get('incident_severity', 'Normal')}\n\nDESCRIPTION: {st.session_state.persisted_desc}"
                r = requests.post(f"https://disaster-response-system-ppci.onrender.com/disaster-ai", json={"query": full_context}, timeout=150)
                if r.status_code == 200:
                    st.session_state.last_result = r.json()
                    if not st.session_state.last_result:
                        st.error("🚨 AI returned an empty response. This can happen if the model is overloaded.")
                else:
                    detail = ""
                    try: detail = f" - {r.json().get('detail', '')}"
                    except: pass
                    st.error(f"🚨 Server Error: {r.status_code}{detail}")
                    st.session_state.analyzed = False 
            except requests.exceptions.Timeout:
                st.error("⌛ Request Timed Out. The AI agent is taking too long. Please check Ollama and try again.")
                st.session_state.analyzed = False
            except Exception as e:
                st.error(f"❌ Connection error: {e}")
                st.session_state.analyzed = False

    if st.session_state.get('last_result'):
        res = st.session_state.last_result

        # Severity parsing
        severity = res.get("severity", "Minor").upper()
        badge_class = f"badge-{severity.lower()}"

        # Build report from structured API response
        actions = "\n".join([f"- {a}" for a in res.get("immediate_actions", [])])
        contacts = "\n".join([f"- {k}: {v}" for k, v in res.get("resources_contacts", {}).items()])
        evac = "\n".join([f"- {s}" for s in res.get("evacuation_steps", [])])
        tips = "\n".join([f"- {t}" for t in res.get("survival_tips", [])])
        report_text = f"**Disaster Type:** {res.get('disaster_type', '').title()}\n**Severity:** {res.get('severity', '')}\n\n**Immediate Actions:**\n{actions}\n\n**Emergency Contacts:**\n{contacts}\n\n**Evacuation Steps:**\n{evac}\n\n**Survival Tips:**\n{tips}\n\n**Summary:** {res.get('summary', '')}"

        st.markdown('<div class="analysis-header">✅ INCIDENT ANALYSIS COMPLETE</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="badge {badge_class}">{severity} SEVERITY</div>', unsafe_allow_html=True)

        if st.button("🔊 Read Report Aloud"):
            # Comprehensive cleanup for TTS
            clean = report_text.replace('"', "'").replace('\n', ' ')
            for char in ['#', '*', '_', '>', '`', '[', ']']:
                clean = clean.replace(char, '')
            
            st.components.v1.html(
                f'<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance("{clean.strip()}"));</script>',
                height=0
            )

        st.write("### 📋 Executive Summary")
        st.write(report_text)

        st.write("### 📞 Emergency Contacts")
        contacts_data = res.get("resources_contacts", {})
        if contacts_data:
            for name, number in contacts_data.items():
                st.markdown(f"**{name}:** {number}")
        else:
            st.markdown("**Police:** 112\n\n**Ambulance:** 108\n\n**Fire:** 101\n\n**Disaster:** 1078")

        st.divider()
        if st.button("🔄 Start New Report", use_container_width=True, type="primary"):
            st.session_state.analyzed = False
            st.session_state.last_result = None
            st.session_state.active_panel = None
            st.session_state.persisted_image = None
            st.session_state.persisted_desc = None
            st.rerun()