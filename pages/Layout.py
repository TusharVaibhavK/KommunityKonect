import streamlit as st
from datetime import datetime, date, time
from utils.db import users_col  
from utils.calendar import calendar_view
from utils.job_utils import log_job_action, get_serviceman_jobs
from utils.notifications import notify_assignment, notify_completion

def layout():
    """Shared layout for all pages with logout button and calendar"""
    # Add the logout button to the sidebar, available on every page
    with st.sidebar:
        if st.button("🔒 Logout"):
            st.session_state.clear()
            st.success("Logged out successfully!")
            # st.experimental_rerun()  # Uncomment this if you want the page to reload after logout

        # Initialize calendar session state
        if 'calendar_date' not in st.session_state:
            st.session_state.calendar_date = date.today()  # Using `date.today()` correctly

        if 'selected_serviceman' not in st.session_state:
            st.session_state.selected_serviceman = None

        # Show calendar for authorized users
        if st.session_state.get("role") in ["admin", "serviceman"]:
            calendar_view()
