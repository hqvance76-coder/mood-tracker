import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

st.set_page_config(page_title="Family Mood Tracker", page_icon="🏡", layout="centered")

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
FORM_URL = "https://docs.google.com/forms/d/1tUC46lsldbVi8xegpa-TDfRYtBl2o7OLsMtSgjTctlU/viewform"
st.link_button("👉 CLICK HERE TO LOG YOUR MOOD", FORM_URL, type="primary", use_container_width=True)
st.write("---")

# --- CONNECT AND READ GOOGLE SHEETS (BULLETPROOF METHOD) ---
try:
    # Safely get your link from secrets
    base_url = st.secrets["public_gsheets_url"]
    
    # Clean the link to parse it directly as a clean CSV download (bypasses space errors)
    if "/edit" in base_url:
        sheet_id = base_url.split("/d/")[1].split("/edit")[0]
    else:
        sheet_id = base_url.split("/d/")[1].split("/")[0]
        
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Form+Responses+1"
    
    # Read data directly from the generated CSV link
    df = pd.read_csv(csv_url)
    
    if df is not None and not df.empty:
        existing_data = pd.DataFrame()
        existing_data["Timestamp"] = pd.to_datetime(df.iloc[:, 0])
        existing_data["Name"] = df.iloc[:, 1].astype(str)
        existing_data["Color"] = df.iloc[:, 2].astype(str)
        
        if df.shape[1] > 3:
            existing_data["Notes"] = df.iloc[:, 3].fillna("")
        else:
            existing_data["Notes"] = ""
            
        existing_data["Score"] = existing_data["Color"].map(MOOD_MAPPING).fillna(3)
    else:
        existing_data = pd.DataFrame(columns=["Timestamp", "Name", "Color", "Notes", "Score"])
except Exception as e:
    st.error(f"Connecting to spreadsheet... Please ensure your Secrets link is correct. Details: {e}")
    existing_data = pd.DataFrame(columns=["Timestamp", "Name", "Color", "Notes", "Score"])

# --- DASHBOARD & STREAKS ---
st.header("📊 Family Dashboard")

if not existing_data.empty:
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
    st.info("No entries processed yet! Tap the big button at the top to log your first mood color.")
