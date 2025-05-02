# kommuniti_app/pages/Home.py
import streamlit as st
from pages.Layout import layout  # Import the shared layout

# Call the layout function to make logout available
layout()

# Add your main page content
st.title("Welcome to Kommuniti!")
st.write("This is the home page of your application.")