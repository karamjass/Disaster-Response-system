from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from agents.orchestrator import orchestrate
from agents.disaster_ai import analyze_disaster
import os

app = FastAPI(title="DisasterAI API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── Original /analyze endpoint (kept for backward-compat) ────────────────────
class AnalysisResponse(BaseModel):
    medical: str
    logistics: Dict[str, Any]
    vision: Optional[str] = None
    report: str


@app.get("/")
def home():
    return {"message": "DisasterAI API Running", "version": "2.0"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    symptoms: str = Form(...),
    image: UploadFile = File(None)
):
    image_path = None
    try:
        if image:
            image_path = os.path.join(UPLOAD_DIR, image.filename)
            with open(image_path, "wb") as f:
                f.write(await image.read())

        result = await orchestrate(symptoms, image_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


# ── NEW: DisasterAI structured endpoint ─────────────────────────────────────
class MapSuggestion(BaseModel):
    description: str
    lat: float
    lon: float


class MapData(BaseModel):
    affected_area: str
    affected_lat: float
    affected_lon: float
    affected_gmaps: str
    nearest_safe_zone: str
    safe_lat: float
    safe_lon: float
    safe_gmaps: str
    evacuation_direction: str


class DisasterAIResponse(BaseModel):
    disaster_type: str
    severity: str
    immediate_actions: List[str]
    evacuation_steps: List[str]
    resources_contacts: Dict[str, str]
    map_suggestion: MapSuggestion
    map_data: MapData
    survival_tips: List[str]
    summary: str
    location_name: Optional[str] = None


class DisasterQuery(BaseModel):
    query: str


@app.post("/disaster-ai", response_model=DisasterAIResponse)
async def disaster_ai_endpoint(body: DisasterQuery):
    """
    DisasterAI endpoint: returns structured disaster response JSON
    with map data, Google Maps links, and evacuation directions.
    """
    try:
        result = await analyze_disaster(body.query)
        md = result.get("map_data", {})
        ms = result.get("map_suggestion", {})
        return DisasterAIResponse(
            disaster_type=result.get("disaster_type", "unknown"),
            severity=result.get("severity", "Unknown"),
            immediate_actions=result.get("immediate_actions", []),
            evacuation_steps=result.get("evacuation_steps", []),
            resources_contacts=result.get("resources_contacts", {}),
            map_suggestion=MapSuggestion(
                description=ms.get("description", "India"),
                lat=ms.get("lat", 20.5937),
                lon=ms.get("lon", 78.9629),
            ),
            map_data=MapData(
                affected_area=md.get("affected_area", "India"),
                affected_lat=md.get("affected_lat", 20.5937),
                affected_lon=md.get("affected_lon", 78.9629),
                affected_gmaps=md.get("affected_gmaps", "https://maps.google.com/?q=20.5937,78.9629"),
                nearest_safe_zone=md.get("nearest_safe_zone", "Nearest Relief Camp"),
                safe_lat=md.get("safe_lat", 20.60),
                safe_lon=md.get("safe_lon", 78.97),
                safe_gmaps=md.get("safe_gmaps", "https://maps.google.com/?q=20.60,78.97"),
                evacuation_direction=md.get("evacuation_direction", "Follow official signs"),
            ),
            survival_tips=result.get("survival_tips", []),
            summary=result.get("summary", ""),
            location_name=result.get("_location_name"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Utility: quick contacts endpoint ─────────────────────────────────────────
@app.get("/contacts")
def get_india_contacts():
    from agents.disaster_ai import INDIA_CONTACTS
    return {"india_emergency_contacts": INDIA_CONTACTS}