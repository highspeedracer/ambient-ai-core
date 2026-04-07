import time
from datetime import datetime

def dispatch_sms(patient_id, contact_name, alerts):
    print("\n" + "="*50)
    print("🚨 INITIATING EMERGENCY DISPATCH PROTOCOL 🚨")
    print("="*50)
    
    # Simulating network delay to make it feel real
    time.sleep(1) 
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Connecting to Twilio SMS Gateway...")
    time.sleep(0.5)
    
    for alert in alerts:
        print(f"\n[SMS SENT at {timestamp}]")
        print(f"To: {contact_name} (Emergency Contact)")
        print(f"Message: 'AMBIENT AI ALERT for {patient_id}. {alert}. Please check on them immediately.'")
    
    print("\n" + "="*50)
    print("✅ DISPATCH COMPLETE AND LOGGED")
    print("="*50 + "\n")
    
    return True