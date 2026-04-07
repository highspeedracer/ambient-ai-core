import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# --- THE DATA ARCHITECTURE ---
class ChatMessage(BaseModel):
    message: str
    # This allows the iPhone to send a dictionary of vitals
    real_time_metrics: dict = None 

@app.get("/")
def read_root():
    return {"status": "Online", "version": "3.2.0"}

# --- THE DYNAMIC AI ENGINE ---
@app.post("/copilot")
async def ask_copilot(chat: ChatMessage):
    # Extract the data sent from your iPhone
    vitals = chat.real_time_metrics or {}
    hr = vitals.get("hr", "N/A")
    steps = vitals.get("steps", "N/A")

    # This is the secret sauce: The AI now knows EXACTLY what is happening to the user
    system_prompt = (
        "You are the Ambient AI Clinical Copilot. You are currently monitoring a 23-year-old male student. "
        f"LIVE VITALS: Heart Rate is {hr} bpm. Total steps today: {steps}. "
        "Context: Patient is healthy but under high cognitive load (coding/studying). "
        "Keep responses clinical, actionable, and extremely brief. "
        "If Heart Rate is above 100, mention 'Tachycardia risk'. If below 60, mention 'Bradycardia'."
    )

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chat.message}
            ],
            temperature=0.2,
        )
        return {"reply": response.choices[0].message.content}
    
    except Exception as e:
        return {"reply": f"SYSTEM ERROR: {str(e)}"}