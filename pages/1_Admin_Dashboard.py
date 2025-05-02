import streamlit as st
from utils.db import requests_col, users_col
from bson import ObjectId
from datetime import datetime
from pages.Layout import layout
from utils.notifications import notify_assignment, notify_completion

# Shared layout + logout
layout()

# Only admins allowed
if "username" not in st.session_state or st.session_state.get("role") != "admin":
    st.warning("You must be an admin to access this page.")
    st.stop()

st.title("🛠️ Admin Dashboard")

# Filters
status_filter = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Completed"])
urgency_filter = st.selectbox("Filter by Urgency", ["All", "Low", "Medium", "High"])

# Build query
query = {}
if status_filter != "All":
    query["status"] = status_filter
if urgency_filter != "All":
    query["urgency"] = urgency_filter

# Fetch jobs
requests = list(requests_col.find(query))

if not requests:
    st.info("No matching service requests found.")
else:
    # Get all servicemen
    servicemen = [user["username"] for user in users_col.find({"role": "serviceman"})]

    for req in requests:
        with st.expander(f"{req.get('category', 'Unknown')} - {req.get('name', 'Unnamed')} @ {req.get('location', 'Unknown')}"):
            st.write(f"**Description:** {req['description']}")
            st.write(f"**Urgency:** {req.get('urgency', 'Not specified')}")
            st.write(f"**Status:** `{req.get('status', 'Pending')}`")
            st.write(f"**Assigned To:** {req.get('assigned_to', 'Not Assigned')}")
            st.write(f"**Timestamp:** {req.get('timestamp', 'N/A')}")

            # Update Fields
            # Get the current status and ensure it's one of the valid options
            current_status = req.get("status", "Pending")
            valid_statuses = ["Pending", "In Progress", "Completed"]
            
            # If the current status is not in valid options, default to "Pending"
            if current_status not in valid_statuses:
                current_status = "Pending"
                
            new_status = st.selectbox(
                "Update Status",
                valid_statuses,
                index=valid_statuses.index(current_status),
                key=f"status_{req['_id']}"
            )

            assigned_to = st.selectbox(
                "Assign to Serviceman",
                ["Not Assigned"] + servicemen,
                index=(["Not Assigned"] + servicemen).index(req.get("assigned_to", "Not Assigned")),
                key=f"assign_{req['_id']}"
            )

            admin_notes = st.text_area(
                "Admin Notes",
                value=req.get("admin_notes", ""),
                key=f"notes_{req['_id']}"
            )

            if st.button("✅ Update", key=f"update_{req['_id']}"):
                # Determine what changed
                status_changed = new_status != req.get("status")
                assignment_changed = assigned_to != req.get("assigned_to", "Not Assigned")
                
                # Update database
                requests_col.update_one(
                    {"_id": ObjectId(req["_id"])},
                    {"$set": {
                        "status": new_status,
                        "assigned_to": assigned_to if assigned_to != "Not Assigned" else None,
                        "admin_notes": admin_notes,
                        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    }}
                )
                
                # Send notifications based on changes
                if assignment_changed and assigned_to != "Not Assigned":
                    notify_assignment(str(req["_id"]), assigned_to)
                
                if status_changed and new_status == "Completed":
                    notify_completion(str(req["_id"]), st.session_state["username"])
                
                st.success("✅ Updated successfully!")

# ---------------------------
# New Admin Controls (Sidebar)
# ---------------------------
def get_pending_jobs():
    return list(requests_col.find({"status": "Pending"}))

def get_servicemen():
    return list(users_col.find({"role": "serviceman"}))

def assign_job(job_id, serviceman_username):
    requests_col.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {
            "assigned_to": serviceman_username,
            "status": "In Progress",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }}
    )
    notify_assignment(job_id, serviceman_username)

def force_complete_job(job_id, reason):
    requests_col.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {
            "status": "Completed",
            "admin_notes": f"[OVERRIDE] {reason}",
            "completed_by": st.session_state["username"],
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }}
    )
    notify_completion(job_id, st.session_state["username"])

# Sidebar tools for admins
if st.session_state.get("role") == "admin":
    st.sidebar.header("🧰 Serviceman Tools")

    pending_jobs = get_pending_jobs()
    servicemen_list = get_servicemen()

    if pending_jobs and servicemen_list:
        job_options = [f"{job['category']}" for job in pending_jobs]
        selected_index = st.sidebar.selectbox("Select Job", list(range(len(job_options))), format_func=lambda i: job_options[i])
        selected_job = pending_jobs[selected_index]

        serviceman_options = [
            f"{s.get('name', 'Unknown')} ({s.get('username', 'NoUsername')})" 
            for s in servicemen_list
        ]

        selected_serviceman_index = st.sidebar.selectbox("Assign To", list(range(len(servicemen_list))), format_func=lambda i: serviceman_options[i])
        selected_serviceman = servicemen_list[selected_serviceman_index]

        if st.sidebar.button("✅ Assign"):
            assign_job(str(selected_job["_id"]), selected_serviceman["username"])
            st.success(f"Job assigned to {selected_serviceman['name']}")

        # Emergency Override
        if st.sidebar.checkbox("🚨 Emergency Override"):
            override_reason = st.sidebar.text_area("Reason")
            if st.sidebar.button("Force Complete"):
                force_complete_job(str(selected_job["_id"]), override_reason)
                st.success("Job forcefully marked as completed.")
    else:
        st.sidebar.info("No pending jobs or servicemen available.")