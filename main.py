import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI  # Switched from AsyncOpenAI for stability

app = FastAPI()

# Allow the iPhone to talk to the server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Groq Engine (using LLaMA 3)
# We are using the standard OpenAI client but pointing it to Groq's servers
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# --- EXISTING ENDPOINTS ---
@app.get("/")
def read_root():
    return {"status": "Online", "version": "3.0.0", "message": "Enterprise Agent Active"}

@app.get("/analyze/{patient_id}")
def analyze_patient(patient_id: str):
    # This is your existing Arthur-001 code
    return {
        "patient": patient_id,
        "risk_level": "LOW",
        "metrics": {"hr_current": 70, "steps_current": 3114},
        "active_alerts": []
    }

# --- NEW COPILOT AI ENDPOINT ---
class ChatMessage(BaseModel):
    message: str

@app.post("/copilot")
def ask_copilot(chat: ChatMessage):
    # We inject the "System Prompt" so the AI knows it is a medical assistant
    # and we feed it the live database context invisibly.
    system_prompt = (
        "You are the Ambient AI Clinical Copilot, an expert triage assistant. "
        "Keep answers concise, highly clinical, and actionable. "
        "Current live context: Maria-042 triggered a HIGH risk alert at 02:14 AM. "
        "Gait analysis showed a 30% reduction in stride length. HR is elevated at 112 bpm. "
        "Arthur-001 is stable at 70 bpm."
    )

    try:
        # Removed 'await' because we are using the synchronous client
        response = client.chat.completions.create(
            model="llama3-70b-8192", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chat.message}
            ],
            temperature=0.2, 
        )
        return {"reply": response.choices[0].message.content}
    
    except Exception as e:
        return {"reply": f"SYSTEM ERROR: {str(e)}"}