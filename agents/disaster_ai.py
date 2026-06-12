"""
DisasterAI Core Agent
Identifies disaster type, severity, immediate actions, India-specific emergency
contacts, evacuation guidance, and produces structured JSON output.
"""

import json
import re
from backend.gemma_client import GemmaClient
from config import GROQ_API_KEY

gemma = GemmaClient(api_key=GROQ_API_KEY)

# ── India Emergency Contacts ──────────────────────────────────────────────────
INDIA_CONTACTS = {
    "Police":            "112",
    "Ambulance":         "108",
    "Fire":              "101",
    "Disaster Helpline": "1078",
    "NDRF":              "011-24363260",
    "Coast Guard":       "1554",
    "Women Helpline":    "1091",
    "Child Helpline":    "1098",
    "Railway Accident":  "1072",
    "Gas Leak":          "1906",
}

# ── Disaster keyword → type map ───────────────────────────────────────────────
DISASTER_KEYWORDS = {
    "flood":       ["flood", "flooding", "inundation", "water level", "overflowing", "submerged", "baadhh", "paani"],
    "earthquake":  ["earthquake", "quake", "tremor", "seismic", "bhukamp", "shaking ground"],
    "fire":        ["fire", "blaze", "burning", "smoke", "aag", "inferno", "wildfire", "forest fire"],
    "cyclone":     ["cyclone", "hurricane", "typhoon", "storm", "toofan", "windstorm", "superstorm"],
    "landslide":   ["landslide", "mudslide", "debris flow", "bhookhalan", "rockfall"],
    "tsunami":     ["tsunami", "tidal wave", "seawave"],
    "chemical":    ["chemical", "gas leak", "toxic", "hazmat", "leak", "spill", "explosion", "blast"],
    "building_collapse": ["collapse", "building fell", "structure", "debris", "trapped", "rubble"],
    "drought":     ["drought", "water shortage", "no water", "sukha", "famine"],
    "heatwave":    ["heatwave", "heat stroke", "extreme heat", "sunstroke", "loo"],
    "accident":    ["accident", "crash", "collision", "vehicle", "road", "highway", "train"],
    "medical":     ["heart attack", "unconscious", "bleeding", "fracture", "burn", "poison", "snake bite"],
}

