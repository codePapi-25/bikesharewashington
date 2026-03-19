import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to Bike Share App Washington! 👋")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    If you are a user looking to rent or return a bike, select User.
    
    If you are a mechanic looking to repair bikes and docks, select Mechanics.
"""
)