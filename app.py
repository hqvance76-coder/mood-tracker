import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import plotly.express as px

st.set_page_config(page_title="Family Mood Tracker", page_icon="🏡", layout="centered")

MOOD_SPECTRUM = {
    "💙 Blue": {"vibe": "Calm / Low Vibration", "score": 1, "color": "#3b82f6"},
    "💚 Green": {"vibe": "Grounded / Centered", "score": 2, "color": "#10b981"},
    "💛 Yellow": {"vibe": "Balanced / Neutral", "score": 3, "color": "#eab308"},
    "🧡 Orange": {"vibe": "Active / Energetic", "score": 4, "color": "#f97316"},
    "❤️ Red": {"vibe": "Excited / High Vibration", "score": 5, "color": "#ef4444"}
}
FAMILY = ["Heather", "Paul", "Royall", "Parker", "Payton"]

st.title("🏡 Family Color & Vibration Tracker")

# Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    existing_data = conn.read(worksheet="Logs", ttl="1m")
except Exception:
    existing_data = pd.DataFrame(columns=["Timestamp", "Name", "Color", "Vibration Level", "Score", "Notes"])

# Check-In Form
st.header("✨ Daily Check-In")
with st.form(key="mood_form", clear_on_submit=True):
    name = st.selectbox("Who is checking in?", FAMILY)
    chosen_mood = st.radio("Select your energy color:", list(MOOD_SPECTRUM.keys()), horizontal=True)
    notes = st.text_area("Optional Notes:")
    submit_button = st.form_submit_button(label="Log My Color")

if submit_button:
    new_entry = pd.DataFrame([{
        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Name": name,
        "Color": chosen_mood,
        "Vibration Level": MOOD_SPECTRUM[chosen_mood]["vibe"],
        "Score": MOOD_SPECTRUM[chosen_mood]["score"],
        "Notes": notes
    }])
    updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
    conn.update(worksheet="Logs", data=updated_data)
    st.success("💖 Energy logged! Refreshing dashboard...")
    st.cache_data.clear()
    st.calendar = None 
    st.rerun()

# Dashboard & Analytics
st.write("---")
st.header("📊 Family Dashboard")

if not existing_data.empty:
    existing_data['Timestamp'] = pd.to_datetime(existing_data['Timestamp'])
    
    # Stars (Past 7 days)
    st.subheader("⭐ Weekly Star Rewards")
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    recent_logs = existing_data[existing_data['Timestamp'] >= one_week_ago]
    
    cols = st.columns(len(FAMILY))
    for i, member in enumerate(FAMILY):
        member_logs = recent_logs[recent_logs['Name'] == member]
        unique_days = member_logs['Timestamp'].dt.date.nunique()
        with cols[i]:
            if unique_days >= 5:
                st.metric(label=member, value="⭐ Star")
            else:
                st.metric(label=member, value="⚪ Active")
            st.caption(f"{unique_days}/5 days")

    # Chart
    st.write("---")
    fig = px.line(existing_data.tail(30), x='Timestamp', y='Score', color='Name', markers=True, title="Recent Energy Trends")
    fig.update_yaxes(range=[0.5, 5.5], tickvals=[1,2,3,4,5], ticktext=["Blue 💙", "Green 💚", "Yellow 💛", "Orange 🧡", "Red ❤️"])
    st.plotly_chart(fig, use_container_width=True)
