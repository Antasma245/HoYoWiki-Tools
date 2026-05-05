import streamlit as st


st.logo(
    "assets/hoyowiki_tools_banner.png",
    size = "large",
    icon_image = "assets/hoyowiki_tools_logo.png"    
)

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

about = st.Page(
    "pages/about.py",
    title = "About this app",
    icon = ":material/info:"
)

pg = st.navigation(
    {
        "Home": [home],
        "Tools": [pgc_creator, quest_formatter],
        "Information": [about]
    }
)

pg.run()