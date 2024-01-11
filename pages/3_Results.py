import logging

import pandas as pd
import streamlit as st

from zp_fetch import ZPSession, flatten_row

st.set_page_config(page_title="Zwift to CSV")

"""
# Zwift to CSV utility

If you have questions or feature request, DM me at [Vincent](discordapp.com/users/vincent.davis)

The form below allows you to get the api data from a zwiftpower team page.
You mist be the team admin to the list of pending riders.
- Events: list of upcoming events
- Results: Resylts tabe on the main events page.
- History: History tab on the main event page. About 1 month of data
- Event ZP data: This is the ZwiftPower event results date.
- Event ZW data: This is the Zwift event results data.
- Event Sprints: Sprints and KOMs.
- Event Primes: This is the primes data, note this has options.
- Event URL: only needed for event results
"""

st.write("Login to ZwiftPower using your Zwift account, account info is not stored.")

with st.form(key="Team Data request"):
    username = st.text_input(label="UserName", placeholder="username")
    password = st.text_input(label="Password", placeholder="password")
    data_req = st.radio(
        label="Choose one",
        options=["Events", "Results", "History", "Event ZP data", "Event ZW data", "Event Sprints", "Event Primes"],
    )
    url = st.text_input(label="Event URL", placeholder="https://zwiftpower.com/events.php?zid=12345")
    st.write("These options are only apply to Primes data")
    cat = st.radio(label="Category", options=["ALL", "A", "B", "C", "D", "E"])
    format = st.radio(label="Format", options=["msec", "elapsed"])
    submit_button = st.form_submit_button(label="Submit")

if submit_button:
    with st.spinner("Processing..."):
        if "Event " in data_req and "https://zwiftpower.com/events.php?zid=" not in url:
            st.error("Please enter a valid Event URL")
        if username is None or password is None:
            st.error("Please enter a valid username and password")
        id = url.split("=")[-1]
        zps = ZPSession(login_data={"username": username, "password": password})
        if data_req == "Events":
            logging.info("Get events data from")
            data = zps.get_api(id=id, api="all_events")["all_events"]["data"]
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="Events.csv",
                mime="text/csv",
            )
            st.dataframe(df)
        elif data_req == "Results":
            logging.info("Get results data from")
            data = zps.get_api(id=id, api="all_results")["all_results"]["data"]
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="Results.csv",
                mime="text/csv",
            )
            st.dataframe(df)
        elif data_req == "History":
            logging.info("Get history data from")
            data = zps.get_api(id=id, api="event_race_history")["event_race_history"]["data"]
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="History.csv",
                mime="text/csv",
            )
            st.dataframe(df)
        elif data_req == "Event ZP data":
            logging.info("Get event data from")
            data = zps.get_api(id=id, api="event_results_view")["event_results_view"]["data"]
            for row in data:
                row.update(flatten_row(row))
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"Event_{id}.csv",
                mime="text/csv",
            )
            st.dataframe(df)
        elif data_req == "Event ZW data":
            logging.info("Get event data from")
            data = zps.get_api(id=id, api="event_results_zwift")["event_results_zwift"]["data"]
            for row in data:
                row.update(flatten_row(row))
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"Event_{id}.csv",
                mime="text/csv",
            )
            st.dataframe(df)
        elif data_req == "Event Sprints":
            logging.info("Get event data from")
            data = zps.get_api(id=id, api="event_sprints")["event_sprints"]["data"]
            for row in data:
                row.update(flatten_row(row))
            df = pd.DataFrame(data)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"Sprints_{id}.csv",
                mime="text/csv",
            )
            st.dataframe(df)
        elif data_req == "Event Primes":
            cat = cat.replace("ALL", "")
            df = zps.get_primes_from_url(url, cat, format)
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"Event_prime_{id}_CAT_{cat}_FORMAT_{format}.csv",
                mime="text/csv",
            )
            st.dataframe(df)
