# Mllm.py

# This script serves as the Large Language Model (LLM) for extracting measurements
# from Hover or EagleView reports.
# The prefix "M" stands for Measurements.

import os
# from groq import Groq
from openai import OpenAI
from Mfile_upload import load_system_prompt, extract_text_from_pdf, get_pdf_path

class MeasurementExtractor:
    def __init__(self):
        # # Set the Groq API key
        # os.environ["GROQ_API_KEY"] = "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"
        # # Initialize the Groq client
        # self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Initialize the OpenAI ChatCompletion client
        self.client = OpenAI(api_key="sk-proj-aKV63t4s0QRHbWDNrzTRT3BlbkFJt1ZLd6RnSRu9ga6v9twf")

    
    def extract_measurements(self,property_pdf_path):
        # Get the path to the PDF file from Mfile_upload module
        # pdf_path = get_pdf_path()
        # Extract the text from the PDF file
        pdf_text = extract_text_from_pdf(property_pdf_path)

        # Define the user message
        user_message = """
        Please output the measurements on the hover report. Use the system prompt to guide you on which measurements to remove.

        For the hover measurements output them like this example below:

        ##Roofing Measurements:
        1. Roof Total Area:** 3,219 ft²
        2. Ridges / hips: 105' 2"
        3. Valleys: 99'
        4. Rakes: 265' 11"
        5. Gutters/Eaves: 171' 8"
        6. Flashing: 48'
        7. Step Flashing: 117' 5"
        8. Roof Pitch (roof pitch type): 1230 ft^2
        9. Roof Pitch (roof pitch type): 920 ft^2

        ## Siding Measurements:
        1. Siding Facades:** 1350.00 ft²
        2. Siding Per Elevation
        * Total Front: 345'
        * Total Right: 350'
        * Total Left: 380' 
        * Total Back: 275'

        The data must look identical to what the format. No changes can be made to the format. 
        Do not use markdown or bolding either.
        """
        
        # Specify the path to the system prompt file
        system_prompt_path = "M_systemprompt.txt"
        # Load the system prompt from the file
        system_prompt = load_system_prompt(system_prompt_path)
        messages = [
            {"role": "system", "content": system_prompt},  # Add the system prompt message
            {"role": "user", "content": user_message},  # Add the user message
            {"role": "user", "content": f"PDF Text: {pdf_text}"}  # Add the extracted PDF text
            ]
        response = self.client.chat.completions.create(
        model="gpt-4o",
        temperature=0,# Specify the model to use
        messages=messages  # Pass the list of messages
        )
        # try:
            # Create a chat completion using the Groq client
            # chat_completion = self.client.chat.completions.create(
            #     messages=[
            #         {"role": "system", "content": system_prompt},
            #         {"role": "user", "content": user_message},
            #         {"role": "user", "content": f"PDF Text: {pdf_text}"}
            #     ],
            #     temperature=1.0,
            #     model="llama3-70b-8192",
            # )
             # Create a list of messages for the chat
            
            # Call the create method of the ChatCompletion client to get the response

        # )
        # Extract the assistant's message content from the response
        measurements = response.choices[0].message.content
        
            # Extract the assistant's message content from the response
        # measurements = chat_completion.choices[0].message.content
            
        return measurements
        # except Exception as e:
        print(f"Error: {str(e)}")
        return None