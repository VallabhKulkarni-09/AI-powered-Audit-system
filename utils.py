# utils.py
import pdfplumber
import pytesseract
import cv2
import pandas as pd
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    text = pytesseract.image_to_string(img)
    return text

def parse_financial_data(text):
    # This function should be customized based on the format of your financial documents
    data = {}
    lines = text.splitlines()
    for line in lines:
        if ':' in line:
            item, amount = line.split(':')
            data[item.strip()] = float(amount.strip())
    return data

def audit_data(data, balance_sheet):
    # Simple audit function to check for discrepancies against the balance sheet
    audited_data = {}
    for item, amount in data.items():
        if item in balance_sheet:
            if balance_sheet[item] != amount:
                audited_data[item] = f"Discrepancy: Expected {balance_sheet[item]}, Found {amount}"
            else:
                audited_data[item] = f"Matched: {amount}"
        else:
            audited_data[item] = f"Not Found in Balance Sheet: {amount}"
    return audited_data

def save_to_csv(data, filename):
    df = pd.DataFrame(data.items(), columns=['Item', 'Status'])
    df.to_csv(filename, index=False)