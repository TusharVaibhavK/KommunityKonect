import streamlit.components.v1 as components
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

st.set_page_config(page_title="Kommuniti App", page_icon="🔧")

st.title("KommunityKonect")
st.write("Redirecting to login page...")

st.title("🔐 Login to Kommuniti Dashboard")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = verify_user(username, password)
    if user:
        st.success(f"Welcome, {user['username']}! Redirecting...")
        if user["role"] == "admin":
            st.switch_page("pages/1_Admin_Dashboard.py")
        elif user["role"] == "serviceman":
            st.switch_page("pages/2_Serviceman_View.py")
    else:
        st.error("Invalid username or password")
