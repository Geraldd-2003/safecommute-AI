"""
SafeCommute AI - local web app (Streamlit)
==========================================
Run:  streamlit run app.py

This file draws the shared sidebar (dataset + matching rules), runs the matching
once, and hands the result to the page the user opened (folder views/).
The matching logic lives in engine.py, which has no UI code.
"""

import streamlit as st

from ui import state, style

st.set_page_config(page_title="SafeCommute AI", page_icon=":material/nights_stay:", layout="wide",
                   initial_sidebar_state="expanded")
style.apply()

PAGES = [
    st.Page("views/home.py", title="Home", icon=":material/home:", default=True),
    st.Page("views/find.py", title="Find my group", icon=":material/group_add:"),
    st.Page("views/dashboard.py", title="Dashboard", icon=":material/monitoring:"),
    st.Page("views/calibration.py", title="Calibration", icon=":material/tune:"),
    st.Page("views/data.py", title="Data", icon=":material/table_view:"),
    st.Page("views/about.py", title="About", icon=":material/info:"),
]
nav = st.navigation(PAGES, position="top")

st.logo(str(state.APP_DIR / "assets" / "logo.svg"), size="large")
with st.sidebar:
    st.caption("Never walk home alone after a late train.")

context = state.build_context()
if context is None:
    st.stop()
st.session_state["ctx"] = context
nav.run()
