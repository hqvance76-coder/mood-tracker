import streamlit as st

st.set_page_config(page_title="Family Mood Tracker", page_icon="🏡", layout="centered")

st.title("🏡 Family Color & Vibration Tracker")
st.markdown("A shared space to map our energy levels and look out for each other.")

# --- BIG BUTTON TO LOG MOOD ---
# Replace the link below with your actual Google Form link!
FORM_URL = "https://docs.google.com/forms/d/1tUC46lsldbVi8xegpa-TDfRYtBl2o7OLsMtSgjTctlU/viewform"

st.link_button("👉 CLICK HERE TO LOG YOUR MOOD", FORM_URL, type="primary", use_container_width=True)

st.write("---")
st.info("Tap the button above to log your energy level. You can view the live charts right after submitting your entry!")
