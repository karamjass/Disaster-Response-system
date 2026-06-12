# Disaster-Response-system
``` An offline-first AI disaster response system powered by Gemma 4 that helps  survivors get instant medical triage, emergency navigation, and safe route  guidance — even when internet and cell networks are completely down. ```

> AI-powered emergency response that works completely 
> offline — no internet, no cloud, no limits.

<img width="1279" height="649" alt="image" src="https://github.com/user-attachments/assets/7ac17c12-6e66-44b1-8ebe-c14486ee23ee" />

## 🎯 Problem
When disasters strike — floods, earthquakes, building 
collapses — internet and cell towers go down first. 
Existing emergency apps fail exactly when needed most.

## 💡 Solution
A fully offline AI system powered by Gemma 4 that gives 
survivors instant medical triage, emergency protocols, 
and safe place navigation — even with zero connectivity.

## ✨ Features
- 🎙️ Voice input — Hindi, English, Hinglish auto-detect
- 🩺 Medical Emergency — CPR, bleeding, burns, shock
- 🗺️ Safe Place Navigator — map + spoken directions
- 📞 Emergency Calls — Police 100, Ambulance 108
- 🤖 Gemma 4 AI — runs 100% on-device via Ollama

## 🛠️ Tech Stack
| Component | Technology |
|---|---|
| AI Model | Gemma 4 via Ollama |
| Frontend | Streamlit |
| Backend | FastAPI |
| Maps | Leaflet.js + OpenStreetMap |
| Voice | Web Speech Recognition API |
| Built with | Antigravity (Google AI agent) |

## 🚀 Setup

**Step 1 — Install Ollama**
https://ollama.com/download

**Step 2 — Download Gemma 4**
```bash
ollama pull gemma4:e4b
```

**Step 3 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 4 — Start FastAPI backend**
```bash
uvicorn main:app --reload
```

**Step 5 — Run Streamlit frontend**
```bash
streamlit run app.py
```


## 👨‍💻 Made by Karam
Built for Kaggle Hackathon 2025
