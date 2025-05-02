import streamlit as st
from utils.db import requests_col
from pages.Layout import layout  # Import the shared layout

if "username" not in st.session_state or st.session_state.get("role") != "serviceman":
    st.warning("You must be a serviceman to access this page.")
    st.stop()

st.set_page_config(page_title="My Jobs", page_icon="🧰")
layout()

st.title("🧰 My Assigned Jobs")

serviceman = st.session_state.get("username")
assigned_jobs = list(requests_col.find({"assigned_to": serviceman}))

if not assigned_jobs:
    st.info("You don't have any assigned jobs yet.")

for job in assigned_jobs:
    with st.expander(f"{job['category']} - {job['location']}"):
        st.write("**Client Name:**", job["name"])
        st.write("**Description:**", job["description"])
        st.write("**Urgency:**", job["urgency"])
        st.write("**Status:**", job.get("status", "Pending"))
        st.write("**Notes:**", job.get("admin_notes", "None"))

        update_status = st.selectbox("Update Status", ["Pending", "In Progress", "Completed"], index=["Pending", "In Progress", "Completed"].index(job.get("status", "Pending")), key=f"status_{job['_id']}")

        if st.button("Submit Update", key=f"btn_{job['_id']}"):
            requests_col.update_one(
                {"_id": job["_id"]},
                {"$set": {"status": update_status}}
            )
            st.success("Status updated!")
            st.experimental_rerun()
