from backend.gemma_client import GemmaClient
from config import GROQ_API_KEY
gemma = GemmaClient(api_key=GROQ_API_KEY)

async def medical_triage(symptoms):
    prompt = f"Emergency Medical Analysis. Symptoms: {symptoms}. List injuries and first aid. Max 50 words."
    return await gemma.generate(prompt)