# ── Known location → lat/lon + safe zone map ────────────────────────────────
# Each entry: (lat, lon, safe_zone_name, safe_lat, safe_lon, evac_direction)
LOCATION_DATA = {
    "delhi":      {"lat":28.6139,"lon":77.2090,"safe_zone":"Jawaharlal Nehru Stadium Grounds","safe_lat":28.5810,"safe_lon":77.2370,"evac_dir":"South towards AIIMS flyover"},
    "mumbai":     {"lat":19.0760,"lon":72.8777,"safe_zone":"Azad Maidan Relief Camp","safe_lat":18.9388,"safe_lon":72.8354,"evac_dir":"North-East towards Western Express Highway"},
    "chennai":    {"lat":13.0827,"lon":80.2707,"safe_zone":"Nehru Indoor Stadium Shelter","safe_lat":13.0604,"safe_lon":80.2824,"evac_dir":"South towards Adyar bridge"},
    "kolkata":    {"lat":22.5726,"lon":88.3639,"safe_zone":"Salt Lake Stadium Relief Centre","safe_lat":22.5716,"safe_lon":88.4102,"evac_dir":"East towards Salt Lake Sector V"},
    "bangalore":  {"lat":12.9716,"lon":77.5946,"safe_zone":"Kanteerava Stadium Shelter","safe_lat":12.9752,"safe_lon":77.5929,"evac_dir":"North towards Cubbon Park"},
    "hyderabad":  {"lat":17.3850,"lon":78.4867,"safe_zone":"LB Stadium Relief Point","safe_lat":17.3884,"safe_lon":78.4748,"evac_dir":"West towards Necklace Road"},
    "pune":       {"lat":18.5204,"lon":73.8567,"safe_zone":"Shivaji Park Open Ground","safe_lat":18.5308,"safe_lon":73.8474,"evac_dir":"North towards University Road"},
    "ahmedabad":  {"lat":23.0225,"lon":72.5714,"safe_zone":"Sardar Patel Stadium Area","safe_lat":23.0062,"safe_lon":72.5713,"evac_dir":"South towards Sabarmati Riverfront"},
    "jaipur":     {"lat":26.9124,"lon":75.7873,"safe_zone":"SMS Stadium Relief Camp","safe_lat":26.8965,"safe_lon":75.8033,"evac_dir":"South-East towards Tonk Road"},
    "bhopal":     {"lat":23.2599,"lon":77.4126,"safe_zone":"Lal Parade Ground Shelter","safe_lat":23.2689,"safe_lon":77.4115,"evac_dir":"North away from Union Carbide area"},
    "lucknow":    {"lat":26.8467,"lon":80.9462,"safe_zone":"KD Singh Babu Stadium","safe_lat":26.8521,"safe_lon":80.9379,"evac_dir":"West towards Hazratganj"},
    "patna":      {"lat":25.5941,"lon":85.1376,"safe_zone":"Gandhi Maidan Relief Camp","safe_lat":25.6093,"safe_lon":85.1348,"evac_dir":"North towards elevated Gandhi Maidan"},
    "bhubaneswar":{"lat":20.2961,"lon":85.8245,"safe_zone":"Kalinga Stadium Cyclone Shelter","safe_lat":20.2891,"safe_lon":85.8186,"evac_dir":"South-West towards Kalinga Stadium"},
    "guwahati":   {"lat":26.1445,"lon":91.7362,"safe_zone":"Nehru Stadium Relief Centre","safe_lat":26.1697,"safe_lon":91.7586,"evac_dir":"North-East towards higher ground"},
    "chandigarh": {"lat":30.7333,"lon":76.7794,"safe_zone":"Sector 16 Cricket Stadium","safe_lat":30.7424,"safe_lon":76.7836,"evac_dir":"North towards Sector 16"},
    "srinagar":   {"lat":34.0837,"lon":74.7973,"safe_zone":"Bakshi Stadium Shelter","safe_lat":34.0844,"safe_lon":74.7983,"evac_dir":"East towards higher Zabarwan foothills"},
}

# Backward-compat: simple coord lookup
LOCATION_COORDS = {k: (v["lat"], v["lon"]) for k, v in LOCATION_DATA.items()}

DEFAULT_COORDS = (20.5937, 78.9629)  # Centre of India
DEFAULT_SAFE = {"safe_zone": "Nearest Government Relief Camp", "safe_lat": 20.60, "safe_lon": 78.97, "evac_dir": "Follow official evacuation signs to nearest relief camp"}


def _gmaps_url(lat: float, lon: float) -> str:
    """Generate a Google Maps link for given coordinates."""
    return f"https://maps.google.com/?q={lat},{lon}"


def detect_disaster_type(text: str) -> str:
    """Return the most likely disaster type from the user's input text."""
    text_lower = text.lower()
    scores = {dtype: 0 for dtype in DISASTER_KEYWORDS}
    for dtype, keywords in DISASTER_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[dtype] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"


def detect_location(text: str):
    """Extract lat/lon and safe zone data from text based on known India cities."""
    text_lower = text.lower()
    for city, data in LOCATION_DATA.items():
        if city in text_lower:
            return (data["lat"], data["lon"]), city.title(), data
    return DEFAULT_COORDS, "India (approximate)", DEFAULT_SAFE


def severity_from_type(disaster_type: str, text: str) -> str:
    """Heuristic severity estimation."""
    text_lower = text.lower()
    critical_words = ["death", "died", "dead", "critical", "trapped", "collapse", "sinking", "explosion", "mass casualty"]
    high_words = ["injured", "hurt", "fire", "flood", "cyclone", "emergency", "help", "urgent"]
    if any(w in text_lower for w in critical_words):
        return "Critical"
    if disaster_type in ("earthquake", "tsunami", "chemical", "building_collapse", "cyclone"):
        return "High"
    if any(w in text_lower for w in high_words):
        return "High"
    if disaster_type in ("flood", "fire", "landslide"):
        return "Medium"
    return "Low"


