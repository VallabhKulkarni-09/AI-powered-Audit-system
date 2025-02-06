import streamlit as st
import os
import pandas as pd
import easyocr
from utils import extract_text_from_pdf, parse_financial_data, audit_data, save_to_csv

st.set_page_config(
    page_title="Audity",
    page_icon="logo.png"
)
# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])  # Specify the language(s) you want to use

def extract_text_from_image_with_easyocr(image_path, reader):
    """Extract text from an image using EasyOCR."""
    result = reader.readtext(image_path)
    text = " ".join([res[1] for res in result])  # Combine the text results
    return text

st.title("Audity")
st.subheader("A Financial Statement Auditor")

# Upload balance sheet
balance_sheet_file = st.file_uploader("Upload Balance Sheet (CSV)", type=["csv"])
balance_sheet = {}

if balance_sheet_file is not None:
    balance_sheet_df = pd.read_csv(balance_sheet_file)
    
    # Strip whitespace from column names
    balance_sheet_df.columns = balance_sheet_df.columns.str.strip()
    
    # Check if required columns exist
    if 'Item' in balance_sheet_df.columns and 'Amount' in balance_sheet_df.columns:
        balance_sheet = dict(zip(balance_sheet_df['Item'], balance_sheet_df['Amount']))
        st.success("Balance Sheet Loaded Successfully")
    else:
        st.error("The uploaded CSV file must contain 'Item' and 'Amount' columns.")

# Upload multiple PDF or image files
uploaded_files = st.file_uploader("Upload PDF or Image files", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    all_texts = []
    for uploaded_file in uploaded_files:
        # Save the uploaded file temporarily
        with open("temp_file", "wb") as f:
            f.write(uploaded_file.getbuffer())

        if uploaded_file.name.endswith('.pdf'):
            text = extract_text_from_pdf("temp_file")
        else:
            # Use EasyOCR to extract text from the image
            text = extract_text_from_image_with_easyocr("temp_file", reader)

        all_texts.append(text)

        st.subheader(f"Extracted Text from {uploaded_file.name}")
        st.write(text)

        # Clean up the temporary file
        os.remove("temp_file")

    if st.button("Parse Financial Data"):
        combined_data = {}
        for text in all_texts:
            data = parse_financial_data(text)
            combined_data.update(data)  # Combine data from all files

        st.subheader("Parsed Data")
        st.write(combined_data)

        if balance_sheet:
            audited_data = audit_data(combined_data, balance_sheet)
            st.subheader("Audited Data")
            st.write(audited_data)

            if st.button("Save to CSV"):
                save_to_csv(audited_data, "financial_statement_audit.csv")
                st.success("Data saved to financial_statement_audit.csv")