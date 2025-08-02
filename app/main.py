import json
import pandas as pd
import streamlit as st
import requests
import base64
from PIL import Image
import streamlit_scrollable_textbox as stx

BACKEND_URL = "http://localhost:8000"

st.set_page_config(layout="wide", page_title="Smart Document Insight Engine")
st.title("Smart Document Insight Engine")

@st.cache_data(show_spinner=False)
def send_to_backend(file_bytes, file_name):
    res = requests.post(
        f"{BACKEND_URL}/parse",
        files={"file": (file_name, file_bytes)}
    )
    if res.status_code != 200:
        st.error("Failed to parse the document.")
        return None
    return res.json()

@st.cache_data(show_spinner=False)
def run_crewai(cleaned_text):
    res = requests.post(
        f"{BACKEND_URL}/crew",
        json={"text": cleaned_text}
    )
    if res.status_code != 200:
        st.error("CrewAI processing failed.")
        return None
    return res.json()

@st.cache_data(show_spinner=False)
def ask_question_rag(cleaned_text, question):
    res = requests.post(
        f"{BACKEND_URL}/rag",
        json={"document_text": cleaned_text, "question": question}
    )
    if res.status_code != 200:
        st.error("RAG query failed.")
        return None
    return res.json()

@st.cache_data(show_spinner=False)
def validate_document_with_rules(cleaned_text, rules):
    res = requests.post(
        f"{BACKEND_URL}/validate",
        json={"text": cleaned_text, "rules": rules}
    )
    if res.status_code != 200:
        st.error("Validation failed.")
        return None
    return res.json()

def render_table_flexibly(title, data):
    st.markdown(f"#### {title}")
    try:
        if isinstance(data, list):
            # List of dicts (normal table)
            if all(isinstance(row, dict) for row in data):
                df = pd.DataFrame(data)
                st.table(df)
            else:
                # Flat list
                df = pd.DataFrame({title: data})
                st.table(df)

        elif isinstance(data, dict):
            # Flat dict
            df = pd.DataFrame.from_dict(data, orient="index", columns=["Value"])
            df.reset_index(inplace=True)
            df.columns = ["Field", "Value"]
            st.table(df)

        elif isinstance(data, str):
            st.text(data)

        else:
            st.write(data)

    except Exception as e:
        st.error(f"Couldn't render table `{title}`: {e}")
        st.json(data)


if "document_data" not in st.session_state:
    st.session_state.document_data = {}
if "crew_outputs" not in st.session_state:
    st.session_state.crew_outputs = {}

uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "jpg", "jpeg", "png"])

