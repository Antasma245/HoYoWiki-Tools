import streamlit as st
import pandas as pd
import io
import re
import time


def get_target_rows(template_df: pd.DataFrame) -> None:
    language_amount = 15 if template_df.iat[0, 17] != "" else 13

    target_rows = {"idx": [], "header": [], "tsv_text": [], "language_amount": language_amount}
    
    for idx, row in template_df.iterrows():
        if row.iat[0] != "":
            if row.iat[3] == "":
                target_rows["idx"].append(idx)
                
                row_header = "%s %s %s (R%s)" % (row.iat[0], row.iat[1], row.iat[2], idx)
                target_rows["header"].append(row_header)

            if idx > 0:
                template_df.iat[idx, 0] = int(row.iat[0])
    
    get_batch_text(template_df, target_rows)


@st.dialog("Batch Text", width = "medium")
def get_batch_text(template_df: pd.DataFrame, target_rows: dict) -> None:
    st.markdown("Please paste the texts in the fields below. Then, press `Submit`.")

    with st.popover("Text Format"):
        st.markdown("""
            You can include one or many objects (materials, books, ...) that use the same template in your selection. However, do **NOT** include the language line (`CHS CHT DE EN ...`) and the identifier column (`Name, Desc, ...`).
            
            When pasting text data, please make sure that:
            * Data is formatted as TSV (tab-separated values). If you directly copy/paste the texts from a Microsoft Excel or Google Sheets document, they should already be formatted as TSV (see below for an example of valid text selection)
            * If your selection includes many objects, make sure they are ordered the same across all sheets (e.g. if your selection contains Mushroom, Sweet Flower and Fowl, the text in each sheet should be in order of Mushroom, Sweet Flower and Fowl)
            * For image URLs, you only need to provide one per object (as opposed to one per language per object for normal texts)
            
            Valid text selection example for one field (3 languages, 2 objects):
        """)

        selection_example_data = {
            "Identifier": ["Book1", "Book2"],
            "CHS": [":blue-background[Story1]", ":blue-background[Story2]"],
            "CHT": [":blue-background[Story1]", ":blue-background[Story2]"],
            "EN": [":blue-background[Story1]", ":blue-background[Story2]"]

        }
        selection_example_df = pd.DataFrame(selection_example_data)
        selection_example_df.set_index("Identifier", inplace = True)

        st.table(selection_example_df)

    for idx, header in zip(target_rows["idx"], target_rows["header"]):
        st.text_area(
            header,
            key = idx,
            placeholder = "Paste text here"
        )
    
    if st.button("Submit", key = "submit_batch_text_button"):
        with st.spinner("Please wait...", show_time = True):
            for idx in target_rows["idx"]:
                batch_text = re.sub("\\n(?!.)", "", st.session_state[idx])
                tsv_text = tsv_to_list(batch_text)

                target_rows["tsv_text"].append(tsv_text)
            
            create_batch_sheet(template_df, target_rows)

            st.rerun()


def create_batch_sheet(template_df: pd.DataFrame, target_rows: dict) -> None:
    target_rows_idx = target_rows["idx"]
    target_rows_tsv = target_rows["tsv_text"]
    language_amount = target_rows["language_amount"]

    object_amount = len(target_rows_tsv[0])
    
    batch_file = io.BytesIO()

    with pd.ExcelWriter(batch_file) as writer:
        for processed_df_counter in range(object_amount):
            # Duplicate the template Dataframe
            duplicated_df = template_df.copy()

            # For each target row
            for row_counter in range(len(target_rows_idx)):
                object_line = target_rows_tsv[row_counter][processed_df_counter]

                # If the object line only has one object (i.e. language), consider it a link
                if len(object_line) == 1:
                    link = object_line[0]

                    # Duplicate the link of the line of content to have one per language
                    for _ in range(language_amount - 1):
                        object_line.append(link)
                
                # Edit the target cells
                duplicated_df.iloc[target_rows_idx[row_counter], 3:18] = object_line

            # Add the duplicated Dataframe to the batch file
            sheet_name = "Sheet%s" % processed_df_counter

            duplicated_df.to_excel(writer, sheet_name = sheet_name, header = False, index = False)

    batch_file.seek(0)

    st.session_state["pgc_batch_spreadsheet"] = batch_file.getvalue()


def tsv_to_list(tsv_string:str) -> list[list[str]]:
    lines = tsv_string.split("\n")

    tsv_list = []
    
    for line in lines:
        values = line.split("\t")
        tsv_list.append(values)
    
    return tsv_list


if "pgc_batch_spreadsheet" not in st.session_state:
    st.session_state["pgc_batch_spreadsheet"] = None

st.title("PGC Creator")

st.markdown("""
Creates and fills in a PGC spreadsheet in batch from a template for it to be loaded and pushed into the WET.

Tested for: :green-badge[:material/check: Genshin Impact] :yellow-badge[:material/contrast: Honkai Star Rail] :yellow-badge[:material/contrast: Zenless Zone Zero]
""")

with st.expander("How to Use"):
    st.markdown("""
    1. Import the template PGC spreadsheet you want to use (if you import a template that contains multiple sheets, only the first one will be considered)
    2. If needed, make modifications to the template and preview it in the page's interactive table
    3. Click on the `Process Template` button
    4. When prompted, fill in the Batch Text form
    5. Click on the `Download PGC Spreadsheet` button that just appeared
    6. Load the downloaded file into the WET
    
    This application supports templates with 15 languages (Genshin Impact) or 13 languages (Honkai Star Rail, Zenless Zone Zero).
    """)

st.divider()

imported_template_xlsx = st.file_uploader("Upload Template", type = "xlsx", key = "import_template_button")

if imported_template_xlsx is not None:
    imported_template_df = pd.read_excel(imported_template_xlsx, header = None, dtype = str)

    template_df = st.data_editor(imported_template_df, num_rows = "dynamic", key = "pgc_template_data")

    if st.button("Process Template", type = "primary", key = "process_template_button"):
        template_df.fillna("", inplace = True)
        get_target_rows(template_df)

if st.session_state["pgc_batch_spreadsheet"] is not None:
    epoch_time = time.time()

    st.download_button(
        "Download PGC spreadsheet",
        data = st.session_state["pgc_batch_spreadsheet"],
        file_name = "PGC_BATCH_OUT_%s.xlsx" % int(epoch_time),
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key = "download_pgc_button",
        icon = ":material/download:"
    )