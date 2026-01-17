import streamlit as st
import pandas as pd
import requests
import zipfile
import io
import plotly.express as px

# --- 1. DATA ENGINE (ROBUST & BULLETPROOF) ---
@st.cache_data
def get_cleaned_data():
    url = "https://cricsheet.org/downloads/t20s_csv.zip"
    try:
        response = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(response.content))
        
        match_data_list = []
        # We process the first 150 files for a robust sample size
        for filename in z.namelist()[:150]:
            # ONLY read match files, ignore README and info files
            if filename.endswith('.csv') and not filename.endswith('_info.csv') and 'README' not in filename:
                try:
                    with z.open(filename) as f:
                        df = pd.read_csv(f)
                        # Ensure standard columns exist
                        if 'striker' in df.columns and 'bowler' in df.columns:
                            match_data_list.append(df)
                except Exception:
                    continue # Skip corrupted files
        
        return pd.concat(match_data_list, ignore_index=True)
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

# --- 2. THE UI & ANALYSIS ---
st.set_page_config(page_title="Cricket Pro-Matchup AI", layout="wide")
st.title("🎯 Pro-Scout: Matchup & Phase Intelligence")

data = get_cleaned_data()

if not data.empty:
    # Sidebar Filters
    st.sidebar.header("Scouting Filters")
    all_batsmen = sorted(data['striker'].unique())
    all_bowlers = sorted(data['bowler'].unique())
    
    batsman = st.sidebar.selectbox("Select Batsman", all_batsmen)
    bowler = st.sidebar.selectbox("Select Bowler", all_bowlers)
    
    # --- CALCULATION LOGIC ---
    # 1. Head-to-Head Data
    h2h = data[(data['striker'] == batsman) & (data['bowler'] == bowler)]
    
    # 2. General Batsman Stats (for Strengths/Weaknesses)
    b_stats = data[data['striker'] == batsman]
    
    # --- DASHBOARD ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(f"⚔️ Matchup: {batsman} vs {bowler}")
        if not h2h.empty:
            balls = len(h2h)
            runs = h2h['runs_off_bat'].sum()
            outs = h2h['wicket_type'].notna().sum()
            dots = (h2h['runs_off_bat'] == 0).sum()
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Strike Rate", round((runs/balls)*100, 1))
            m2.metric("Dismissals", outs)
            m3.metric("Dot Ball %", f"{round((dots/balls)*100, 1)}%")
        else:
            st.info("No direct historical matchup found in this sample. Displaying player archetypes...")

    with col2:
        st.subheader("🚀 Acceleration Profile")
        # Define Phases
        b_stats = b_stats.copy()
        b_stats['phase'] = pd.cut(b_stats['ball'], bins=[0, 6, 15, 20], labels=['Powerplay', 'Middle', 'Death'])
        phase_performance = b_stats.groupby('phase', observed=False)['runs_off_bat'].sum().reset_index()
        
        fig = px.bar(phase_performance, x='phase', y='runs_off_bat', color='phase', title="Runs by Match Phase")
        st.plotly_chart(fig, use_container_width=True)

    # --- DEEP ANALYTICS ---
    st.divider()
    st.subheader("🔍 AI Scouting Report")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### **💪 Strengths**")
        # Logic: High strike rate in specific phases
        death_sr = b_stats[b_stats['phase'] == 'Death']['runs_off_bat'].mean() * 100
        if death_sr > 180:
            st.success("Elite Death Over Accelerator: High impact in final 5 overs.")
        st.write(f"- Boundary Frequency: 1 every {round(len(b_stats)/b_stats['runs_off_bat'].isin([4,6]).sum(), 1)} balls")

    with col_b:
        st.markdown("### **⚠️ Weaknesses**")
        dot_avg = (b_stats['runs_off_bat'] == 0).mean() * 100
        if dot_avg > 40:
            st.error(f"High Dot% ({round(dot_avg, 1)}%): Struggles with strike rotation.")
        if not h2h.empty and outs > 0:
            st.warning(f"Tactical Vulnerability: Has been dismissed by {bowler} {outs} times.")

else:
    st.warning("Data is still loading or unavailable. Please wait 30 seconds and refresh.")