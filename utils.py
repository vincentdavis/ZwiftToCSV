import json
import logging

import pandas as pd
import streamlit as st


def check_login(username: str, password: str) -> None:
    """
    :param username: The username provided by the user for login.
    :param password: The password provided by the user for login.
    :return: None
    """
    try:
        assert username and password
    except AssertionError:
        st.exception("Please enter a valid username and password")


def download_data(df: pd.DataFrame = None, data = None, file_name:str="Zwift_To_Csv_download", key: int = 1):
    """
    Download data as a CSV file.

    :param df: A pandas DataFrame object containing the data to be downloaded.
    :type df: pd.DataFrame
    :return: None
    """
    col1, col2 = st.columns(2)
    with col1:
        if df is not None:
            st.download_button(
                label="Download csv file",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"{file_name}.csv",
                mime="text/csv",
                key=f"{key}_csv",
            )
        else:
            st.text("no csv available")
    with col2:
        if data is not None:
            st.download_button(
                label="Download JSON file",
                data=json.dumps(data, indent=4),
                file_name=f"{file_name}.json",
                mime="text/csv",
                key=f"{key}_json",
            )
        else:
            st.text("no json available")


def flatten_row(row: dict) -> dict:
    """
    If the returned data is a list with sub lists or sub dicts, flatten it
    :param row:
    :return:
    """
    update_row = {}
    for k, v in row.items():
        try:
            if isinstance(v, list) and len(v) == 2:
                update_row[f"{k}"] = v[0]
                update_row[f"{k}_1"] = v[1]
        except:
            logging.info(k, v)
    return update_row


def flatten_dict(data):
    """If the returned data is a top level dict"""
    flat_dict = {}
    for k, v in data.items():
        if isinstance(v, dict):
            flat_dict.update(flatten_dict(v))  # Recursively flatten sub-dictionaries
        else:
            flat_dict[k] = v  # Add non-dictionary values directly
    return flat_dict

def activity_date_parse(data:dict, other:dict=None)->pd.DataFrame:
    """Parse the small and large data url.
    other is used to add the activity_id, activity_name, and activity_date to the data..
    Anything that is constant down the rows."""

    data["latitude"]=[coord[0] if coord else None for coord in data['latlng']]
    data["longitude"]=[coord[1] if coord else None for coord in data['latlng']]
    data.pop('latlng')
    df = pd.DataFrame(data)
    for k, v in other.items():
        df[k] = v
    return df



