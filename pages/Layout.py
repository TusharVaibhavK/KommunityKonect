# kommuniti_app/pages/layout.py
import streamlit as st

def layout():
    # Add the logout button to the sidebar, available on every page
    with st.sidebar:
        if st.button("🔒 Logout"):
            st.session_state.clear()
            st.success("Logged out successfully!")
            # st.experimental_rerun()

