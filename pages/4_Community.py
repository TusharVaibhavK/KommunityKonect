import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import os
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

# --- Post Creation ---
st.subheader("📢 Create a Community Post")
with st.form("post_form"):
    title = st.text_input("Title")
    content = st.text_area("Content")
    
    all_users = [u["username"] for u in users_col.find({}, {"username": 1}) if u.get("username") and u["username"] != current_user]
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
    st.caption(f"by `{post['author']}` at {post['timestamp'][:19].replace('T', ' ')}")
    st.write(post['content'])
    if post.get("invited_users"):
        st.info(f"Invited: {', '.join(post['invited_users'])}")
    st.markdown("---")
