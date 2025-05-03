import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import os
from service_agents.community_concierge import CommunityConcierge
from dotenv import load_dotenv

load_dotenv()

# MongoDB Setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["kommuniti"]  # Replace with your DB name
posts_col = db["community_posts"]
users_col = db["users"]  # Assuming you have a collection with user info

# Simulate current logged-in user (replace with actual auth system)
current_user = st.session_state.get("username", "demo_user")

st.title("🏘️ Community Board")

# Initialize agent
if 'concierge' not in st.session_state:
    st.session_state.concierge = CommunityConcierge()

tab1, tab2, tab3 = st.tabs(["Create Event", "View Events", "Manage Invites"])

with tab1:
    with st.form("create_event"):
        title = st.text_input("Event Title")
        description = st.text_area("Description")
        date = st.date_input("Date")

        if st.form_submit_button("Create Event"):
            result = st.session_state.concierge.create_community_event({
                "title": title,
                "description": description,
                "date": date.strftime("%Y-%m-%d")
            })
            st.success(result)

with tab2:
    events = st.session_state.concierge.list_community_events("upcoming")
    st.write(events)

with tab3:
    # Implement invite management UI
    st.write("Invite management coming soon!")


# --- Post Creation ---
st.subheader("📢 Create a Community Post")
with st.form("post_form"):
    title = st.text_input("Title")
    content = st.text_area("Content")

    all_users = [u["username"] for u in users_col.find(
        {}, {"username": 1}) if u.get("username") and u["username"] != current_user]
    invited = st.multiselect("Invite Residents", options=all_users)

    submitted = st.form_submit_button("Post")
    if submitted and title and content:
        posts_col.insert_one({
            "author": current_user,
            "title": title,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "invited_users": invited
        })
        st.success("Post created and invites sent!")

st.markdown("---")

# --- Feed ---
st.subheader("📰 Community Feed")

posts = posts_col.find().sort("timestamp", -1)
for post in posts:
    st.markdown(f"**{post['title']}**")
    st.caption(
        f"by `{post['author']}` at {post['timestamp'][:19].replace('T', ' ')}")
    st.write(post['content'])
    if post.get("invited_users"):
        st.info(f"Invited: {', '.join(post['invited_users'])}")
    st.markdown("---")
