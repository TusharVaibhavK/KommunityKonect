import streamlit as st
st.set_page_config(page_title="My Jobs", page_icon="🧰")

from utils.db import requests_col
from pages.Layout import layout
from datetime import datetime
from utils.notifications import notify_assignment, notify_completion
from utils.job_utils import log_job_action

# Check role and login
if "username" not in st.session_state or st.session_state.get("role") != "serviceman":
    st.warning("You must be a serviceman to access this page.")
    st.stop()

layout()

st.title("🧰 My Assigned Jobs")
serviceman = st.session_state.get("username")

assigned_jobs = list(requests_col.find({"assigned_to": serviceman}))

if not assigned_jobs:
    st.info("You don't have any assigned jobs yet.")

# Enhanced completion function
def complete_job(job_id: str, serviceman_username: str) -> str:
    """Enhanced with logging and notifications"""
    try:
        result = requests_col.update_one(
            {"_id": job_id, "assigned_to": serviceman_username},
            {"$set": {
                "status": "Completed",
                "completed_at": datetime.utcnow(),
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }}
        )

        if result.modified_count:
            log_job_action(job_id, "COMPLETED", serviceman_username)
            notify_completion(job_id, serviceman_username)
            return f"✅ Job {job_id} completed!"
        return "⚠️ Job not found or already completed"
    except Exception as e:
        return f"🚨 Error: {str(e)}"

for job in assigned_jobs:
    with st.expander(f"{job['category']} - {job['location']}"):
        st.write("**Client Name:**", job["name"])
        st.write("**Description:**", job["description"])
        st.write("**Urgency:**", job["urgency"])
        st.write("**Status:**", job.get("status", "Pending"))
        st.write("**Admin Notes:**", job.get("admin_notes", "None"))
        st.write("**Last Updated:**", job.get("timestamp", "N/A"))

        update_status = st.selectbox(
            "Update Status",
            ["Pending", "In Progress", "Completed"],
            index=["Pending", "In Progress", "Completed"].index(job.get("status", "Pending")),
            key=f"status_{job['_id']}"
        )

        serviceman_notes = st.text_area(
            "Add Notes",
            value=job.get("serviceman_notes", ""),
            key=f"notes_{job['_id']}"
        )

        if st.button("Submit Update", key=f"btn_{job['_id']}"):
            if update_status == "Completed":
                msg = complete_job(job["_id"], serviceman)
                st.success(msg)
            else:
                requests_col.update_one(
                    {"_id": job["_id"]},
                    {"$set": {
                        "status": update_status,
                        "serviceman_notes": serviceman_notes,
                        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    }}
                )
                st.success("Status updated!")
