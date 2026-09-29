import os
import tempfile
import streamlit as st

from backend import convert_xml


st.set_page_config(
    page_title="XML to JSON Agent"
)

st.title("XML to JSON Agent")

input_type = st.radio(
    "Choose input method",
    ["Upload XML File", "Enter File Path"],
    horizontal=True
)

file_path = None

if input_type == "Upload XML File":

    uploaded_file = st.file_uploader(
        "Upload XML file",
        type=["xml"]
    )

    if uploaded_file:

        temp_dir = tempfile.gettempdir()

        file_path = os.path.join(
            temp_dir,
            uploaded_file.name
        )

        with open(
            file_path,
            "wb"
        ) as f:
            f.write(
                uploaded_file.getbuffer()
            )

        st.success(
            f"File uploaded: {uploaded_file.name}"
        )

else:

    file_path = st.text_input(
        "Enter XML file path",
        placeholder=r"C:\Users\Aryan Singh\Downloads\sample_employees.xml"
    )


instruction = st.text_area(
    "What do you want to do?",
    placeholder=(
        "Example: Convert employees into a simple array. "
        "Combine first and last name into name. "
        "Keep only name, department and skills."
    )
)


if st.button(
    "Convert",
    type="primary"
):

    if not file_path:

        st.warning(
            "Please upload an XML file or enter a file path."
        )

    elif not os.path.exists(file_path):

        st.error(
            "File not found."
        )

    elif not instruction:

        st.warning(
            "Please enter what you want to do with the XML."
        )

    else:

        with st.spinner(
            "Agent is deciding how to convert the XML..."
        ):

            result = convert_xml(
                file_path,
                instruction
            )

        if result["method"] == "LLM":

            st.info(
                "🤖 LLM was used for this conversion."
            )

        else:

            st.info(
                "🔧 XML Parser Tool was used for this conversion."
            )

        st.success(
            "Conversion completed!"
        )

        st.subheader("JSON")

        try:

            import json

            json_data = json.loads(
                result["result"]
            )

            st.json(json_data)

        except:

            st.code(
                result["result"],
                language="json"
            )

        output_path = (
            os.path.splitext(file_path)[0]
            + ".json"
        )

        if os.path.exists(output_path):

            with open(
                output_path,
                "r",
                encoding="utf-8"
            ) as f:

                json_file = f.read()

            st.download_button(
                "Download JSON",
                json_file,
                file_name=os.path.basename(
                    output_path
                ),
                mime="application/json"
            )