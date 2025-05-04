import streamlit as st
from utils.auth import verify_user
from utils.db import users_col

import requests

# Fetch the public IP
ip = requests.get("https://api.ipify.org").text

# Display it (or log it)
st.write(f"Streamlit App's Outbound IP: **{ip}**")

# st.set_page_config(page_title="Kommuniti App", page_icon="🔧")

st.title("🔐 Login to Kommuniti Dashboard")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
