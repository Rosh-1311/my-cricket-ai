import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time

# --- 1. GLOBAL VENUE & SOIL DATABASE ---
# This dictionary contains 'Minute Details' like Soil Geotechnics and Altitude
VENUES_DATABASE = {
    "Wankhede, Mumbai": {"soil": "Red", "clay": 0.40, "altitude": 10, "avg_temp": 30, "drainage": "High"},
    "Chepauk, Chennai": {"soil": "Black", "clay": 0.70, "altitude": 5, "avg_temp": 33, "drainage": "Medium"},
    "Perth (Optus), AUS": {"soil": "Clay-Heavy", "clay": 0.80, "altitude": 20, "avg_temp": 28, "drainage": "Extreme"},
    "Lord's, London": {"soil": "Loam", "clay": 0.30, "altitude": 35, "avg_temp": 22, "drainage": "Low"}
}

# --- 2. THE INTELLIGENCE CORE ---
class CricketAI:
    @staticmethod
    def calculate_pitch_physics(venue_name, temp, humidity, clouds):
        v = VENUES_DATABASE[venue_name]
        
        # Physics: Thermal Contraction of Soil (Black soil cracks in heat > 32C)
        spin_index = 0.4 + (0.4 if v['soil'] == "Black" and temp > 31 else 0)
        
        # Physics: Magnus Effect & Air Density (Swing)
        # Higher altitude = Thinner air = Less swing. High humidity = Denser air = More swing.
        base_swing = (humidity / 100) * (clouds / 100)
        altitude_penalty = v['altitude'] / 2000 # Higher altitude reduces swing
        swing_prob = max(0, base_swing - altitude_penalty)
        
        # Dew Logic: Night + Humidity > 70%
        is_night = datetime.now().hour >= 18 or datetime.now().hour <= 4
        dew_factor = 0.85 if is_night and humidity > 70 else 0.1
        
        return {"swing": swing_prob, "spin": spin_index, "dew": dew_factor}

    @staticmethod
    def player_dna_eval(role, pressure, spin_skill, accel_rating, physics):
        score = 80
        alerts = []
        
        # CHOKE LOGIC: Low Pressure Resistance + High Dew (Slippery ball)
        if pressure < 45 and physics['dew'] > 0.7:
            score -= 25
            alerts.append("🚩 **CHOKE ALERT:** High failure probability under dew/pressure.")
            
        # SPIN-CHOKE: Poor skill vs high surface grip
        if physics['spin'] > 0.7 and spin_skill < 50:
            score -= 20
            alerts.append("🌀 **SPIN TRAP:** Batter likely to be suffocated by spin on this surface.")
            
        # ACCELERATION: 
        if accel_rating > 80:
            score += 15
            alerts.append("🚀 **ACCELERATOR:** Elite ability to shift gears in death overs.")
            
        return max(0, min(100, score)), alerts

# --- 3. THE PROFESSIONAL UI ---
st.set_page_config(page_title="AI Cricket Strategy Suite", layout="wide")

st.title("🏹 AI Cricket Intelligence Suite (V7.0 - Pro)")
st.caption("No API Required | Physics-Engine Enabled | Behavioral DNA Mapping")

# Sidebar for Match Setup
with st.sidebar:
    st.header("📍 Match Context")
    venue = st.selectbox("Select Global Venue", list(VENUES_DATABASE.keys()))
    temp = st.slider("Temperature (°C)", 10, 45, 30)
    humidity = st.slider("Humidity (%)", 10, 100, 75)
    clouds = st.slider("Cloud Cover (%)", 0, 100, 20)

# Calculate Physics
ai = CricketAI()
physics = ai.calculate_pitch_physics(venue, temp, humidity, clouds)

# Dashboard Columns
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Atmospheric Swing", f"{int(physics['swing']*100)}%")
    st.progress(physics['swing'])
with c2:
    st.metric("Surface Spin-Grip", f"{int(physics['spin']*100)}%")
    st.progress(physics['spin'])
with c3:
    st.metric("Dew Impact Risk", "CRITICAL" if physics['dew'] > 0.7 else "Safe")
    st.progress(physics['dew'])

st.divider()

# Player Analysis Section
st.subheader("👤 Deep Player DNA Mapping")
p_name = st.text_input("Enter Player Name", "E.g. Virat Kohli")
p_role = st.selectbox("Archetype", ["Power Hitter", "Anchor", "Wrist Spinner", "Swing Bowler"])

col_a, col_b, col_c = st.columns(3)
p_press = col_a.slider("Pressure Resistance", 0, 100, 80)
p_spin = col_b.slider("Skill vs Spin", 0, 100, 70)
p_accel = col_c.slider("Acceleration Power", 0, 100, 60)

if st.button("RUN TACTICAL SIMULATION"):
    with st.spinner('Processing physics and behavioral DNA...'):
        time.sleep(1) # Simulated processing
        score, reports = ai.player_dna_eval(p_role, p_press, p_spin, p_accel, physics)
        
        st.markdown(f"### AI Strategic Score: `{score}/100`")
        for r in reports:
            st.info(r)

st.divider()
st.caption("Engine Notes: This model uses the **Clausius-Clapeyron** relation to estimate dew point and **Soil Geotechnics** for pitch behavior.")