import streamlit as st
from st_pages import Page, show_pages

st.set_page_config(page_title="Zwift to CSV")
show_pages(
    [
        Page("streamlit_app.py", "Zwift to CSV", ""),
        Page("pages/2_Team_Data.py", "Team Data", ""),
        Page("pages/3_Results.py", "Events, Result Data", ""),
        Page("pages/4_Profiles.py", "Profiles", ""),
        Page("pages/5_Zwift.py", "Zwift", ""),
        Page("pages/6_Misc.py", "Misc", ""),
    ]
)

"""
### Zwift to CSV utility
- If you have questions, problems or feature request, DM on discord at [vincent.davis](discordapp.com/users/vincent.davis)
- See the menu on the left for options.
- Also checkout [PyFitness activity analysis tools](https://vincentdavis-pyfitness.streamlit.app)
"""
