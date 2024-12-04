import logging

import pandas as pd
import streamlit as st

from utils import check_login, flatten_row
from zp_fetch import ZPSession

# st.set_page_config(page_title="Zwift to CSV")
"""
# Zwift to CSV utility

If you have questions or feature request, DM me at [Vincent](discordapp.com/users/vincent.davis)

The form below allows you to get the api data from a zwiftpower team page.
You must be the team admin to the list of pending riders.
"""

st.write("Login to ZwiftPower using your Zwift account. No data is stored.")

with st.form(key="Team Data request"):
    username = st.text_input(label="UserName", placeholder="username")
    password = st.text_input(label="Password", placeholder="password")
    data_req = st.radio(
        label="Choose the Team data",
        options=["Team riders and basic data", "Pending Riders (Admin)", "Recent Team Results"],
    )
    url = st.text_input(label="Team URL", placeholder="https://zwiftpower.com/team.php?id=12345")
    submit_button = st.form_submit_button(label="Submit")

if submit_button:
    with st.spinner("Processing..."):
        if "https://zwiftpower.com/team.php?id=" not in url:
            st.exception("Please enter a valid Team URL")
        check_login(username, password)
        id = url.split("=")[-1]
        zps = ZPSession(login_data={"username": username, "password": password})
        if data_req == "Team riders and basic data":
            logging.info(f"Get team riders data from: {url}")
            data = zps.get_api(id=id, api="team_riders")["team_riders"]["data"]
            for row in data:
                row.update(flatten_row(row))
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="Team_riders.csv",
                mime="text/csv",
            )
            st.dataframe(df)
        elif data_req == "Pending Riders":
            logging.info(f"Get pending riders data from: {url}")
            data = zps.get_api(id=id, api="team_pending")["team_pending"]["data"]
            for row in data:
                row.update(flatten_row(row))
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="Team_pending.csv",
                mime="text/csv",
            )
            st.dataframe(df)
        elif data_req == "Recent Team Results":
            logging.info(f"Get recent team results data from: {url}")
            data = zps.get_api(id=id, api="team_results")["team_results"]["data"]
            for row in data:
                row.update(flatten_row(row))
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="Team_results.csv",
                mime="text/csv",
            )
            st.dataframe(df)
