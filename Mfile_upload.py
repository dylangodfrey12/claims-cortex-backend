# Mfile_upload.py

# This script is designed to upload measurements files from either Hover or EagleView.
# The prefix "M" stands for Measurements.
from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path):
    # Open the PDF file
    with open(file_path, "rb") as file:
        # Create a PDF reader object
        pdf_reader = PdfReader(file)
        
        # Initialize an empty string to store the extracted text
        text = ""
        
        # Iterate over each page of the PDF
        for page in pdf_reader.pages:
            # Extract the text from the page and append it to the text string
            text += page.extract_text()
    
    # Return the extracted text
    return text

def load_system_prompt(file_path):
    # Open the system prompt file in read mode with UTF-8 encoding
    with open(file_path, "r", encoding="utf-8") as file:
        # Read the contents of the system prompt file
        system_prompt = file.read()
    # Return the system prompt text
    return system_prompt

def get_pdf_path():
    # Specify the path to the PDF file
    return "HoverMeasurements11.pdf"