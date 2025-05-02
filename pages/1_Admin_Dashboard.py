import streamlit as st
from utils.db import requests_col, users_col
from bson import ObjectId
from datetime import datetime
from pages.Layout import layout  # Import the shared layout

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
        with st.expander(f"{req['category']} - {req['name']} @ {req['location']}"):
            st.write(f"**Description:** {req['description']}")
            st.write(f"**Urgency:** {req['urgency']}")
            st.write(f"**Status:** `{req.get('status', 'Pending')}`")
            st.write(f"**Assigned To:** {req.get('assigned_to', 'Not Assigned')}")
            st.write(f"**Timestamp:** {req.get('timestamp', 'N/A')}")

            # Update Fields
            new_status = st.selectbox(
                "Update Status",
                ["Pending", "In Progress", "Completed"],
                index=["Pending", "In Progress", "Completed"].index(req.get("status", "Pending")),
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
                requests_col.update_one(
                    {"_id": ObjectId(req["_id"])},
                    {"$set": {
                        "status": new_status,
                        "assigned_to": assigned_to if assigned_to != "Not Assigned" else None,
                        "admin_notes": admin_notes,
                        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    }}
                )
                st.success("✅ Updated successfully!")
                # st.experimental_rerun()
