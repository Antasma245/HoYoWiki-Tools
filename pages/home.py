import streamlit as st


st.title("Welcome to HoYoWiki-Tools!")

st.markdown("""
    Here you will find a collection of small applications that aim to streamline the work of HoYoWiki collaborators by automating repetitive tasks.

    Check out what we have in stock in the sidebar at the left of this page!
""")

st.markdown("")

with st.expander("Browser Compatibility :material/warning:", width = "stretch"):
    st.markdown("""
        One of this program's components only guarantees support for recent versions of the following web browsers:
        * Google Chrome
        * Firefox
        * Microsoft Edge
        * Safari

        Compatibility with unsupported browsers or old versions of the above browsers is not guaranteed.
    """)