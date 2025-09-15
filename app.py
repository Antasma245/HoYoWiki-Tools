import streamlit as st


home = st.Page(
    "pages/home.py",
    title = "HoYoWiki-Tools",
    icon = ":material/home:",
    default = True
)

quest_formatter = st.Page(
    "pages/quest_formatter.py",
    title = "Quest Formatter",
    icon = ":material/chat_paste_go:"
)

about = st.Page(
    "pages/about.py",
    title = "About this app",
    icon = ":material/info:"
)

pg = st.navigation(
    {
        "Home": [home],
        "Tools": [quest_formatter],
        "Information": [about]
    }
)

pg.run()