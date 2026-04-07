import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Ambient AI Care", layout="wide")

st.title("🛡️ Ambient AI: Senior Care Monitor")
st.subheader("Patient Status: Arthur-001")

# 1. Fetch data from our API
try:
    response = requests.get("http://127.0.0.1:8000/analyze/arthur-001")
    data = response.json()
    
    # 2. Top Level Metrics (The "At a Glance" view)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_color = "inverse" if data['risk_level'] == "HIGH" else "normal"
        st.metric("Risk Level", data['risk_level'], delta=None, delta_color=risk_color)
        
    with col2:
        st.metric("Daily Steps", data['metrics']['steps_current'], 
                  delta=data['metrics']['steps_current'] - data['metrics']['steps_baseline'])
        
    with col3:
        st.metric("Heart Rate (BPM)", data['metrics']['hr_current'], 
                  delta=data['metrics']['hr_current'] - data['metrics']['hr_baseline'], delta_color="inverse")

    # 3. Alert Box
    if data['active_alerts']:
        st.error("### ⚠️ Active Alerts")
        for alert in data['active_alerts']:
            st.write(f"- {alert}")

    # 4. Data Visualization (The "Investor" Charts)
    st.divider()
    st.write("### 30-Day Mobility Trend")
    df = pd.read_csv('arthur_data.csv')
    fig = px.line(df, x='Date', y='Steps', title='Daily Step Count (Anomaly Detected at End)')
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Could not connect to the Brain (API). Make sure main.py is running! Error: {e}")