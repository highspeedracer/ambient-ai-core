import os
from fastapi import FastAPI, File, UploadFile
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

        # 2. ARCHIVE TO THE VAULT
        db.table("patient_logs").insert({
            "heart_rate": hr,
            "steps": steps,
            "nurse_query": chat.message,
            "ai_response": ai_reply
        }).execute()

        return {"reply": ai_reply}
    
    except Exception as e:
        return {"reply": f"SYSTEM ERROR: {str(e)}"}


# --- NEW: THE DYNAMIC SBAR SCRIBE ENDPOINT ---
class SBARRequest(BaseModel):
    patient_name: str
    age: int
    note: str
    vitals: dict

@app.post("/sbar")
async def generate_sbar(req: SBARRequest):
    hr = req.vitals.get("hr", 0)
    steps = req.vitals.get("steps", 0)

    system_prompt = (
        "You are an expert Clinical Scribe. Your ONLY job is to write a formal, strictly formatted "
        "SBAR (Situation, Background, Assessment, Recommendation) shift handoff report. "
        "Use professional medical terminology. Do not use conversational filler. "
        "Format with clear headings: **SITUATION:**, **BACKGROUND:**, **ASSESSMENT:**, **RECOMMENDATION:**."
    )
    
    # The context is now 100% dynamic to the specific patient
    clinical_context = (
        f"Generate SBAR for {req.patient_name}, age {req.age}. "
        f"Latest Biometrics: Heart Rate {hr} bpm, Steps {steps}. "
        f"Nurse's current note/status: {req.note}."
    )

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": clinical_context}
            ],
            temperature=0.1, 
        )
        
        db.table("patient_logs").insert({
            "heart_rate": hr,
            "steps": steps,
            "nurse_query": f"SYSTEM: GENERATE SBAR FOR {req.patient_name}",
            "ai_response": response.choices[0].message.content
        }).execute()

        return {"report": response.choices[0].message.content}
    
    except Exception as e:
        return {"report": f"SBAR GENERATION ERROR: {str(e)}"}


# --- NEW: FACILITY RADAR ENDPOINT ---
@app.get("/facility-status")
async def get_facility_status():
    import random
    
    # THE FIX: Age is now explicitly included for every patient
    mock_patients = [
        {"id": "101", "name": "Maria L.", "age": 78, "hr": random.randint(105, 118), "steps": 120, "status": "CRITICAL", "note": "Tachycardia risk"},
        {"id": "102", "name": "Arthur G.", "age": 65, "hr": random.randint(68, 75), "steps": 3100, "status": "STABLE", "note": "Normal rhythm"},
        {"id": "103", "name": "James W.", "age": 54, "hr": random.randint(85, 95), "steps": 450, "status": "ELEVATED", "note": "Monitor hydration"},
        {"id": "104", "name": "Isiah R.", "age": 23, "hr": random.randint(60, 70), "steps": 4210, "status": "STABLE", "note": "Optimal vitals"},
    ]
    
    # Simple Triage Logic Engine: If HR crosses a threshold, change status
    for p in mock_patients:
        if p["hr"] > 100:
            p["status"] = "CRITICAL"
        elif p["hr"] > 85:
            p["status"] = "ELEVATED"
        else:
            p["status"] = "STABLE"

    return {"patients": mock_patients}

# --- NEW: THE AMBIENT EAR (VOICE TRANSCRIPTION) ---
@app.post("/transcribe")
async def transcribe_voice(file: UploadFile = File(...)):
    try:
        # Read the audio file sent from the iPhone
        file_bytes = await file.read()
        
        # We must save it temporarily so Groq can process it
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(file_bytes)
            
        # Send the audio to Groq's Whisper model
        with open(temp_file_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                file=(temp_file_path, audio_file.read()),
                model="whisper-large-v3",
                prompt="The audio is a clinical medical observation. Use standard medical terminology.",
                response_format="text"
            )
            
        # Clean up the temporary file
        os.remove(temp_file_path)
        
        # Return the exact text to the iPhone
        return {"text": transcription}
        
    except Exception as e:
        return {"error": f"TRANSCRIPTION FAILED: {str(e)}"}