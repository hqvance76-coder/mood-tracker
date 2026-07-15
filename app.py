import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import plotly.express as px

st.set_page_config(page_title="Family Mood Tracker", page_icon="🏡", layout="centered")

# Map the exact textual answers from your Google Form to numerical scores for the chart
MOOD_MAPPING = {
    "💙 Blue": 1,
    "💚 Green": 2,
    "💛 Yellow": 3,
    "🧡 Orange": 4,
    "❤️ Red": 5
}
FAMILY = ["Heather", "Paul", "Royall", "Parker", "Payton"]

st.title("🏡 Family Color & Vibration Tracker")
st.markdown("A shared space to map our energy levels and look out for each other.")

# --- BIG BUTTON TO LOG MOOD ---
# PASTE YOUR GOOGLE FORM LINK BETWEEN THE QUOTES BELOW:
FORM_URL = "https://forms.gle/goJYoSG6LKWTNvZY6"

st.link_button("👉 CLICK HERE TO LOG YOUR MOOD", FORM_URL, type="primary", use_container_width=True)
st.write("---")

# --- CONNECT AND READ GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Google Forms automatically creates a tab named "Form Responses 1"
    existing_data = conn.read(worksheet="Form Responses 1", ttl="1m")
    
    # Rename columns to match what Google Form creates so Python can read them easily
    existing_data.columns = ["Timestamp", "Name", "Color", "Notes"]
    # Create numerical score column for plotting the trend line
    existing_data["Score"] = existing_data["Color"].map(MOOD_MAPPING)
except Exception:
    existing_data = pd.DataFrame(columns=["Timestamp", "Name", "Color", "Notes", "Score"])

# --- DASHBOARD & STREAKS ---
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
    
    # Notes Feed
    st.write("---")
    st.subheader("📝 Recent Notes")
    notes_df = existing_data[existing_data['Notes'].fillna('').str.strip().astype(bool)].tail(5)
    for _, row in notes_df.iloc[::-1].iterrows():
        st.markdown(f"**{row['Name']}** ({row['Timestamp'].strftime('%a %b %d')}):")
        st.info(f"\"{row['Notes']}\"")
else:
    st.info("No entries found yet! Tap the big button at the top to log your first mood color.")
