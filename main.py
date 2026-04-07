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