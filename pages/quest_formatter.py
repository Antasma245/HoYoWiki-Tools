import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import html
import json
import re


def format_objective(objective_df: pd.DataFrame) -> None:
    st.session_state["quest_formatter_html"] = None

    html_data = "<ol>"

    for _, row in objective_df.iterrows():
        if row["header"]:
            html_data += "<li><p>%s</p></li>" % row["text"]

    html_data += "</ol>"
    
    st.session_state["quest_formatter_html"] = html_data


def classify_dialogue(dialogue_df: pd.DataFrame) -> None:
    st.session_state["quest_formatter_html"] = None

    dialogue_df.insert(0, "type", None)

    variable_text = []

    for idx, row in dialogue_df.iterrows():
        row_type = None

        if row["header"] == "Quest Description":
            row_type = "description"

            variable_text.append(row["header"])
        elif row["header"] == "Quest Objective":
            row_type = "objective"

            variable_text.append(row["header"])
        elif row["header"] == "(Missing localization)":
            row_type = "missing"
        elif "Additional Dialogue" in row["header"] or "Alternative Dialogue" in row["header"] or "Optional Dialogue" in row["header"]:
            row_type = "addopt"

            variable_text.append(row["header"])
        elif row["header"] == "Choice":
            row_type = "choice_flag"
        elif re.search(r"\d+\.\s+", row["header"]):
            row_type = "choice_branch"
        elif "," in row["header"]:
            row_type = "location"

            variable_text.append(row["header"])
        elif row["header"] and row["text"]:
            row_type = "dialogue"

            variable_text.append(row["header"])
        elif row["header"]:
            row_type = "sub_mission"

            variable_text.append(row["header"])
        elif row["text"]:
            row_type = "action"
        else:
            row_type = "blank"
        
        dialogue_df.at[idx, "type"] = row_type

        for variable_group in re.finditer(r"(?:\{[^{}]+\})+", row["text"]):
            matched_text = variable_group[0]

            if r"{RUBY#" in matched_text:
                for ruby_group in re.finditer(r"\s*(\S+)\{RUBY#\[.\](.+)\}(\S+)\s*", row["text"]):
                    matched_ruby = ruby_group[0]

                    base_text = html.escape(ruby_group[1] + ruby_group[3])
                    ruby_text = html.escape(ruby_group[2])

                    formatted_ruby = """<custom-ruby data-ruby="%s|%s"></custom-ruby>""" % (base_text, ruby_text)

                    dialogue_df.at[idx, "text"] = row["text"].replace(matched_ruby, formatted_ruby)
            elif r"{NON_BREAK_SPACE}" in matched_text:
                dialogue_df.at[idx, "text"] = row["text"].replace(r"{NON_BREAK_SPACE}", "&nbsp;")
            else:
                variable_text.append(matched_text)

    if len(variable_text) > 0:
        get_variable_text_translation(dialogue_df, variable_text)
    else:
        format_dialogue(dialogue_df)


@st.dialog("Header & Bracket Content Replacement", width = "medium")
def get_variable_text_translation(classified_dialogue_df: pd.DataFrame, variable_text: list[str]) -> None:
    st.markdown("If applicable, please provide a translation of the content below. If not, leave field as is. Then, press `Submit`.")

    text_to_translate = list(dict.fromkeys(variable_text))
    
    for og_text in text_to_translate:
        st.text_input(
            og_text,
            value = og_text,
            key = og_text,
            placeholder = "Do not leave empty!",
            icon = ":material/translate:"
        )
    
    text_to_translate.sort(key = lambda og_text: len(og_text), reverse = True)
    
    if st.button("Submit", key = "submit_translated_text_button"):
        for og_text in text_to_translate:
            translated_text = st.session_state[og_text]

            classified_dialogue_df = classified_dialogue_df.map(lambda text: text.replace(og_text, translated_text))
        
        format_dialogue(classified_dialogue_df)

        st.rerun()



