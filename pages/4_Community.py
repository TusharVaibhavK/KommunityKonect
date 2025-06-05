# import streamlit as st
# from pymongo import MongoClient
# from datetime import datetime
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # MongoDB Setup
# client = MongoClient(os.getenv("MONGODB_URI"))
# db = client["kommuniti"]
# posts_col = db["community_posts"]
# events_col = db["community_events"]
# users_col = db["users"]

# # Get current logged-in user
# current_user = st.session_state.get("username", "demo_user")
# current_user_role = st.session_state.get("role", "resident")

# st.title("🏘️ Community Board")

# tab1, tab2, tab3 = st.tabs(["Create Event", "View Events", "Manage Invites"])

# with tab1:
#     with st.form("create_event"):
#         title = st.text_input("Event Title")
#         description = st.text_area("Description")
#         date = st.date_input("Date")
#         time = st.time_input("Time")
#         location = st.text_input("Location")
#         # Only show host selection for admins
#         if current_user_role == "admin":
#             all_users = [u["username"] for u in users_col.find(
#                 {}, {"username": 1}) if u.get("username")]
#             host = st.selectbox("Event Host", options=all_users, index=all_users.index(
#                 current_user) if current_user in all_users else 0)
#         else:
#             host = current_user

#         if st.form_submit_button("Create Event"):
#             if title and description and date:
#                 event_data = {
#                     "title": title,
#                     "description": description,
#                     "date": date.strftime("%Y-%m-%d"),
#                     "time": time.strftime("%H:%M"),
#                     "location": location,
#                     "host": host,
#                     "created_by": current_user,
#                     "created_at": datetime.utcnow().isoformat(),
#                     "attendees": [host],
#                     "status": "upcoming"
#                 }
#                 events_col.insert_one(event_data)
#                 st.success(f"Event '{title}' created successfully!")
#             else:
#                 st.error("Please fill in all required fields")

# with tab2:
#     st.subheader("Upcoming Community Events")

#     # Filter options
#     filter_col1, filter_col2 = st.columns(2)
#     with filter_col1:
#         filter_option = st.radio(
#             "Show events:", ["All events", "My events", "Events I'm attending"])
#     with filter_col2:
#         sort_by = st.selectbox(
#             "Sort by:", ["Date (newest first)", "Date (oldest first)", "Title (A-Z)"])

#     # Apply filters and sorting
#     query = {}
#     if filter_option == "My events":
#         query["host"] = current_user
#     elif filter_option == "Events I'm attending":
#         query["attendees"] = current_user

#     # Apply sorting
#     sort_field = "date"
#     sort_direction = -1
#     if sort_by == "Date (oldest first)":
#         sort_direction = 1
#     elif sort_by == "Title (A-Z)":
#         sort_field = "title"
#         sort_direction = 1

#     events = events_col.find(query).sort(sort_field, sort_direction)

#     # Display events
#     event_count = 0
#     for event in events:
#         event_count += 1
#         with st.expander(f"{event['title']} - {event['date']} at {event.get('time', 'TBD')}"):
#             st.write(f"**Description:** {event['description']}")
#             st.write(f"**Location:** {event.get('location', 'TBD')}")
#             st.write(f"**Host:** {event['host']}")
#             st.write(f"**Attendees:** {', '.join(event.get('attendees', []))}")

#             # RSVP button
#             if current_user not in event.get('attendees', []):
#                 if st.button(f"RSVP to '{event['title']}'", key=f"rsvp_{event['_id']}"):
#                     events_col.update_one(
#                         {"_id": event["_id"]},
#                         {"$addToSet": {"attendees": current_user}}
#                     )
#                     st.success(f"You've RSVP'd to '{event['title']}'!")
#                     st.experimental_rerun()
#             else:
#                 if st.button(f"Cancel RSVP to '{event['title']}'", key=f"cancel_{event['_id']}"):
#                     events_col.update_one(
#                         {"_id": event["_id"]},
#                         {"$pull": {"attendees": current_user}}
#                     )
#                     st.success(
#                         f"You've cancelled your RSVP to '{event['title']}'")
#                     st.experimental_rerun()

#     if event_count == 0:
#         st.info("No events found based on your filter.")

# with tab3:
#     st.subheader("Your Event Invitations")

#     # Get events you're invited to but haven't RSVP'd
#     invites = events_col.find({"attendees": {"$ne": current_user}})

#     invite_count = 0
#     for invite in invites:
#         invite_count += 1
#         st.write(
#             f"**{invite['title']}** - {invite['date']} at {invite.get('time', 'TBD')}")
#         st.write(f"Host: {invite['host']}")
#         st.write(f"Description: {invite['description']}")

#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button(f"Accept", key=f"accept_{invite['_id']}"):
#                 events_col.update_one(
#                     {"_id": invite["_id"]},
#                     {"$addToSet": {"attendees": current_user}}
#                 )
#                 st.success(
#                     f"You've accepted the invitation to '{invite['title']}'!")
#                 st.experimental_rerun()
#         with col2:
#             if st.button(f"Decline", key=f"decline_{invite['_id']}"):
#                 st.info(
#                     f"You've declined the invitation to '{invite['title']}'")

