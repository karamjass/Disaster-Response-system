"""
DisasterAI Chat Interface — standalone Streamlit page.
Run alongside streamlit_app.py or as the main entry point.
"""

import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import json

API_URL = "http://127.0.0.1:8000/disaster-ai"

st.set_page_config(
    page_title="DisasterAI — India Emergency Assistant",
    page_icon="🆘",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("chat_history", []),
    ("last_result", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp { background: #0D1117 !important; }

.hero {
    text-align: center;
    padding: 2rem 1rem 1.2rem;
}
.hero h1 {
    font-size: 2.8rem;
    font-weight: 800;
    color: #F8FAFC;
    margin-bottom: 0.3rem;
}
.hero h1 span { color: #EF4444; }
.hero p { color: #94A3B8; font-size: 1.05rem; }

.severity-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 99px;
    font-weight: 800;
    font-size: 0.8rem;
    letter-spacing: 1px;
    margin-bottom: 1rem;
}
.sev-Critical { background:#EF4444; color:white; }
.sev-High     { background:#F97316; color:white; }
.sev-Medium   { background:#EAB308; color:#0D1117; }
.sev-Low      { background:#22C55E; color:white; }

.section-card {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.section-card h4 {
    margin: 0 0 0.7rem 0;
    font-size: 0.95rem;
    font-weight: 700;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.action-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 6px 0;
    color: #E2E8F0;
    font-size: 0.93rem;
    border-bottom: 1px solid #21262D;
}
.action-item:last-child { border-bottom: none; }
.action-num {
    background: #EF4444;
    color: white;
    border-radius: 50%;
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 800;
    flex-shrink: 0;
    margin-top: 1px;
}
.contact-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #21262D;
    color: #E2E8F0;
    font-size: 0.9rem;
}
.contact-row:last-child { border-bottom: none; }
.contact-num {
    font-weight: 800;
    font-size: 1.1rem;
    color: #38BDF8;
    font-family: monospace;
}
.summary-box {
    background: #0F2A1A;
    border-left: 4px solid #22C55E;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    color: #BBF7D0;
    font-size: 0.95rem;
    line-height: 1.6;
    margin-bottom: 1rem;
}
.disaster-type-tag {
    display: inline-block;
    background: #1E3A5F;
    color: #93C5FD;
    padding: 3px 12px;
    border-radius: 99px;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.8rem;
}
.input-container {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 16px;
    padding: 1.5rem;
    margin-top: 1rem;
}
div.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    transition: all 0.2s !important;
}
div.stButton > button[kind="primary"] {
    background: #EF4444 !important;
    border: none !important;
    color: white !important;
}
div.stButton > button[kind="primary"]:hover {
    background: #DC2626 !important;
    transform: translateY(-1px) !important;
}
[data-baseweb="textarea"] textarea {
    background: #0D1117 !important;
    color: #E2E8F0 !important;
    border: 1px solid #30363D !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}
.json-toggle {
    font-size: 0.8rem;
    color: #64748B;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🆘 Disaster<span>AI</span></h1>
    <p>Intelligent disaster response for India — calm, clear, actionable.</p>
</div>
""", unsafe_allow_html=True)

# ── Quick Scenario Buttons ────────────────────────────────────────────────────
st.markdown("**Quick Scenarios:**")
scenarios = {
    "🌊 Flood": "There is severe flooding in my area in Mumbai. Water has entered homes and roads are submerged.",
    "🏚 Earthquake": "An earthquake just struck near Delhi. Buildings are shaking and there are collapsed structures.",
    "🔥 Fire": "A fire has broken out in a building in Chennai. Multiple floors are on fire and people are trapped.",
    "🌀 Cyclone": "A cyclone is approaching coastal Odisha. High winds and storm surge expected.",
    "🧪 Gas Leak": "There is a gas leak at an industrial plant near Bhopal. Toxic fumes spreading.",
}
cols = st.columns(len(scenarios))
for col, (label, query) in zip(cols, scenarios.items()):
    with col:
        if st.button(label, use_container_width=True, key=f"quick_{label}"):
            st.session_state["prefill_query"] = query

# ── Input Area ────────────────────────────────────────────────────────────────
st.markdown('<div class="input-container">', unsafe_allow_html=True)
prefill = st.session_state.pop("prefill_query", "")
user_query = st.text_area(
    "Describe the emergency situation:",
    value=prefill,
    placeholder="e.g. 'There is a flood in my area in Patna, Bihar. Water level is rising fast and people are trapped on rooftops...'",
    height=110,
    key="user_query_input",
    label_visibility="collapsed",
)

col_btn1, col_btn2, col_btn3 = st.columns([3, 1, 1])
with col_btn1:
    analyze_btn = st.button("🚨 Get Disaster Response", type="primary", use_container_width=True)
with col_btn2:
    json_btn = st.button("📋 Export JSON", use_container_width=True)
with col_btn3:
    clear_btn = st.button("🔄 Clear", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if clear_btn:
    st.session_state.last_result = None
    st.rerun()

# ── API Call ──────────────────────────────────────────────────────────────────
if analyze_btn and user_query.strip():
    with st.spinner("🔍 Analyzing disaster situation..."):
        try:
            resp = requests.post(API_URL, json={"query": user_query}, timeout=120)
            if resp.status_code == 200:
                st.session_state.last_result = resp.json()
                st.session_state.chat_history.append({
                    "query": user_query,
                    "result": st.session_state.last_result,
                })
            else:
                st.error(f"API Error {resp.status_code}: {resp.text[:200]}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")
        except requests.exceptions.Timeout:
            st.error("⏱ Request timed out. The model may be slow — try again.")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

elif analyze_btn:
    st.warning("⚠️ Please describe the emergency situation first.")

# ── Export JSON ───────────────────────────────────────────────────────────────
if json_btn and st.session_state.last_result:
    st.download_button(
        "⬇️ Download JSON",
        data=json.dumps(st.session_state.last_result, indent=2),
        file_name="disaster_ai_response.json",
        mime="application/json",
    )

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.last_result:
    res = st.session_state.last_result
    dtype    = res.get("disaster_type", "unknown").replace("_", " ").title()
    severity = res.get("severity", "Unknown")
    actions  = res.get("immediate_actions", [])
    evac     = res.get("evacuation_steps", [])
    contacts = res.get("resources_contacts", {})
    tips     = res.get("survival_tips", [])
    summary  = res.get("summary", "")
    map_data = res.get("map_data", {})
    ms       = res.get("map_suggestion", {})

    # Map data fields
    affected_area = map_data.get("affected_area", res.get("location_name", "India"))
    affected_lat  = map_data.get("affected_lat", ms.get("lat", 20.5937))
    affected_lon  = map_data.get("affected_lon", ms.get("lon", 78.9629))
    affected_gmap = map_data.get("affected_gmaps", f"https://maps.google.com/?q={affected_lat},{affected_lon}")
    safe_zone     = map_data.get("nearest_safe_zone", ms.get("description", "Nearest Relief Camp"))
    safe_lat      = map_data.get("safe_lat", affected_lat + 0.01)
    safe_lon      = map_data.get("safe_lon", affected_lon + 0.01)
    safe_gmap     = map_data.get("safe_gmaps", f"https://maps.google.com/?q={safe_lat},{safe_lon}")
    evac_dir      = map_data.get("evacuation_direction", "Follow official evacuation signs")

    st.markdown("---")

    # ── Header Row ────────────────────────────────────────────────────────────
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f'<div class="disaster-type-tag">🏷 {dtype}</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="severity-badge sev-{severity}">⚡ {severity.upper()} SEVERITY</span>', unsafe_allow_html=True)
    with c2:
        if summary:
            st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

    # ── Main Panels ───────────────────────────────────────────────────────────
    left, right = st.columns([3, 2])

    with left:
        # Immediate Actions
        if actions:
            st.markdown('<div class="section-card"><h4>⚡ Immediate Actions</h4>', unsafe_allow_html=True)
            for i, action in enumerate(actions, 1):
                st.markdown(
                    f'<div class="action-item"><div class="action-num">{i}</div><div>{action}</div></div>',
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Evacuation Steps
        if evac:
            st.markdown('<div class="section-card"><h4>🚶 Evacuation Steps</h4>', unsafe_allow_html=True)
            for i, step in enumerate(evac, 1):
                st.markdown(
                    f'<div class="action-item"><div class="action-num" style="background:#F97316">{i}</div><div>{step}</div></div>',
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Survival Tips
        if tips:
            st.markdown('<div class="section-card"><h4>💡 Survival Tips</h4>', unsafe_allow_html=True)
            for tip in tips:
                st.markdown(f'<div class="action-item">💡 &nbsp;{tip}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with right:
        # Emergency Contacts
        if contacts:
            st.markdown('<div class="section-card"><h4>📞 Emergency Contacts (India)</h4>', unsafe_allow_html=True)
            for service, number in contacts.items():
                st.markdown(
                    f'<div class="contact-row"><span>{service}</span><span class="contact-num">{number}</span></div>',
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)



        # ── Folium Map with dual markers ─────────────────────────────────────
        st.markdown('<div class="section-card"><h4>🗺️ Evacuation Map</h4>', unsafe_allow_html=True)
        sev_colors = {"Critical":"red","High":"orange","Medium":"beige","Low":"green"}
        sev_hex    = {"Critical":"#EF4444","High":"#F97316","Medium":"#EAB308","Low":"#22C55E"}

        m = folium.Map(
            location=[(affected_lat + safe_lat)/2, (affected_lon + safe_lon)/2],
            zoom_start=13,
            tiles="CartoDB dark_matter",
        )
        # Affected area marker (red)
        folium.Marker(
            [affected_lat, affected_lon],
            popup=f"<b>⚠️ AFFECTED: {affected_area}</b><br>{dtype}<br>Severity: {severity}",
            tooltip=f"Affected: {affected_area}",
            icon=folium.Icon(color=sev_colors.get(severity, "red"), icon="warning-sign"),
        ).add_to(m)
        folium.Circle(
            [affected_lat, affected_lon], radius=1500,
            color=sev_hex.get(severity, "#EF4444"),
            fill=True, fill_opacity=0.2,
        ).add_to(m)
        # Safe zone marker (green)
        folium.Marker(
            [safe_lat, safe_lon],
            popup=f"<b>🟢 SAFE ZONE: {safe_zone}</b>",
            tooltip=f"Safe: {safe_zone}",
            icon=folium.Icon(color="green", icon="ok-sign"),
        ).add_to(m)
        folium.Circle(
            [safe_lat, safe_lon], radius=800,
            color="#22C55E", fill=True, fill_opacity=0.15,
        ).add_to(m)
        # Evacuation route line (dashed)
        folium.PolyLine(
            [[affected_lat, affected_lon], [safe_lat, safe_lon]],
            color="#38BDF8", weight=3, dash_array="10,8",
            popup="Evacuation Route",
        ).add_to(m)
        st_folium(m, width=None, height=320, key="disaster_map")
        st.markdown("</div>", unsafe_allow_html=True)



# ── Sidebar: Quick Contacts ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🆘 India Emergency Numbers")
    contacts_sidebar = {
        "🛡 Police": "112",
        "🩺 Ambulance": "108",
        "🔥 Fire": "101",
        "⚠️ Disaster": "1078",
        "🌊 NDRF": "011-24363260",
        "🚢 Coast Guard": "1554",
        "👩 Women": "1091",
        "👶 Child": "1098",
        "🚂 Railway": "1072",
        "💨 Gas Leak": "1906",
    }
    for name, num in contacts_sidebar.items():
        st.markdown(f"**{name}** &nbsp;&nbsp; `{num}`")

    st.divider()
    st.caption("DisasterAI v2.1 · Powered by Gemma via Ollama")
    st.caption("India-specific emergency response system")

