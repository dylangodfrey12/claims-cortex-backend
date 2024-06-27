# Xllm.py

# This script prepares the necessary data for input into the model. 
# The model will be used to extract data from Xactimate Estimates.
# The prefix "X" stands for Xactimate.

import openai
from Xfile_upload import load_system_prompt, extract_text_from_pdf, get_pdf_path

class XactimateExtractor:
    def __init__(self):
        # Initialize the OpenAI ChatCompletion client
        self.client = openai.ChatCompletion()
        api_key = "sk-proj-aKV63t4s0QRHbWDNrzTRT3BlbkFJt1ZLd6RnSRu9ga6v9twf"
        openai.api_key = api_key
    
    def extract_estimate(self,estimate_pdf_path):
        # Get the path to the PDF file from Xfile_upload module
        # pdf_path = get_pdf_path()
        # Extract the text from the PDF file
        pdf_text = extract_text_from_pdf(estimate_pdf_path)

        # Define the user message
        user_message = """
        Please read give me all of the line items paid for in the 
        xactimate estimate that I've just uploaded. You should only have the line items that were
        paid for and nothing else.

        Here is an example of the formatting:

        1: R&R Flashing - pipe jack
        2: 3 Tab Shingle
        3: Haul debris

        4. Contents - move out then reset
        5. Seal the surface area w/PVA primer - one coat
        6. Paint the walls - two coats
        7. Final cleaning - construction - Residential
        8. Haul debris - per pickup truck load - including dump fees
        9. General labor - labor minimum
        10. Cleaning labor minimum  

        Ensure you match which number the line item is.

        Only take information from the Line Items Page.
        Even if the line item repeats place it on the output.

        Guide to Understanding Your Property Estimate page is invalid, don't read from it.
        
        """
        
        # Specify the path to the system prompt file
        system_prompt_path = "X_systemprompt.txt"
        # Load the system prompt from the file
        system_prompt = load_system_prompt(system_prompt_path)
        
        # Create a list of messages for the chat
        messages = [
            {"role": "system", "content": system_prompt},  # Add the system prompt message
            {"role": "user", "content": user_message},  # Add the user message
            {"role": "user", "content": f"PDF Text: {pdf_text}"}  # Add the extracted PDF text
        ]

        # Call the create method of the ChatCompletion client to get the response
        response = self.client.create(
            model="gpt-4o",  # Specify the model to use
            messages=messages  # Pass the list of messages
        )
        # Extract the assistant's message content from the response
        estimate = response.choices[0].message.content
        
        # Return the assistant's message
        return estimate

    