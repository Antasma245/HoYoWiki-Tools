import streamlit as st


home = st.Page(
    "pages/home.py",
    title = "HoYoWiki-Tools",
    icon = ":material/home:",
    default = True
)

about = st.Page(
    "pages/about.py",
    title = "About this app",
    icon = ":material/info:"
)

pg = st.navigation(
    {
        "Home": [home],
        "Information": [about]
    }
)

pg.run()