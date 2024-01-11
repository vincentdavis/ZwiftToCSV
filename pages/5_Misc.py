import logging

import pandas as pd
import streamlit as st

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
        options=["Rider Records", "Team Standings"],
    )
    submit_button = st.form_submit_button(label="Submit")

if submit_button:
    with st.spinner("Processing..."):
        if username is None or password is None:
            st.error("Please enter a valid username and password")
        zps = ZPSession(login_data={"username": username, "password": password})
        if data_req == "Rider Records":
            id = None
            logging.info(f"Get rider records data from: {username}")
            data = zps.get_api(id=id, api="rider_records")["rider_records"]["data"]
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="Rider_records.csv",
                mime="text/csv",
            )
            st.dataframe(df)
        elif data_req == "Team Standings":
            logging.info("Get team standings data from:")
            id = None
            data = zps.get_api(id=id, api="team_standings")["team_standings"]["data"]
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="Team_standings.csv",
                mime="text/csv",
            )
            st.dataframe(df)
