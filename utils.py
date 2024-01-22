import streamlit as st
def check_login(username, password):
    try:
        assert username and password
    except AssertionError as e:
        st.exception("Please enter a valid username and password")
        raise e