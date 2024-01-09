import streamlit as st
from requests_html import HTMLSession as Session

st.set_page_config(layout="wide")

"""
# Welcome to Vincent's experiments with cycling data files

This is a work in progress. Please report any issues at [pyfitness_streamlit](https://github.com/vincentdavis/pyfitness_streamlit)

You can also contact me on discord: [Vincent](discordapp.com/users/VincentDavis#3484)

This "dashboard" will look at the details of the FIT file 
and the distribution on the data. You are able to compare two file side by side.
"""
s = Session()
response = s.get("https://google.com/")
st.write("HTML output test")
st.write(response.html)
