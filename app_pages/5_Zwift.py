import json
import logging
import zipfile
import io

import pandas as pd
import streamlit as st

from utils import check_login, download_data, flatten_dict, activity_date_parse
from zw_fetch import API_OPTIONS, ZwiftAPIClient, parse_url_or_id

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
    activity_id = st.text_input(label="Activity id or url", placeholder="[12345] or https://www.zwift.com/activity/1234567899)")
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

            case str() if "Download FIT" in data_req:
                logging.info("Getting fit file")
                if not zwid  and not activity_id:
                    st.error("zwid and activity_id are required to download fit file")
                zwid = parse_url_or_id(zwid)
                activity_id = parse_url_or_id(activity_id)
                fit_data = zps.get_activity_fit(zwid=zwid, activity=activity_id)
                st.download_button(
                    label="Download FIT file",
                    data=fit_data,
                    file_name=f"zwid_{zwid}_activity_{activity_id}.FIT",
                    mime="application/octet-stream",
                    key="FIT_file",
                )

            case str() if "Download graph Activity data" in data_req:
                logging.info("Download graph Activity data")
                if not zwid  and not activity_id:
                    st.error("zwid and activity_id are required to download fit file")
                zwid = parse_url_or_id(zwid)
                activity_id = parse_url_or_id(activity_id)
                full_data, small_data, activity = zps.get_activity_data_url(zwid=zwid, activity=activity_id)
                other_data = activity["profile"]
                other_data.update({"startDate": activity["startDate"]})
                if full_data:
                    df_full_data = activity_date_parse(full_data, other_data)
                    download_data(df_full_data, full_data, file_name=f"zwid_{zwid}_activity_{activity_id}", key=1)

                if small_data:
                    df_small_data = activity_date_parse(small_data, other_data)

                    download_data(df_small_data, small_data, key=2)
                if not full_data and not small_data:
                    st.error("No data found")

            case str() if "Download ALL event rider graph data" in data_req:
                logging.info(f"Start Get Event rider data: {event_id}")
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
                riders_data = dict()
                for sg_id in eventSubgroups_ids:
                    results_json = zps.get_event_subgroup_results(sg_id)["entries"]
                    for entry in results_json:
                        activity_id = entry["activityData"]["activityId"]
                        zwid = entry["profileId"]
                        try:
                            full_data, small_data, activity = zps.get_activity_data_url(zwid=zwid, activity=activity_id)
                            other_data = activity["profile"]
                            other_data.update({"startDate": activity["startDate"]})
                            if full_data:
                                df_full_data = activity_date_parse(full_data, other_data)
                                riders_data.update({f"{zwid}_full": df_full_data})
                            if small_data:
                                df_small_data = activity_date_parse(small_data, other_data)
                                riders_data.update({f"{zwid}_small": df_small_data})
                        except Exception as e:
                            logging.error(f"Error getting fit file for activity {activity_id}: {e}")

                    if riders_data:
                        with io.BytesIO() as output:
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                for sheet_name, df in riders_data.items():
                                    df.to_excel(writer, sheet_name=sheet_name[:31],
                                                index=False)  # Truncate name to Excel's 31-char limit

                            output.seek(0)
                            st.download_button(
                                label="Download Excel file",
                                data=output,
                                file_name=f"event_{event_id}_{sg_id}_riders_data.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"riders_data_excel_{sg_id}"
                            )




            # case str() if "Download CSV of FIT file" in data_req:
            #     logging.info("Getting fit file")
            #     if not zwid  and not activity_id:
            #         st.error("zwid and activity_id are required to download fit file")
            #     zwid = parse_url_or_id(zwid)
            #     activity_id = parse_url_or_id(activity_id)
            #     fit_data = zps.get_activity_file( zwid=zwid, activity=activity_id)
            #     df = pd.read_csv(fit_data)
            #     st.dataframe(df)

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
            case "Private Event":
                logging.info(f"Start Get private Event Data: {event_id}")
                if "https://www.zwift.com/events/view/" in event_id:
                    event_id = event_id.split("/")[-1]
                try:
                    event_id = int(event_id)
                    assert event_id <= 999999999 and event_id > 0
                except ValueError:
                    st.exception(f"event_id error, got {event_id}")
                logging.info(f"get Event data {event_id}")
                data = zps.get_private_event(event_id)
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
