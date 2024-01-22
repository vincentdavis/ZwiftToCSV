import logging

import pandas as pd
import streamlit as st

from utils import check_login
from zp_fetch import ZPSession, flatten_row, flatten_dict
from zw_fetch import API_OPTIONS, ZwiftAPIClient

st.set_page_config(page_title="Zwift to CSV")
"""
# Zwift to CSV utility

If you have questions or feature request, DM me at [vincent.davis](discordapp.com/users/vincent.davis)

The form below allows you to get the api data from a zwiftpower team page.
You mist be the team admin to the list of pending riders.
"""

st.write("Login to ZwiftPower using your Zwift account. No data is stored.")

with st.form(key="Team Data request"):
    username = st.text_input(label="UserName", placeholder="username")
    password = st.text_input(label="Password", placeholder="password")
    data_req = st.radio(
        label="Choose data API to fetch",
        options=API_OPTIONS,
    )
    submit_button = st.form_submit_button(label="Submit")

if submit_button:
    with st.spinner("Processing..."):
        check_login(username, password)
        zps = ZwiftAPIClient(username, password)
        if data_req == "Me":
            logging.info(f"Getting {data_req}")
            data = zps.get_profile()
            data = flatten_dict(data)
            df = pd.DataFrame.from_dict(data, orient="index", columns=["value"])
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="Team_riders.csv",
                mime="text/csv",
            )
            st.dataframe(df)
        elif data_req != "Me":
            logging.info(f"Not yet implemented")
            st.exception("Not yet implemented")
            # st.download_button(
            #     label="Download csv file",
            #     data=df.to_csv(index=False).encode("utf-8"),
            #     file_name="Team_pending.csv",
            #     mime="text/csv",
            # )
            # st.dataframe(df)

