import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["your_db_name"]  # replace with your DB name
requests_col = db["service_requests"]
posts_col = db["community_posts"]

# Simulate logged-in user
current_user = st.session_state.get("username", "demo_user")

st.title("👤 My Dashboard")

# View Switcher Tiles
col1, col2 = st.columns(2)
with col1:
    view_repairs = st.button("🔧 My Repair Requests")
with col2:
    view_community = st.button("🏘️ Community Feed")

# Default view
if "dashboard_view" not in st.session_state:
    st.session_state["dashboard_view"] = "repairs"

if view_repairs:
    st.session_state["dashboard_view"] = "repairs"
if view_community:
    st.session_state["dashboard_view"] = "community"

# ------------------------------------------
# 🔧 My Repair Requests View
# ------------------------------------------
if st.session_state["dashboard_view"] == "repairs":
    st.subheader("🔧 My Service Requests")

    my_requests = requests_col.find({"user_id": current_user}).sort("timestamp", -1)
    for req in my_requests:
        st.markdown(f"**Request ID:** `{str(req['_id'])}`")
        st.write(f"**Status:** {req.get('status', 'N/A')}")
        st.write(f"**Assigned To:** {req.get('assigned_to', 'Not Assigned')}")
        st.image(req.get("photo_url", ""), width=300)
        st.caption(f"Submitted on {req.get('timestamp', '')[:19].replace('T', ' ')}")
        st.markdown("---")

# ------------------------------------------
# 🏘️ Community Feed View
# ------------------------------------------
elif st.session_state["dashboard_view"] == "community":
    st.subheader("🏘️ Community Posts")

    posts = posts_col.find().sort("timestamp", -1)
    for post in posts:
        st.markdown(f"**{post['title']}**")
        st.caption(f"by `{post['author']}` at {post['timestamp'][:19].replace('T', ' ')}")
        st.write(post['content'])
        if post.get("invited_users"):
            st.info(f"Invited: {', '.join(post['invited_users'])}")
        st.markdown("---")