def format_dialogue(classified_dialogue_df: pd.DataFrame) -> None:
    html_data = ""

    opened_tags = []

    for idx, row in classified_dialogue_df.iterrows():
        last_row_type = classified_dialogue_df.at[idx - 1, "type"] if idx > 0 else None

        match row["type"]:
            case "description":
                html_data += """
                <table>
                    <tbody>
                        <tr>
                            <td colspan="1" rowspan="1">
                                <p>
                                    <strong><span style="color: rgb(255, 255, 255);">%s: </span></strong>
                                    <span style="color: rgb(255, 255, 255);">%s</span>
                                </p>
                            </td>
                        </tr>
                    </tbody>
                </table>
                """ % (row["header"], row["text"])
            case "objective":
                html_data += """
                <table>
                    <tbody>
                        <tr>
                            <td colspan="1" rowspan="1">
                                <p><strong>%s: </strong>%s</p>
                            </td>
                        </tr>
                    </tbody>
                </table>
                """ % (row["header"], row["text"])
            case "missing":
                continue
            case "addopt":
                html_data += """
                <p>%s</p>
                <table>
                    <tbody>
                        <tr>
                            <td colspan="1" rowspan="1">
                """ % row["header"]

                opened_tags.append("addopt")
            case "choice_flag":
                continue
            case "choice_branch":
                if last_row_type != "choice_flag":
                    opened_tags.reverse()

                    html_data += """
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    """

                    opened_tags.remove("choice_branch")
                    
                    opened_tags.reverse()
                    
                row["header"] = re.sub(r"\d+\.\s+", "", row["header"])

                html_data += """
                <table>
                    <tbody>
                        <tr>
                            <td colspan="1" rowspan="1">
                                <p><span style="color: rgb(255, 255, 255);">%s: %s</span></p>
                """ % (row["header"], row["text"])

                opened_tags.append("choice_branch")
            case "location":
                html_data += """
                <p>
                    <strong><span style="color: rgb(236, 229, 216);">%s</span></strong>
                </p>
                """ % row["header"]
            case "dialogue":
                if last_row_type == "objective":
                    html_data += "<p></p>"
                
                html_data += """<p><span style="color: rgb(255, 255, 255);">%s: </span>%s</p>""" % (row["header"], row["text"])
            case "sub_mission":
                if last_row_type == "objective":
                    html_data += "<p></p>"
                
                html_data += "<p><em>%s</em></p>" % row["header"]
            case "action":
                html_data += """
                <p></p>
                <table>
                    <tbody>
                        <tr>
                            <td colspan="1" rowspan="1">
                                <p><span style="color: rgb(255, 255, 255);">%s</span></p>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <p></p>
                """ % row["text"]
            case "blank":
                next_row_type = classified_dialogue_df.at[idx + 1, "type"]
                if opened_tags and next_row_type != "choice_flag":
                    match opened_tags[-1]:
                        case "addopt" | "choice_branch":
                            html_data += """
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                            """

                            opened_tags.pop()

                if next_row_type != "choice_branch":
                    html_data += "<p></p>"

    if opened_tags:
        for tag in reversed(opened_tags):
            match tag:
                case "addopt" | "choice_branch":
                    html_data += """
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    """

                    opened_tags.pop()
    
    st.session_state["quest_formatter_html"] = html_data


if "quest_formatter_html" not in st.session_state:
    st.session_state["quest_formatter_html"] = None

st.title("Quest Formatter")

st.markdown("""
Takes text data from a localization sheet made by the Quest Team and formats it to be pasted directly into the WET.

Tested for: :green-badge[:material/check: Genshin Impact]
""")

with st.expander("How to Use"):
    st.subheader("To Format Quest Objective")

    st.markdown("""
    1. Open the localization sheet of the quest you're working on
    2. Locate the `Quest Objective` header
    3. Starting from the row just below the header, select and copy the first column of quest objective data as well as your language's one (non-numbered quest objectives will automatically be ignored)
    4. Paste your selection in the page's interactive table, under the `Objective` tab
    5. Click on the `Format` button
    6. Click on the `Copy Formatted Text` button that just appeared
    7. Paste the formatted text into the WET
    """)

    st.subheader("To Format Quest Dialogue")

    st.markdown("""
    1. Open the localization sheet of the quest you're working on
    2. Locate the `Dialogue` header
    3. Starting from the row just below the header, select and copy the first column of dialogue data as well as your language's one (make sure to fill in the Missing Translation fields beforehand, else exclude them from your selection)
    4. Paste your selection in the page's interactive table, under the `Dialogue` tab
    5. Click on the `Format` button
    6. If prompted, fill in the Content Replacement form
    7. Click on the `Copy Formatted Text` button that just appeared
    8. Paste the formatted text into the WET
    """)

st.divider()

default_table_data = {"header": [""], "text": [""]}
default_table_df = pd.DataFrame(default_table_data)

default_table_config = {
    "header" : st.column_config.TextColumn("Row Header", width = "small"),
    "text" : st.column_config.TextColumn("Text", width = "large")
}

objective_tab, dialogue_tab = st.tabs(["Objective", "Dialogue"])

with objective_tab:
    objective_df = st.data_editor(default_table_df, column_config = default_table_config, num_rows = "dynamic", key = "objective_data")

    if st.button("Format", type = "primary", key = "format_objective_button"):
        format_objective(objective_df)

with dialogue_tab:
    dialogue_df = st.data_editor(default_table_df, column_config = default_table_config, num_rows = "dynamic", key = "dialogue_data")

    if st.button("Format", type = "primary", key = "format_dialogue_button"):
        classify_dialogue(dialogue_df)

if st.session_state["quest_formatter_html"] is not None:
    sanitized_html = json.dumps(st.session_state["quest_formatter_html"])

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