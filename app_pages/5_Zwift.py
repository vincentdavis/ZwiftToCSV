import logging

import pandas as pd
import streamlit as st

from utils import check_login, download_data, flatten_dict
from zw_fetch import API_OPTIONS, ZwiftAPIClient

# st.set_page_config(page_title="Zwift to CSV")
"""
# Zwift to CSV utility

If you have questions or feature request, DM me at [vincent.davis](discordapp.com/users/vincent.davis)

The form below allows you to get the api data from a zwiftpower team page.
You mist be the team admin to the list of pending riders.
"""

st.write("Login to your Zwift account. No data is stored.")

with st.form(key="Zwift Data request"):
    username = st.text_input(label="UserName", placeholder="username")
    password = st.text_input(label="Password", placeholder="password", type="password")
    data_req = st.radio(
        label="Choose data API to fetch",
        options=API_OPTIONS,
    )
    st.markdown("- For activity and profiles fill this field.")
    zwid = st.text_input(label="Zwift id (ZWID) or blank for yourself", placeholder="[blank] or 12345")
    st.markdown(
        "- For event data or results, enter event id (12345) or event url https://www.zwift.com/events/view/12345"
    )
    event_id = st.text_input(label="Event id or url ", placeholder="[12345] or https://www.zwift.com/events/view/12345")
    main_submit = st.form_submit_button(label="Submit")

logging.info(f"Main Form {main_submit}")

if main_submit:
    with st.spinner("Processing..."):
        check_login(username, password)
        zps = ZwiftAPIClient(username, password)
        match data_req:
            case "Me":
                logging.info(f"Getting {data_req}")
                data = zps.get_profile()
                data_flat = flatten_dict(data)
                # df = pd.DataFrame.from_dict(data_flat, orient="index", columns=["value"])
                # download_data(df, data)
                # st.dataframe(df)
            case "My Clubs":
                logging.info("Getting My Clubs")
                data = zps.get_my_clubs()
                data_flat = flatten_dict(data)
                df = pd.DataFrame.from_dict(data_flat, orient="index", columns=["value"])
                download_data(df, data)
                st.dataframe(df)
            case str() if "Power Profile" in data_req:
                logging.info("Getting Power Profile")
                data = zps.get_power_profile()
                print(data)
                data_flat = flatten_dict(data)
                df = pd.DataFrame.from_dict(data, orient="index", columns=["value"])
                download_data(df, data)
                st.dataframe(df)
            case str() if "Activity Feeds" in data_req:
                logging.info("Activity Feed options form")
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
            case "Event":
                logging.info(f"Start Get Event Data: {event_id}")
                if "https://www.zwift.com/events/view/" in event_id:
                    event_id = event_id.split("/")[-1]
                try:
                    event_id = int(event_id)
                    assert event_id <= 999999999 and event_id > 0
                except ValueError:
                    st.exception(f"event_id error, got {event_id}")
                logging.info(f"get Event data {event_id}")
                data = zps.get_event(event_id)
                df = pd.DataFrame.from_dict(data)
                download_data(data=data)
                st.json(data)
            case "Event Results":
                logging.info(f"Start Get Event Results: {event_id}")
                if "https://www.zwift.com/events/view/" in event_id:
                    event_id = event_id.split("/")[-1]
                try:
                    event_id = int(event_id)
                    assert 999999999 >= event_id > 0
                except ValueError:
                    st.exception(f"event_id error, got {event_id}")
                logging.info(f"get Event data {event_id}")
                event_json = zps.get_event(event_id)
                eventSubgroups_ids = [sg_id["id"] for sg_id in event_json["eventSubgroups"]]
                logging.info(f"get eventSubgroups_ids: {eventSubgroups_ids}")
                for sg_id in eventSubgroups_ids:
                    results_json = zps.get_event_subgroup_results(sg_id)["entries"]
                    results = [flatten_dict(row) for row in results_json]
                    df = pd.DataFrame(results)
                    st.text(f"event_{event_id}_subgroup_id_{sg_id}")
                    download_data(df=df, data=results_json, key=sg_id)
            case _:
                pass
