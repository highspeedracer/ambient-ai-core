from fastapi import FastAPI
import pandas as pd
import joblib
from notifier import dispatch_sms

app = FastAPI(title="Ambient AI Core")

# 1. Load the AI Brain
try:
    ai_model = joblib.load("model_arthur-001.pkl")
    print("✅ Enterprise AI Model Loaded and Active")
except Exception as e:
    print("⚠️ Warning: AI Model not found. Run train_model.py first.")
    ai_model = None

@app.get("/")
def home():
    return {"status": "Online", "version": "2.0.1", "message": "Enterprise ML Engine Active"}

@app.get("/analyze/{patient_id}")
def get_analysis(patient_id: str):
    try:
        df = pd.read_csv('arthur_data.csv')
        baseline = df.head(20).mean(numeric_only=True)
        current_state = df.tail(1) 
        
        alerts = []
        risk_level = "LOW"

        # 2. The AI Decision Engine (Now with corrected lowercase SQL column names!)
        if ai_model:
            metrics_for_ai = pd.DataFrame({
                'steps': [current_state['Steps'].values[0]],
                'avg_heart_rate': [current_state['Avg_Heart_Rate'].values[0]],
                'sleep_hours': [current_state['Sleep_Hours'].values[0]],
                'bathroom_visits': [current_state['Bathroom_Visits'].values[0]]
            })
            
            prediction = ai_model.predict(metrics_for_ai)[0]
            
            if prediction == -1:
                risk_level = "HIGH"
                alerts.append("CRITICAL: AI detected a multivariate baseline anomaly.")
        
        # 3. Proactive Dispatch
        if alerts:
            dispatch_sms(patient_id, "Sarah (Daughter)", alerts)
        
        # 4. Return everything the Dashboard needs to render perfectly
        return {
            "patient": patient_id,
            "risk_level": risk_level,
            "active_alerts": alerts,
            "metrics": {
                "steps_baseline": int(baseline['Steps']),
                "steps_current": int(current_state['Steps'].values[0]),
                "bathroom_baseline": int(baseline['Bathroom_Visits']),
                "bathroom_current": int(current_state['Bathroom_Visits'].values[0]),
                "hr_baseline": int(baseline['Avg_Heart_Rate']),
                "hr_current": int(current_state['Avg_Heart_Rate'].values[0])
            }
        }
    except Exception as e:
        print(f"INTERNAL API ERROR: {e}") # This will print the actual error to Terminal 1
        return {"error": str(e)}