#     if invite_count == 0:
#         st.info("You have no pending event invitations.")

# st.markdown("---")

# # --- Post Creation ---
# st.subheader("📢 Create a Community Post")
# with st.form("post_form"):
#     title = st.text_input("Title")
#     content = st.text_area("Content")

#     all_users = [u["username"] for u in users_col.find(
#         {}, {"username": 1}) if u.get("username") and u["username"] != current_user]
#     invited = st.multiselect("Invite Residents", options=all_users)

#     submitted = st.form_submit_button("Post")
#     if submitted and title and content:
#         posts_col.insert_one({
#             "author": current_user,
#             "title": title,
#             "content": content,
#             "timestamp": datetime.utcnow().isoformat(),
#             "invited_users": invited,
#             "likes": 0,
#             "liked_by": []
#         })
#         st.success("Post created and invites sent!")

# st.markdown("---")

# # --- Feed ---
# st.subheader("📰 Community Feed")

# # Filter and sort options
# col1, col2 = st.columns(2)
# with col1:
#     feed_filter = st.selectbox(
#         "Show posts:", ["All posts", "My posts", "Posts I'm invited to"])
# with col2:
#     feed_sort = st.selectbox(
#         "Sort by:", ["Newest first", "Oldest first", "Most liked"])

# # Apply filter
# query = {}
# if feed_filter == "My posts":
#     query["author"] = current_user
# elif feed_filter == "Posts I'm invited to":
#     query["invited_users"] = current_user

# # Apply sort
# sort_field = "timestamp"
# sort_dir = -1
# if feed_sort == "Oldest first":
#     sort_dir = 1
# elif feed_sort == "Most liked":
#     sort_field = "likes"
#     sort_dir = -1

# posts = posts_col.find(query).sort(sort_field, sort_dir)

# # Display posts
# post_count = 0
# for post in posts:
#     post_count += 1
#     with st.container():
#         title_col, like_col = st.columns([4, 1])
#         with title_col:
#             st.markdown(f"**{post['title']}**")
#         with like_col:
#             like_count = post.get('likes', 0)
#             already_liked = current_user in post.get('liked_by', [])
#             like_button_label = "❤️" if already_liked else "🤍"
#             if st.button(f"{like_button_label} {like_count}", key=f"like_{post['_id']}"):
#                 if already_liked:
#                     posts_col.update_one(
#                         {"_id": post["_id"]},
#                         {"$pull": {"liked_by": current_user}, "$inc": {"likes": -1}}
#                     )
#                 else:
#                     posts_col.update_one(
#                         {"_id": post["_id"]},
#                         {"$addToSet": {"liked_by": current_user}, "$inc": {"likes": 1}}
#                     )
#                 st.experimental_rerun()

#         st.caption(
#             f"by `{post['author']}` at {post['timestamp'][:19].replace('T', ' ')}")
#         st.write(post['content'])
#         if post.get("invited_users"):
#             st.info(f"Invited: {', '.join(post['invited_users'])}")
#         st.markdown("---")

# if post_count == 0:
#     st.info("No posts found based on your filter.")

import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["kommuniti"]
posts_col = db["community_posts"]
events_col = db["community_events"]
users_col = db["users"]

# Get current logged-in user
current_user = st.session_state.get("username", "demo_user")
current_user_role = st.session_state.get("role", "resident")

st.title("🏘️ Community Board")

# Add a 4th tab for Community Posts
tab1, tab2, tab3, tab4 = st.tabs(
    ["Create Event", "View Events", "Manage Invites", "Community Posts"])

with tab1:
    with st.form("create_event"):
        title = st.text_input("Event Title")
        description = st.text_area("Description")
        date = st.date_input("Date")
        time = st.time_input("Time")
        location = st.text_input("Location")
        # Only show host selection for admins
        if current_user_role == "admin":
            all_users = [u["username"] for u in users_col.find(
                {}, {"username": 1}) if u.get("username")]
            host = st.selectbox("Event Host", options=all_users, index=all_users.index(
                current_user) if current_user in all_users else 0)
        else:
            host = current_user

        if st.form_submit_button("Create Event"):
            if title and description and date:
                event_data = {
                    "title": title,
                    "description": description,
                    "date": date.strftime("%Y-%m-%d"),
                    "time": time.strftime("%H:%M"),
                    "location": location,
                    "host": host,
                    "created_by": current_user,
                    "created_at": datetime.utcnow().isoformat(),
                    "attendees": [host],
                    "status": "upcoming"
                }
                events_col.insert_one(event_data)
                st.success(f"Event '{title}' created successfully!")
            else:
                st.error("Please fill in all required fields")

