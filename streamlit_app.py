import streamlit as st

st.set_page_config(page_title="Zwift to CSV")
pg = st.navigation(
    [
        st.Page("app_pages/Zwift2CSV.py", title="Zwift to CSV"),
        st.Page("app_pages/2_Team_Data.py", title="Team Data"),
        st.Page("app_pages/3_Results.py", title="Events, Result Data"),
        st.Page("app_pages/4_Profiles.py", title="Profiles"),
        st.Page("app_pages/5_Zwift.py", title="Zwift"),
        st.Page("app_pages/6_Misc.py", title="Misc"),
        # st.Page("app_pages/7_ZWIRCUS.py", title="ZWIRCUS"),
        st.Page("app_pages/8_ZwiftRacing.py", title="ZwiftRacing"),
    ]
)
pg.run()
