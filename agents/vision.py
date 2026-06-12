import base64
from backend.gemma_client import GemmaClient
from config import GROQ_API_KEY
gemma = GemmaClient(api_key=GROQ_API_KEY)

async def analyze_disaster_image(image_path):
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")
    prompt = "Vision Intelligence. Analyze image for hazards, structural damage, and trapped persons. Max 50 words."
    return await gemma.generate(prompt, images=[image_b64])