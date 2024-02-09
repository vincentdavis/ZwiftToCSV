import logging

import pandas as pd
import streamlit as st

from utils import download_data
from zr import CATS, SORTBY, expand_elo_columns, get_elo

st.set_page_config(page_title="Zwift Racing app")
"""
# Zwift to CSV utility

### get data from zwiftracing.app
- https://www.zwiftracing.app/rankings/open

If you have questions or feature request, DM me at [vincent.davis](discordapp.com/users/vincent.davis)


"""

SORT_DIR = {"Descending": "desc", "Ascending": "asc"}

st.write("Login to ZwiftPower using your Zwift account. No data is stored.")

with st.form(key="zr"):
    st.markdown("#### vELO raking and points data")
    cat = st.radio(
        label="Category",
        options=CATS,
    )
    pagesize = st.number_input(label="Number of rows (see ALL option)", min_value=1, max_value=1000, value=50)
    sortby = st.radio(label="Sort by", options=SORTBY)
    sortdirection = st.radio(label="Sort order", options=["Descending", "Ascending"])
    gender = st.radio(label="Gender", options=["Both", "M", "F"])
    all_pages = st.checkbox(label="Get ALL rows (pages)", value=False)
    submit = st.form_submit_button(label="Submit")

logging.info(f"Main Form {submit}")

if submit:
    with st.spinner("Processing..."):
        sortdirection = SORT_DIR[sortdirection]
        if gender == "Both":
            gender = ""
        page = 0
        data = get_elo(all_pages, cat, pagesize, sortby, sortdirection, page, gender)
        df = pd.DataFrame.from_dict(data)
        df = expand_elo_columns(df)
        download_data(df, data)
        st.dataframe(df)
