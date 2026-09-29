import os
import streamlit as st

from backend import convert_xml


st.set_page_config(
    page_title="XML to JSON Agent"
)

st.title("XML to JSON Agent")

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


if st.button("Convert"):

    if not file_path:

        st.warning(
            "Enter an XML file path."
        )

    elif not os.path.exists(file_path):

        st.error(
            "File not found."
        )

    elif not instruction:

        st.warning(
            "Enter what you want to do with the XML."
        )

    else:

        with st.spinner(
            "Agent is deciding..."
        ):

            result = convert_xml(
                file_path,
                instruction
            )

        st.success(
            "Conversion completed!"
        )

        st.write(
            "Method used:",
            result["method"]
        )

        st.subheader("JSON")

        st.json(
            result["result"]
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