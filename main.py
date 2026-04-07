import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from supabase import create_client, Client

app = FastAPI()

# Allow iPhone connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq & Supabase
client = AsyncOpenAI(api_key=os.environ.get("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
db: Client = create_client(supabase_url, supabase_key)

class ChatMessage(BaseModel):
    message: str
    real_time_metrics: dict = None 

@app.post("/copilot")
async def ask_copilot(chat: ChatMessage):
    vitals = chat.real_time_metrics or {}
    hr = vitals.get("hr", 0)
    steps = vitals.get("steps", 0)

    system_prompt = f"You are Ambient AI. Vitals: HR {hr}, Steps {steps}. Be clinical and brief."

    try:
        # 1. Get AI response
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": chat.message}],
            temperature=0.2,
        )
        ai_reply = response.choices[0].message.content

        # 2. ARCHIVE TO THE VAULT (The $200M Move)
        db.table("patient_logs").insert({
            "heart_rate": hr,
            "steps": steps,
            "nurse_query": chat.message,
            "ai_response": ai_reply
        }).execute()

        return {"reply": ai_reply}
    
    except Exception as e:
        return {"reply": f"SYSTEM ERROR: {str(e)}"}

# --- NEW: THE SBAR SCRIBE ENDPOINT ---
class SBARRequest(BaseModel):
    patient_name: str
    vitals: dict

@app.post("/sbar")
async def generate_sbar(req: SBARRequest):
    hr = req.vitals.get("hr", 0)
    steps = req.vitals.get("steps", 0)

    # We force LLaMA to become a strict medical scribe
    system_prompt = (
        "You are an expert Clinical Scribe. Your ONLY job is to write a formal, strictly formatted "
        "SBAR (Situation, Background, Assessment, Recommendation) shift handoff report. "
        "Use professional medical terminology. Do not use conversational filler. "
        "Format with clear headings: **SITUATION:**, **BACKGROUND:**, **ASSESSMENT:**, **RECOMMENDATION:**."
    )
    
    clinical_context = (
        f"Generate SBAR for {req.patient_name}. "
        f"Latest Biometrics: Heart Rate {hr} bpm, Steps {steps}. "
        "Context: Patient is a 23-year-old male under high cognitive stress. Simulated environment."
    )

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": clinical_context}
            ],
            temperature=0.1, # Extremely low temperature so it doesn't hallucinate
        )
        # Log this report to the Vault as well
        db.table("patient_logs").insert({
            "heart_rate": hr,
            "steps": steps,
            "nurse_query": "SYSTEM: GENERATE SBAR",
            "ai_response": response.choices[0].message.content
        }).execute()

        return {"report": response.choices[0].message.content}
    
    except Exception as e:
        return {"report": f"SBAR GENERATION ERROR: {str(e)}"}