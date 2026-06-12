from backend.gemma_client import GemmaClient
from config import GROQ_API_KEY
gemma = GemmaClient(api_key=GROQ_API_KEY)

async def generate_report(data):
    prompt = f"""DisasterAI Report format:
Disaster Type / Severity / Immediate Actions / Emergency Contacts / Evacuation Steps / Survival Tips / Summary
Data: {str(data)[:800]}"""
    return await gemma.generate(prompt)