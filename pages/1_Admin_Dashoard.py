import streamlit as st
from utils.db import requests_col
from bson import ObjectId
from datetime import datetime
from pages.Layout import layout  # Import the shared layout

layout()

if "username" not in st.session_state or st.session_state.get("role") != "admin":
    st.warning("You must be an admin to access this page.")
    st.stop()

st.set_page_config(page_title="Admin Dashboard", page_icon="🛠️")
# Call the layout function to make logout available
st.title("🛠️ Admin Dashboard")

status_filter = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Completed"])

query = {} if status_filter == "All" else {"status": status_filter}
requests = list(requests_col.find(query))

for req in requests:
    with st.expander(f"{req['category']} - {req['name']} @ {req['location']}"):
        st.write("**Description:**", req["description"])
        st.write("**Urgency:**", req["urgency"])
        st.write("**Status:**", req.get("status", "Pending"))
        st.write("**Assigned To:**", req.get("assigned_to", "Not Assigned"))
        st.write("**Timestamp:**", req.get("timestamp", "N/A"))

        new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Completed"], index=["Pending", "In Progress", "Completed"].index(req.get("status", "Pending")))
        assigned_to = st.text_input("Assign to", value=req.get("assigned_to", ""))
        admin_notes = st.text_area("Admin Notes", value=req.get("admin_notes", ""))

        if st.button("Update", key=str(req["_id"])):
            requests_col.update_one(
                {"_id": ObjectId(req["_id"])},
                {"$set": {
                    "status": new_status,
                    "assigned_to": assigned_to,
                    "admin_notes": admin_notes,
                    "timestamp": datetime.utcnow().isoformat()
                }}
            )
            st.success("Updated successfully!")
            st.experimental_rerun()