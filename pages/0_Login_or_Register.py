import streamlit as st
from utils.db import users_col
import hashlib
from pages.Layout import layout  # Import the shared layout

st.set_page_config(page_title="Login / Register", page_icon="🔐")
st.title("🔐 Login or Register")

menu = st.selectbox("Choose Action", ["Login", "Register"])

if menu == "Register":
    st.subheader("Create New Account")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type='password')
    role = st.selectbox("Select your role", [
                        "Admin", "Serviceman", "Resident"])
    telegram_id = st.text_input("Telegram ID (Optional)", "")

    if st.button("Register"):
        hashed_pass = hashlib.sha256(new_pass.encode()).hexdigest()
        if users_col.find_one({"username": new_user}):
            st.warning("🚫 Username already exists")
        else:
            # Create user document with proper handling of telegram_id
            user_doc = {
                "username": new_user,
                "password": hashed_pass,
                "role": role
            }

            # Only add telegram_id if it's provided
            if telegram_id:
                user_doc["telegram_id"] = telegram_id

            users_col.insert_one(user_doc)
            st.success("✅ Registered successfully. You can now login.")

if menu == "Login":
    st.subheader("Login to your account")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        hashed_pass = hashlib.sha256(password.encode()).hexdigest()
        user = users_col.find_one(
            {"username": username, "password": hashed_pass})
        if user:
            st.session_state["username"] = user["username"]
            st.session_state["role"] = user["role"]
            st.success(f"✅ Logged in as {user['role'].capitalize()}")
            if user['role'] == "admin":
                st.switch_page("pages/1_Admin_Dashboard.py")
            else:
                st.switch_page("pages/2_Serviceman_View.py")
        else:
            st.error("❌ Invalid credentials")
