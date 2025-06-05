import streamlit as st
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["kommuniti"]

# Get current logged-in user info
current_user = st.session_state.get("username", None)
user_role = st.session_state.get("role", None)

# Page configuration
st.set_page_config(
    page_title="KommunitiKonect - Home",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check login state
if not current_user:
    st.warning("Please log in to access all features.")
    st.info("Click on Login/Register in the sidebar to get started.")

# Banner and welcome
col1, col2 = st.columns([2, 1])
with col1:
    st.title("🏡 Welcome to KommunitiKonect")
    if current_user:
        st.subheader(f"Hello, {current_user}!")

    st.markdown("""
    Your all-in-one community management platform connecting residents 
    with service professionals for a seamless living experience.
    """)

# Quick stats
if current_user:
    st.markdown("---")
    st.subheader("📊 Your Dashboard Overview")

    # Get user-specific stats
    user_requests = db["service_requests"].count_documents(
        {"requester": current_user})
    attending_events = db["community_events"].count_documents(
        {"attendees": current_user})

    # Show stats in columns
    stat1, stat2, stat3, stat4 = st.columns(4)
    with stat1:
        st.metric("Service Requests", user_requests)
    with stat2:
        st.metric("Events Attending", attending_events)
    with stat3:
        if user_role == "serviceman":
            assigned_jobs = db["service_requests"].count_documents(
                {"assigned_to": current_user})
            st.metric("Assigned Jobs", assigned_jobs)
        else:
            community_posts = db["community_posts"].count_documents(
                {"author": current_user})
            st.metric("Community Posts", community_posts)
    with stat4:
        # Show date of joining
        user_data = db["users"].find_one({"username": current_user})
        if user_data and "created_at" in user_data:
            join_date = datetime.fromisoformat(
                user_data["created_at"]).strftime("%b %d, %Y")
            st.metric("Member Since", join_date)
        else:
            st.metric("Member Since", "N/A")

# Main features section
st.markdown("---")
st.header("🌟 Key Features")

# Create three columns for main features
feat1, feat2, feat3 = st.columns(3)

with feat1:
    st.subheader("🔧 Service Requests")
    st.markdown("""
    - Submit maintenance requests
    - Upload photos of issues
    - Track request status
    - Rate service quality
    """)
    if st.button("Submit a Request", key="request_btn"):
        st.switch_page("pages/3_Submit_Request.py")

with feat2:
    st.subheader("🏘️ Community Board")
    st.markdown("""
    - Create and join community events
    - Share important announcements
    - Connect with neighbors
    - RSVP to local gatherings
    """)
    if st.button("Visit Community Board", key="community_btn"):
        st.switch_page("pages/4_Community.py")

with feat3:
    st.subheader("👤 User Dashboard")
    st.markdown("""
    - View your activity history
    - Manage personal requests
    - Check upcoming events
    - Update profile information
    """)
    if st.button("View Dashboard", key="dashboard_btn"):
        st.switch_page("pages/5_User_Dashboard.py")

# Telegram integration
st.markdown("---")
st.header("📱 Connect with our Telegram Bot")

col_tg1, col_tg2 = st.columns([1, 2])

with col_tg1:
    # QR code or Telegram logo
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/512px-Telegram_logo.svg.png",
             width=150)
    st.markdown("""
    Scan the QR code or click the button to connect with our Telegram bot
    for instant notifications and request submissions on the go!
    """)

    telegram_url = "https://t.me/KommunitiNotifer_bot"
    st.markdown(f"[Connect with @KommunitiNotifer_bot]({telegram_url})")

with col_tg2:
    st.subheader("Why Use Our Telegram Bot?")
    st.markdown("""
    - **Instant Notifications**: Get real-time updates about your service requests
    - **Quick Submissions**: Submit new requests directly from Telegram
    - **Status Updates**: Check the status of pending requests with simple commands
    - **Event Reminders**: Receive reminders about upcoming community events
    - **24/7 Access**: Connect with the community system anytime, anywhere
    """)

# Role-specific features
if current_user:
    st.markdown("---")

    if user_role == "admin":
        st.header("👑 Admin Tools")
        st.markdown("""
        As an administrator, you have access to additional tools for managing the community:
        - Review and assign service requests
        - Manage serviceman schedules
        - Create community announcements
        - Generate service reports
        """)
        if st.button("Go to Admin Dashboard"):
            st.switch_page("pages/1_Admin_Dashboard.py")

    elif user_role == "serviceman":
        st.header("🛠️ Serviceman Tools")
        st.markdown("""
        As a service professional, you have access to:
        - View your assigned requests
        - Update job status
        - Schedule appointments
        - Access repair guidelines
        """)
        if st.button("View My Assignments"):
            st.switch_page("pages/2_Serviceman_View.py")

# Help & Support section
st.markdown("---")
st.header("ℹ️ Help & Support")

help_col1, help_col2 = st.columns(2)

with help_col1:
    st.subheader("Frequently Asked Questions")

    # Create expandable FAQ sections
    with st.expander("How do I submit a service request?"):
        st.write("""
        Navigate to the 'Submit Request' page from the sidebar. Fill in the details about your issue, 
        upload any relevant photos, and submit. You'll receive updates as your request is processed.
        """)

    with st.expander("How do I join a community event?"):
        st.write("""
        Go to the Community Board and navigate to the 'View Events' tab. Browse through upcoming events 
        and click the RSVP button for any event you'd like to attend.
        """)

    with st.expander("Can I use the system on my mobile phone?"):
        st.write("""
        Yes! Our web interface is mobile-friendly. Additionally, you can connect with our 
        Telegram bot for on-the-go access to key features.
        """)

with help_col2:
    st.subheader("Contact Support")

    with st.form("support_form"):
        support_issue = st.text_input("Subject")
        support_details = st.text_area("How can we help you?")
        support_submit = st.form_submit_button("Send Message")

        if support_submit and support_issue and support_details:
            # Save support request to database
            db["support_requests"].insert_one({
                "subject": support_issue,
                "details": support_details,
                "user": current_user if current_user else "Guest",
                "status": "New",
                "created_at": datetime.utcnow().isoformat()
            })
            st.success(
                "Your support request has been submitted. We'll get back to you soon.")

# Footer
st.markdown("---")
footer_col1, footer_col2 = st.columns(2)
with footer_col1:
    st.markdown("© 2025 KommunitiKonect. All rights reserved.")
with footer_col2:
    st.markdown("Built with ❤️ for better community living")
