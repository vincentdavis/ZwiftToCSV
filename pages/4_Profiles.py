import logging

import pandas as pd
import streamlit as st

from utils import check_login, flatten_row
from zp_fetch import ZPSession

st.set_page_config(page_title="Zwift to CSV")

"""
# Zwift to CSV utility

If you have questions or feature request, DM me at [Vincent](discordapp.com/users/vincent.davis)
"""
st.write("Login to ZwiftPower using your Zwift account. user info is not stored.")

with st.form(key="Team Data request"):
    username = st.text_input(label="UserName", placeholder="username")
    password = st.text_input(label="Password", placeholder="password")
    data_req = st.radio(
        label="Choose one",
        options=["Main Profile", "Victims", "Signups"],
    )
    url = st.text_input(label="Profile URL", placeholder="https://zwiftpower.com/profile.php?z=123456")
    submit_button = st.form_submit_button(label="Submit")

if submit_button:
    with st.spinner("Processing..."):
        check_login(username, password)
        if "https://zwiftpower.com/profile.php?z=" not in url:
            st.exception("Please enter a valid Profile URL")
        id = url.split("=")[-1]
        zps = ZPSession(login_data={"username": username, "password": password})
        if data_req == "Main Profile":
            logging.info(f"Get rider records data from: {username}")
            data = zps.get_api(id=id, api="profile_profile")["profile_profile"]["data"]
            for row in data:
                row.update(flatten_row(row))
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="Rider_records.csv",
                mime="text/csv",
            )
            st.dataframe(df)
        elif data_req == "Victims":
            logging.info("Get team standings data from:")
            data = zps.get_api(id=id, api="profile_victims")["profile_victims"]["data"]
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="Team_standings.csv",
                mime="text/csv",
            )
            st.dataframe(df)
        elif data_req == "Signups":
            logging.info("Get team standings data from:")
            data = zps.get_api(id=id, api="profile_signups")["profile_signups"]["data"]
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="Team_standings.csv",
                mime="text/csv",
            )
            st.dataframe(df)
