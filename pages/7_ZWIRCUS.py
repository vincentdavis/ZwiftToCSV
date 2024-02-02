import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from zp import racer_results

c1, c2 = st.columns(2)
with c1:
    zwircus_image = Image.open('images/zwircus.png')
    st.image(zwircus_image, caption='Who are you racing')
with c2:
    st.write("## Zwircus")
    st.write("### Discover who you are racing on Zwift")
    st.write("This page is built for [zwircus.com](https://zwircus.com)")

st.write("#### WKG and Coggan Levels")
st.write("Paste the zwiftpower url for a rider below")
st.write("Example: https://zwiftpower.com/profile.php?zid=1234567890")
profile_url = st.text_input(label="PROFILE URL", placeholder="PROFILE URL")

if "https://zwiftpower.com/profile.php?z=" in profile_url:
    # Get the zwiftpower data
    st.write("Getting ZwiftPower data, wait for it.... Might take 5-10 seconds")
    results = racer_results(profile_url)
    df = results['results_df']
    gender_convert = {1: 'Male_WKG', 0: 'Female_WKG'}
    gender = gender_convert[df['male'].iloc[0]]

    cf = pd.read_csv('data/coggan_factors.csv')

    wkg_list = ['wkg_ftp', 'wkg1200', 'wkg300', 'wkg60', 'wkg30', 'wkg15', 'wkg5']  # did not include 'avg_wkg'
    x = [3600, 1200, 300, 60, 30, 15, 5]
    # colors = px.colors.qualitative.Plotly
    colors = px.colors.sequential.Greys

    # WKG and Coggan Levels

    # wkg_curve = px.area(cf, x="time", y=f"{gender}_WKG", color="Level", title="WKG and Coggan Levels")

    wkg_curve = go.Figure()
    wkg_curve.update_layout(title='WKG and Coggan Levels',
                            height=700,
                            )
    for i, w in enumerate(cf.Level.unique()):
        c = cf[cf.Level == w]
        wkg_curve.add_trace(go.Scatter(name=f"{w}", x=c['time'], y=c[gender], mode='lines', fill='tonexty',
                                       line_color=colors[-i]))
    wkg_max = {'wkg_ftp': 0, 'wkg1200': 0, 'wkg300': 0, 'wkg60': 0, 'wkg30': 0, 'wkg15': 0, 'wkg5': 0}
    wkg_max.update(df[wkg_list].max().to_dict())
    print(wkg_max)
    wkg_curve.add_trace(
        go.Scatter(name=f"Athlete's WKG", x=x, y=list(wkg_max.values()), mode='lines', line_color='blue'))
    st.plotly_chart(wkg_curve, theme="streamlit", use_container_width=True)

    # WKG and Coggan Levels

    for c in wkg_list:
        try:
            cmax = df[c].max()
        except Exception as e:
            cmax = 0
            print(e)
        st.write(f"{c} max value: {cmax}")

    # #### Historical WKG
    # wkg_hist = go.Figure()
    # wkg_hist.update_layout(
    #     title='Historical WKG')
    # df_sorted = df.sort_values('event_date')
    # for c in wkg_list:
    #     wkg_curve.add_trace(
    #         go.Scatter(name=f"{c}", x=df_sorted['event_date'], y=df_sorted[c]))
    # st.plotly_chart(wkg_hist, theme="streamlit", use_container_width=False)

    # #### Historical WKG/HR
    # wkg_hr = go.Figure()
    # wkg_hr.update_layout(
    #     title='Historical WKG/HR')
    # for c in wkg_list:
    #     try:
    #         # print(df[[c, 'avg_hr']].dtypes)
    #         df[c] = df[c].replace('', np.nan)
    #         df[c] = df[c].astype(float)
    #         df_sorted = df[(df[c]>0) & (df['avg_hr']>0)].sort_values('event_date')
    #         df_sorted[f"{c}_hr"] = df_sorted[c] / df_sorted['avg_hr']
    #         wkg_hr.add_trace(
    #             go.Scatter(name=f"{c}", x=df_sorted['event_date'], y=df_sorted[f"{c}_hr"]))
    #     except Exception as e:
    #         print(e)
    #         print(f"Error with {c}")
    # st.plotly_chart(wkg_hr, theme="streamlit", use_container_width=False)

    for name in results.keys():
        if '_df' in name:
            with st.expander(f"Data from {name} api"):
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button(label="Download csv file",
                                       data=results[name].to_csv(index=False).encode('utf-8'),
                                       file_name=f"profile_id){results['profile_id']}_{name.replace('_df', '')}.csv",
                                       mime='text/csv')
                with c2:
                    st.download_button(label="Download json file",
                                       data=json.dumps(results[f"{name.replace('df', 'json')}"]).encode('utf-8'),
                                       file_name=f"profile_id){results['profile_id']}_{name.replace('_df', '')}.json",
                                       mime='text/json')
                st.dataframe(results[name])