def get_relevant_contacts(disaster_type: str) -> dict:
    """Return a subset of India contacts relevant to the disaster."""
    base = {"Police": INDIA_CONTACTS["Police"],
            "Ambulance": INDIA_CONTACTS["Ambulance"],
            "Disaster Helpline": INDIA_CONTACTS["Disaster Helpline"],
            "NDRF": INDIA_CONTACTS["NDRF"]}
    extras = {
        "fire":             {"Fire Brigade": INDIA_CONTACTS["Fire"]},
        "chemical":         {"Fire Brigade": INDIA_CONTACTS["Fire"], "Gas Leak": INDIA_CONTACTS["Gas Leak"]},
        "flood":            {"Coast Guard": INDIA_CONTACTS["Coast Guard"]},
        "tsunami":          {"Coast Guard": INDIA_CONTACTS["Coast Guard"]},
        "accident":         {"Railway Accident": INDIA_CONTACTS["Railway Accident"]},
        "building_collapse":{"NDRF HQ": INDIA_CONTACTS["NDRF"]},
    }
    base.update(extras.get(disaster_type, {}))
    return base


SYSTEM_PROMPT = """You are DisasterAI for India. Reply ONLY in valid JSON, no markdown.

Schema:
{
  "disaster_type": "flood|earthquake|fire|cyclone|landslide|tsunami|chemical|building_collapse|heatwave|accident|medical|unknown",
  "severity": "Low|Medium|High|Critical",
  "immediate_actions": ["<5 short steps>"],
  "evacuation_steps": ["<3 steps>"],
  "resources_contacts": {"Police":"112","Ambulance":"108","Fire":"101","Disaster":"1078"},
  "survival_tips": ["<2 tips>"],
  "summary": "<2 sentences>"
}

Rules: calm tone, life first, India contacts only, keep everything brief.
"""


async def analyze_disaster(user_input: str) -> dict:
    """
    Full DisasterAI pipeline:
    1. Pre-process: detect type, location, severity from keywords.
    2. Call LLM for structured JSON response.
    3. Merge/validate the result.
    4. Build rich map_data with Google Maps links.
    Returns a fully structured dict.
    """
    detected_type = detect_disaster_type(user_input)
    coords, location_name, loc_data = detect_location(user_input)
    heuristic_severity = severity_from_type(detected_type, user_input)
    relevant_contacts = get_relevant_contacts(detected_type)

    prompt = f"""{SYSTEM_PROMPT}

Context (pre-analyzed):
- Detected disaster type: {detected_type}
- Estimated severity: {heuristic_severity}
- Detected location in India: {location_name} (lat={coords[0]}, lon={coords[1]})
- Known India emergency contacts: {json.dumps(relevant_contacts)}

User Input:
\"\"\"{user_input}\"\"\"

Respond with JSON only."""

    raw = await gemma.generate(prompt)

    # Try to parse JSON from LLM response
    parsed = _extract_json(raw)

    if not parsed:
        # Fallback: build structured response from heuristics
        parsed = _fallback_response(detected_type, heuristic_severity, coords, location_name, relevant_contacts, user_input)

    # Always merge relevant contacts
    if "resources_contacts" in parsed:
        parsed["resources_contacts"].update(relevant_contacts)
    else:
        parsed["resources_contacts"] = relevant_contacts

    # ── Build rich map_data ───────────────────────────────────────────────
    safe_zone  = loc_data.get("safe_zone", DEFAULT_SAFE["safe_zone"])
    safe_lat   = loc_data.get("safe_lat", DEFAULT_SAFE["safe_lat"])
    safe_lon   = loc_data.get("safe_lon", DEFAULT_SAFE["safe_lon"])
    evac_dir   = loc_data.get("evac_dir", DEFAULT_SAFE["evac_dir"])

    parsed["map_data"] = {
        "affected_area":      location_name,
        "affected_lat":       coords[0],
        "affected_lon":       coords[1],
        "affected_gmaps":     _gmaps_url(coords[0], coords[1]),
        "nearest_safe_zone":  safe_zone,
        "safe_lat":           safe_lat,
        "safe_lon":           safe_lon,
        "safe_gmaps":         _gmaps_url(safe_lat, safe_lon),
        "evacuation_direction": evac_dir,
    }

    # Keep legacy map_suggestion for backward compat
    parsed["map_suggestion"] = {
        "description": safe_zone,
        "lat": safe_lat,
        "lon": safe_lon,
    }

    # Store raw for debugging
    parsed["_raw_llm"] = raw
    parsed["_location_name"] = location_name

    return parsed


