<<<<<<< HEAD
import streamlit.components.v1 as components
=======
>>>>>>> a17f65f845572487a607ae2c739c6becc154cc01
import streamlit as st
from utils.auth import verify_user
from utils.db import users_col
from utils.db_init import init_database

# Initialize the database when the app starts
client = init_database()

# Redirect to the login page

# Add auto-redirect to the login page
components.html(
    """
    <script>
    window.location.href = '/Login_or_Register';
    </script>
    """,
    height=0
)

import requests

# Fetch the public IP
ip = requests.get("https://api.ipify.org").text

# Display it (or log it)
st.write(f"Streamlit App's Outbound IP: **{ip}**")

# st.set_page_config(page_title="Kommuniti App", page_icon="🔧")

st.title("KommunityKonect")
st.write("Redirecting to login page...")

st.title("🔐 Login to Kommuniti Dashboard")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