if uploaded_file:
    file_name = uploaded_file.name

    if "current_file" not in st.session_state or st.session_state.current_file != file_name:
        st.session_state.current_file = file_name
        st.session_state.document_data = {}
        st.session_state.crew_outputs = {}

    if file_name not in st.session_state.document_data:
        with st.spinner("Uploading and parsing document..."):
            file_bytes = uploaded_file.read()
            doc_data = send_to_backend(file_bytes, file_name)
            if not doc_data:
                st.stop()
            st.session_state.document_data[file_name] = doc_data
    else:
        st.info("Loaded from session cache.")
        doc_data = st.session_state.document_data[file_name]

    # Extract document parts
    file_ext = doc_data["extension"]
    cleaned_text = doc_data["cleaned_text"]
    extracted_text = doc_data["extracted_text"]
    images = doc_data.get("images", [])
    img_ocr = doc_data.get("img_ocr", [])
    img_correct_ocr = doc_data.get("img_correct_ocr", [])

    # Display columns
    left_col, right_col = st.columns([1, 1.3])
    with left_col:
        st.subheader("Document Preview")
        if file_ext == "pdf":
            base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
            st.markdown(
                f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="750" type="application/pdf">',
                unsafe_allow_html=True
            )
        elif file_ext in ["jpg", "jpeg", "png"]:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        else:
            st.warning("Preview not supported for this format.")

    # Display tabs
    with right_col:
        st.subheader("Document Content")
        content_tabs = st.tabs(["Cleaned Text", "Extracted Text", "Images", "Key-Value Pairs", "Tables"])

        with content_tabs[0]:
            stx.scrollableTextbox(cleaned_text, height=600, key="cleaned_text")

        with content_tabs[1]:
            stx.scrollableTextbox(extracted_text, height=600, key="extracted_text")

        with content_tabs[2]:
            if images:
                for idx, img_b64 in enumerate(images):
                    with st.expander(f"Image {idx + 1}"):
                        image_data = base64.b64decode(img_b64)
                        st.image(image_data, caption=f"Image {idx + 1}", use_container_width=False)
                        st.markdown("**OCR Text:**")
                        stx.scrollableTextbox(img_ocr[idx], height=100, key=f"ocr_text_{idx}")
                        st.markdown("**Corrected Text:**")
                        stx.scrollableTextbox(img_correct_ocr[idx], height=120, key=f"corrected_text_{idx}")
            else:
                st.info("No images with OCR found.")

            if file_ext in ["jpg", "jpeg", "png"]:
                st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

        # Run CrewAI
        if file_name not in st.session_state.crew_outputs:
            with st.spinner("Running CrewAI agents..."):
                crew_outputs = run_crewai(cleaned_text)
                if crew_outputs:
                    st.session_state.crew_outputs[file_name] = crew_outputs
        else:
            crew_outputs = st.session_state.crew_outputs[file_name]

        doc_type = crew_outputs.get("type", "Unknown")
        fields = crew_outputs.get("fields", {})
        tables = crew_outputs.get("tables", {})
        rules = crew_outputs.get("rules", {})
        validation_result = crew_outputs.get("validation_result", {})
        custom_validation = crew_outputs.get("custom_validation", {})

        with content_tabs[3]:
            st.json(fields, expanded=True)
            fields = json.loads(fields)

        with content_tabs[4]:
            try:
                if isinstance(tables, str):
                    tables = json.loads(tables)
                if not tables:
                    st.info("No tables found.")
                elif isinstance(tables, dict):
                    for table_name, table_data in tables.items():
                        with st.expander(f"Table: {table_name}"):
                            render_table_flexibly(table_name, table_data)
                else:
                    st.warning("Unsupported table format received.")
            except Exception as err:
                st.error(f"Failed to display tables: {err}")
    
    st.subheader("Ask a Question About the Document")
    user_query = st.text_input("Enter your question")
    all_text = "Document Content \n " + cleaned_text + "\n Image Content \n".join(img_correct_ocr)
    if user_query:
        with st.spinner("Getting answer..."):
            rag_response = ask_question_rag(all_text, user_query)
            if rag_response:
                st.markdown(f"**Answer:** {rag_response['answer']}")
                st.markdown("**Context Used:**")
                for i, ctx in enumerate(rag_response["context"]):
                    # st.markdown(f"**Chunk {i + 1}:**")
                    stx.scrollableTextbox(ctx, height=120, key=f"context_{i}")

    st.divider()
    st.markdown(f"### Document Type: `{doc_type}`")

    # Valid?
    if validation_result:
        validation_result = json.loads(validation_result)
        st.subheader("Result")
        # with st.expander("Validation Report"):
        if isinstance(validation_result, str):
                validation_result = json.loads(validation_result)
        if not validation_result:
            st.info("No tables found.")
        elif isinstance(validation_result, dict):
            for name, data in validation_result.items():
                if name not in ["overall_validity"]:
                    if not data or data == {}:
                        st.warning(f"There are no {name}")
                    else:
                        with st.expander(f"Table: {name}"):
                            render_table_flexibly(name, data)
            # st.json(validation_result, expanded=True)
        check_valid = validation_result.get("overall_validity")
        if check_valid == "VALID":
            st.success("Document is VALID")
        else:
            st.error("Document is INVALID")

        st.divider()
        # Custom rules
        st.subheader("Add Custom Rules")
        custom_rules = st.text_area("Enter custom rules (one per line)", height=200)
        if custom_rules:
            with st.spinner("Validating with custom rules..."):
                # send a json with text and rules
                custom_validation = validate_document_with_rules(cleaned_text, custom_rules.splitlines())
                if custom_validation:
                    st.markdown("**Custom Validation Result:**")
                    if isinstance(custom_validation, str):
                        custom_validation = json.loads(custom_validation)
                    if not custom_validation:
                        st.info("No tables found.")
                    elif isinstance(custom_validation, dict):
                        for name, data in custom_validation.items():
                            if name not in ["overall_validity"]:
                                if not data or data == {}:
                                    st.warning(f"There are no {name}")
                                else:
                                    with st.expander(f"Table: {name}"):
                                        render_table_flexibly(name, data)
                    # st.json(custom_validation, expanded=True)
                    custom_check_valid = custom_validation.get("overall_validity")
                    if custom_check_valid == "VALID":
                        st.success ("Custom validation passed!")
                    else:
                        st.error("Custom validation failed.")
                else:
                    st.error("Custom validation failed to return results.")

    st.divider()
    # Database store
    st.subheader("📤 Store to MongoDB")
    if st.button("Store Document"):
        payload = {
            "user_id": "testing123",
            "filename": file_name,
            "type": doc_type,
            "content": extracted_text,
            "clean_content": cleaned_text,
            "images": [
                {
                    "image_base64": img_b64,
                    "ocr_text": img_ocr[i],
                    "corrected_text": img_correct_ocr[i]
                }
                for i, img_b64 in enumerate(images)
            ],
            "fields": fields,
            "tables": tables,
            "rules": {
                "user_rules": custom_rules.splitlines() if custom_rules else [],
                "ai_suggested": rules
            },
            "validation_status": check_valid and custom_check_valid,
            "validation_report": validation_result.get("validation_report") or {},
            # send the failed fields from both custom_validation and validation_result
            "failed_fields": [
                rule.get("rule", str(rule))
                for rule in validation_result.get("failed rules", []) + custom_validation.get("failed_rules", [])
            ],
        }

        res = requests.post(f"{BACKEND_URL}/store", json=payload)
        if res.status_code == 200:
            inserted_id = res.json().get("inserted_id")
            st.success(f"Stored document with ID: `{inserted_id}`")
        else:
            st.error(f"Failed to store document: {res.text}")

    st.divider()
