import logging

import pandas as pd
import streamlit as st

from utils import check_login, download_data, flatten_row, flatten_dict
from zp_fetch import ZPSession
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
    st.text("Choose your activity feed options")
    zwid = st.text_input(label='blank for yourself or ZWID', placeholder="[blank] or 12345")
    main_submit = st.form_submit_button(label="Submit")
logging.info(f"Main Form {main_submit}")

if main_submit:
    with st.spinner("Processing..."):
        check_login(username, password)
        zps = ZwiftAPIClient(username, password)
        if data_req == "Me":
            logging.info(f"Getting {data_req}")
            data = zps.get_profile()
            data_flat = flatten_dict(data)
            df = pd.DataFrame.from_dict(data_flat, orient="index", columns=["value"])
            download_data(df, data)
            st.dataframe(df)
        elif data_req == "My Clubs":
            logging.info(f"Getting My Clubs")
            data = zps.get_my_clubs()
            data_flat = flatten_dict(data)
            df = pd.DataFrame.from_dict(data_flat, orient="index", columns=["value"])
            download_data(df, data)
            st.dataframe(df)
        elif "Power Profile" in data_req:
            logging.info(f"Getting Power Profile")
            data = zps.get_power_profile()
            print(data)
            data_flat = flatten_dict(data)
            df = pd.DataFrame.from_dict(data, orient="index", columns=["value"])
            download_data(df, data)
            st.dataframe(df)
        elif "Activity Feeds" in data_req:
            logging.info(f"Activity Feed options form")
            if not zwid:
                zwid = zps.get_profile()["id"]
            try:
                zwid = int(zwid)
                assert zwid <= 999999999
            except ValueError:
                st.exception("zwid must be an integer or leave it blank for yourself")
            logging.info(f"get Activity Feed {zwid}")
            data = zps.get_activities(zwid)
            df = pd.DataFrame.from_dict(data)
            download_data(df, data)
            st.dataframe(df)

