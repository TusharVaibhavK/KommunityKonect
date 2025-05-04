import streamlit as st

st.title("🎉 Community Concierge")

option = st.selectbox("What do you want to do?", [
                      "Create Event", "View Events"])

if option == "Create Event":
    st.components.v1.iframe(
        "https://your-flowise-instance.com/public/flow/community-concierge", height=700)
else:
    # Read from MongoDB and display events (can use PyMongo)
    pass