with tab2:
    st.subheader("Upcoming Community Events")

    # Filter options
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_option = st.radio(
            "Show events:", ["All events", "My events", "Events I'm attending"])
    with filter_col2:
        sort_by = st.selectbox(
            "Sort by:", ["Date (newest first)", "Date (oldest first)", "Title (A-Z)"])

    # Apply filters and sorting
    query = {}
    if filter_option == "My events":
        query["host"] = current_user
    elif filter_option == "Events I'm attending":
        query["attendees"] = current_user

    # Apply sorting
    sort_field = "date"
    sort_direction = -1
    if sort_by == "Date (oldest first)":
        sort_direction = 1
    elif sort_by == "Title (A-Z)":
        sort_field = "title"
        sort_direction = 1

    events = events_col.find(query).sort(sort_field, sort_direction)

    # Display events
    event_count = 0
    for event in events:
        event_count += 1
        with st.expander(f"{event['title']} - {event['date']} at {event.get('time', 'TBD')}"):
            st.write(f"**Description:** {event['description']}")
            st.write(f"**Location:** {event.get('location', 'TBD')}")
            st.write(f"**Host:** {event['host']}")
            st.write(f"**Attendees:** {', '.join(event.get('attendees', []))}")

            # RSVP button
            if current_user not in event.get('attendees', []):
                if st.button(f"RSVP to '{event['title']}'", key=f"rsvp_{event['_id']}"):
                    events_col.update_one(
                        {"_id": event["_id"]},
                        {"$addToSet": {"attendees": current_user}}
                    )
                    st.success(f"You've RSVP'd to '{event['title']}'!")
                    st.experimental_rerun()
            else:
                if st.button(f"Cancel RSVP to '{event['title']}'", key=f"cancel_{event['_id']}"):
                    events_col.update_one(
                        {"_id": event["_id"]},
                        {"$pull": {"attendees": current_user}}
                    )
                    st.success(
                        f"You've cancelled your RSVP to '{event['title']}'")
                    st.experimental_rerun()

    if event_count == 0:
        st.info("No events found based on your filter.")

with tab3:
    st.subheader("Your Event Invitations")

    # Get events you're invited to but haven't RSVP'd
    invites = events_col.find({"attendees": {"$ne": current_user}})

    invite_count = 0
    for invite in invites:
        invite_count += 1
        st.write(
            f"**{invite['title']}** - {invite['date']} at {invite.get('time', 'TBD')}")
        st.write(f"Host: {invite['host']}")
        st.write(f"Description: {invite['description']}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Accept", key=f"accept_{invite['_id']}"):
                events_col.update_one(
                    {"_id": invite["_id"]},
                    {"$addToSet": {"attendees": current_user}}
                )
                st.success(
                    f"You've accepted the invitation to '{invite['title']}'!")
                st.experimental_rerun()
        with col2:
            if st.button(f"Decline", key=f"decline_{invite['_id']}"):
                st.info(
                    f"You've declined the invitation to '{invite['title']}'")

    if invite_count == 0:
        st.info("You have no pending event invitations.")

# Move community posts to tab4
with tab4:
    # Post Creation - moved inside tab4
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
                "invited_users": invited,
                "likes": 0,
                "liked_by": []
            })
            st.success("Post created and invites sent!")

    st.markdown("---")

    # Feed section
    st.subheader("📰 Community Feed")

    # Filter and sort options
    col1, col2 = st.columns(2)
    with col1:
        feed_filter = st.selectbox(
            "Show posts:", ["All posts", "My posts", "Posts I'm invited to"])
    with col2:
        feed_sort = st.selectbox(
            "Sort by:", ["Newest first", "Oldest first", "Most liked"])

    # Apply filter
    query = {}
    if feed_filter == "My posts":
        query["author"] = current_user
    elif feed_filter == "Posts I'm invited to":
        query["invited_users"] = current_user

    # Apply sort
    sort_field = "timestamp"
    sort_dir = -1
    if feed_sort == "Oldest first":
        sort_dir = 1
    elif feed_sort == "Most liked":
        sort_field = "likes"
        sort_dir = -1

    posts = posts_col.find(query).sort(sort_field, sort_dir)

    # Display posts
    post_count = 0
    for post in posts:
        post_count += 1
        with st.container():
            title_col, like_col = st.columns([4, 1])
            with title_col:
                st.markdown(f"**{post['title']}**")
            with like_col:
                like_count = post.get('likes', 0)
                already_liked = current_user in post.get('liked_by', [])
                like_button_label = "❤️" if already_liked else "🤍"
                if st.button(f"{like_button_label} {like_count}", key=f"like_{post['_id']}"):
                    if already_liked:
                        posts_col.update_one(
                            {"_id": post["_id"]},
                            {"$pull": {"liked_by": current_user},
                                "$inc": {"likes": -1}}
                        )
                    else:
                        posts_col.update_one(
                            {"_id": post["_id"]},
                            {"$addToSet": {"liked_by": current_user},
                                "$inc": {"likes": 1}}
                        )
                    st.experimental_rerun()  # Added this back to refresh after liking

            st.caption(
                f"by `{post['author']}` at {post['timestamp'][:19].replace('T', ' ')}")
            st.write(post['content'])
            if post.get("invited_users"):
                st.info(f"Invited: {', '.join(post['invited_users'])}")
            st.markdown("---")

    if post_count == 0:
        st.info("No posts found based on your filter.")