def _extract_json(text: str) -> dict | None:
    """Try to extract a JSON object from LLM text output."""
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?", "", text).strip()
    # Find first { ... } block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


def _fallback_response(dtype, severity, coords, location, contacts, user_input) -> dict:
    """Rule-based fallback when LLM JSON parsing fails."""
    actions_map = {
        "flood":       ["Move to higher ground immediately", "Do NOT walk through floodwater", "Turn off electricity at mains", "Contact NDRF: 011-24363260", "Listen to local radio/alerts"],
        "earthquake":  ["DROP, COVER, HOLD ON", "Move away from windows and heavy objects", "After shaking stops, exit carefully", "Check for gas leaks — do NOT use lighters", "Go to open ground away from buildings"],
        "fire":        ["Activate fire alarm immediately", "Crawl low under smoke", "Close doors to slow fire spread", "Evacuate via stairs — NEVER use lift", "Call Fire: 101"],
        "cyclone":     ["Move to a sturdy building immediately", "Stay away from windows and doors", "Store drinking water and food for 3 days", "Follow official evacuation orders", "Keep battery-powered radio for updates"],
        "landslide":   ["Move away from the slope immediately", "Do not re-enter affected area", "Watch for secondary slides", "Contact NDRF: 011-24363260"],
        "chemical":    ["Evacuate upwind immediately", "Cover nose/mouth with wet cloth", "Do NOT switch on lights (sparks)", "Call Gas Emergency: 1906", "Seal doors/windows if inside"],
        "building_collapse": ["Do NOT enter damaged structure", "Call for help using whistle/banging", "Conserve energy if trapped", "Signal rescuers with light or sound", "NDRF: 011-24363260"],
        "medical":     ["Call Ambulance: 108 immediately", "Do NOT move the patient unnecessarily", "Apply pressure to bleeding wounds", "Check airways — tilt head back gently", "Stay with the patient until help arrives"],
        "accident":    ["Call 108 for ambulance immediately", "Do NOT move seriously injured persons", "Secure the scene — turn on hazard lights", "Apply pressure to wounds", "Call Police: 112"],
        "unknown":     ["Call Emergency: 112", "Move to a safe location", "Stay calm and assess surroundings", "Contact local disaster helpline: 1078"],
    }
    evac_map = {
        "flood":    ["Follow designated flood evacuation route", "Proceed to nearest elevated shelter", "Avoid bridges over rivers"],
        "earthquake": ["Move to open ground", "Avoid coastal areas (tsunami risk)", "Follow civil defence routes"],
        "fire":     ["Use nearest fire exit", "Assemble at designated muster point", "Do not return to building until cleared"],
        "cyclone":  ["Move inland", "Go to cyclone shelter", "Follow official government evacuation route"],
        "default":  ["Follow official evacuation signs", "Move away from danger zone", "Report to nearest relief camp"],
    }
    return {
        "disaster_type": dtype,
        "severity": severity,
        "immediate_actions": actions_map.get(dtype, actions_map["unknown"]),
        "evacuation_steps": evac_map.get(dtype, evac_map["default"]),
        "resources_contacts": contacts,
        "survival_tips": [
            "Keep phone battery above 20% — use low-power mode",
            "Drink only bottled or boiled water",
            "Stay tuned to All India Radio for official updates",
            "Do not spread unverified information",
        ],
        "summary": f"A {dtype} situation has been detected with {severity} severity near {location}. "
                   f"Follow the immediate actions listed. Contact emergency services immediately."
    }
