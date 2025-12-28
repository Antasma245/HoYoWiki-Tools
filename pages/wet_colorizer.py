import streamlit as st
import streamlit.components.v1 as components
import json


def build_palette_selector(color_palette: list[str]) -> None:
    palette_columns = st.columns(8)

    column_index = 0

    for color in color_palette:
        with palette_columns[column_index]:
            st.html("""<div style="width: 40px; height: 40px; background: %s;"></div>""" % color)

            if len(color) == 9:
                if st.button(":material/colorize:", key = color, disabled = True, help = "RGBA colors are not supported"):
                    st.session_state["wet_colorizer_color"] = color
            else:
                if st.button(":material/colorize:", key = color, help = color):
                    st.session_state["wet_colorizer_color"] = color
        
        if column_index < 7:
            column_index += 1
        else:
            column_index = 0


def hex_to_rgb(hex_code: str) -> str:
    hex_code = hex_code.lstrip('#')

    r, g, b = [int(hex_code[i:i+2], 16) for i in [0, 2, 4]]

    rgb_string = "%s, %s, %s" % (r, g, b)

    return rgb_string


if "wet_colorizer_unlock" not in st.session_state:
    st.session_state["wet_colorizer_unlock"] = False

if "wet_colorizer_color" not in st.session_state:
    st.session_state["wet_colorizer_color"] = "#FFFFFF"

if "wet_colorizer_html" not in st.session_state:
    st.session_state["wet_colorizer_html"] = None

st.title("WET Colorizer")

st.markdown("""
Adds color data to a text and prepares it to be pasted directly into the WET, extending the base color palette.

Tested for: :green-badge[:material/check: Genshin Impact] :yellow-badge[:material/contrast: Honkai Star Rail] :yellow-badge[:material/contrast: Zenless Zone Zero]
""")

with st.expander("How to Use"):
    st.markdown("""
    1. Under the `Palette` tab, select the color you want to use (alternatively, you can pick one from scratch under the `RGB Selector` tab)
    2. Enter the text you want to colorize (the color will be applied to the whole text)
    3. Click on the `Colorize` button
    4. Click on the `Copy Colorized Text` button that just appeared
    5. Paste the colorized text into a section of the WET that supports it
    """)

st.divider()

palette_tab, rgb_tab = st.tabs(["Palette", "RGB Selector"])

with palette_tab:
    st.subheader("Recommend Palette")

    recommend_palette = [
        "#ECE5D8", "#CCBFAD", "#FFD780", "#B28659", "#8A6D48", "#9B9C9F", "#7B7F88", "#4A5366",
        "#80FFD7", "#FFE699", "#80C0FF", "#99FFFF", "#FF9999", "#FFACFF", "#99FF88", "#BFBFBF",
        "#FFFFFFD9", "#FFFFFFA6", "#FFFFFF73", "#FFFFFF40", "#FFFFFF", "#37FFFF", "#FFE14B"
    ]

    build_palette_selector(recommend_palette)

    st.subheader("Extended Palette")
    
    extended_palette = [
        "#F39000", "#C7BCFF", "#B7FFB9"
    ]

    build_palette_selector(extended_palette)

with rgb_tab:
    st.warning("**Warning:** In order to preserve the **consistency** of entries, please make sure you've agreed on a **defined format** with the wiki team before introducing new colors into the WET.", icon = ":material/warning:")

    unlock_rgb_selector = st.checkbox("I have read and understand the above, unlock the RGB selector :material/lock:", value = st.session_state["wet_colorizer_unlock"])

    picked_color = st.color_picker("Select a color:", value = st.session_state["wet_colorizer_color"], disabled = not unlock_rgb_selector)

    st.session_state["wet_colorizer_color"] = picked_color.upper()

st.divider()

selected_color_hex = st.session_state["wet_colorizer_color"]
selected_color_rgb = hex_to_rgb(selected_color_hex)

st.html("""<p>Selected color: <span style="color: rgb(%s);">%s</span></p>""" % (selected_color_rgb, selected_color_hex))

text_to_colorize = st.text_input("Text to colorize:")

if st.button("Colorize", type = "primary"):
    html_data = """<p><span style="color: rgb(%s);">%s</span></p>""" % (selected_color_rgb, text_to_colorize)

    st.session_state["wet_colorizer_html"] = html_data

if st.session_state["wet_colorizer_html"] is not None:
    sanitized_html = json.dumps(st.session_state["wet_colorizer_html"])

    copy_html_button = """
    <button style="font-size: 14px; padding: 10px 10px; border-radius: 8px;" onclick="copyHTML()">Copy Formatted Text</button>
    <script>
    async function copyHTML() {
        const html = %s;
        try {
            await navigator.clipboard.write([
                new ClipboardItem({
                    "text/html": new Blob([html], { type: "text/html" })
                })
            ]);
            alert("Copy successful!");
        } catch (err) {
            alert("Failed to copy: " + err);
        }
    }
    </script>
    """ % sanitized_html

    components.html(copy_html_button)