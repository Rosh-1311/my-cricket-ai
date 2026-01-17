import streamlit as st
import pandas as pd
import requests
import zipfile
import io

# --- 1. AUTOMATED DATA FETCHING (Cricsheet) ---
@st.cache_data
def get_historical_data():
    url = "https://cricsheet.org/downloads/t20s_csv.zip"
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    # We load the main match data (this is the big data pool)
    df = pd.concat([pd.read_csv(z.open(f)) for f in z.namelist()[:100] if 'info' not in f])
    return df

# --- 2. THE MATCHUP BRAIN ---
def analyze_matchup(df, batsman, bowler):
    # Filter for specific head-to-head encounters
    h2h = df[(df['striker'] == batsman) & (df['bowler'] == bowler)]
    
    if h2h.empty:
        return None, "No historical H2H data found. Switching to Skill-Type analysis..."

    stats = {
        "Balls Faced": len(h2h),
        "Runs Scored": h2h['runs_off_bat'].sum(),
        "Dismissals": len(h2h[h2h['wicket_type'].notnull()]),
        "Dots": len(h2h[h2h['runs_off_bat'] == 0]),
        "Boundaries": len(h2h[h2h['runs_off_bat'].isin([4, 6])])
    }
    stats["Strike Rate"] = (stats["Runs Scored"] / stats["Balls Faced"]) * 100
    return stats, "H2H Data Found"

# --- 3. THE INTERFACE ---
st.set_page_config(page_title="Matchup AI Pro", layout="wide")
st.title("🎯 Pro Matchup Intelligence: Batsman vs Bowler")

with st.spinner("Downloading Global Match Data..."):
    raw_data = get_historical_data()

# Selection UI
col1, col2 = st.columns(2)
with col1:
    batsman_name = st.selectbox("Select Batsman", sorted(raw_data['striker'].unique()))
with col2:
    bowler_name = st.selectbox("Select Bowler", sorted(raw_data['bowler'].unique()))

if st.button("Generate Matchup Report"):
    stats, msg = analyze_matchup(raw_data, batsman_name, bowler_name)
    
    st.subheader(f"⚔️ {batsman_name} vs {bowler_name}")
    st.write(f"Status: {msg}")
    
    if stats:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Strike Rate", f"{stats['Strike Rate']:.1f}")
        m2.metric("Dismissals", stats['Dismissals'])
        m3.metric("Dot %", f"{(stats['Dots']/stats['Balls Faced'])*100:.1f}%")
        m4.metric("Balls Faced", stats['Balls Faced'])
        
        # Tactical Advice
        if stats['Strike Rate'] < 110:
            st.error(f"⚠️ **Choke Alert:** {bowler_name} successfully suppresses {batsman_name}'s scoring.")
        elif stats['Dismissals'] > 2:
            st.warning(f"🚩 **Vulnerability:** {bowler_name} has {batsman_name}'s number.")
        else:
            st.success(f"🚀 **Dominance:** {batsman_name} handles this matchup with ease.")