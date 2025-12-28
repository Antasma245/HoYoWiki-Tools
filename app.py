import streamlit as st


home = st.Page(
    "pages/home.py",
    title = "HoYoWiki-Tools",
    icon = ":material/home:",
    default = True
)

pgc_creator = st.Page(
    "pages/pgc_creator.py",
    title = "PGC Creator",
    icon = ":material/table_edit:"
)

quest_formatter = st.Page(
    "pages/quest_formatter.py",
    title = "Quest Formatter",
    icon = ":material/chat_paste_go:"
)

wet_colorizer = st.Page(
    "pages/wet_colorizer.py",
    title = "WET Colorizer",
    icon = ":material/format_color_fill:"
)

about = st.Page(
    "pages/about.py",
    title = "About this app",
    icon = ":material/info:"
)

pg = st.navigation(
    {
        "Home": [home],
        "Tools": [pgc_creator, quest_formatter, wet_colorizer],
        "Information": [about]
    }
)

pg.run()