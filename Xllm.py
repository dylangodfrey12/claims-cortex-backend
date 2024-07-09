# Xllm.py

# This script prepares the necessary data for input into the model. 
# The model will be used to extract data from Xactimate Estimates.
# The prefix "X" stands for Xactimate.

from openai import OpenAI
from Xfile_upload import load_system_prompt, extract_text_from_pdf, get_pdf_path

class XactimateExtractor:
    def __init__(self):
        self.client = OpenAI(api_key="sk-proj-aKV63t4s0QRHbWDNrzTRT3BlbkFJt1ZLd6RnSRu9ga6v9twf")
    
    def extract_estimate(self,estimate_pdf_path):
        # Get the path to the PDF file from Xfile_upload module
        # pdf_path = get_pdf_path()
        # Extract the text from the PDF file
        pdf_text = extract_text_from_pdf(estimate_pdf_path)

        # Define the user message
        user_message = """
            Please read give me all of the line items paid for in the Xactimate estimate that I've just uploaded. You should only have the line items and quantities that were paid for and nothing else.

            ---

            **Example One of the Formatting:**

            **1: Remove 3 tab - 25 yr. - composition shingle roofing - incl. felt:**

            - **Quantity:** 0.33SQ

            **2: tab - 25 yr. - comp. shingle roofing - w/out felt:**

            - **Quantity:** 0.33SQ

            **3: Remove Additional charge for high roof (2 stories or greater)**

            - **Quantity:** 20.07 SQ

            **4: Asphalt starter - universal starter course**

            - **Quantity:** 135.00 LF

            **5: Ridge cap - composition shingles**

            - **Quantity:** 14.00 LF

            **6: Drip Edge**

            - **Quantity:** 321.00 LF

            **7: Flashing - Pipe Jack**

            - **Quantity:** 321.00 LF

            **8: Continuous ridge vent - aluminum**

            - **Quantity:** 54.00 LF

            ---

            **Example Two of the Formatting:**

            **1: Tear off, haul and dispose of comp. shingles - 3 tab**

            - **Quantity:** 20.24 SQ

            **2: Roofing felt - 15 lb.**

            - **Quantity:** 14.68 SQ

            **3: Roofing felt - 15 lb**

            - **Quantity:** 5.56 SQ

            **4: 3 tab - 25 yr. - comp. shingle roofing - w/out felt**

            - **Quantity:** 0.67 SQ

            **5: 3 tab - 25 yr. - comp. shingle roofing - w/out felt**

            - **Quantity:** 22.00 SQ

            **6: 3 tab - 25 yr. - comp. shingle roofing - w/out felt**

            - **Quantity:** 0.67 SQ

            **7: Flashing - Pipe Jack**

            - **Quantity:** 3.00 EA

            **8: R&R Chimney flashing - average (32" x 36")**

            - **Quantity:** 1.00 EA

            **9: Drip Edge**

            - **Quantity:** 229.05 LF

            **10: Ice & water barrier**

            - **Quantity:** 556.00 SF

            ---

            **Example Three of the Formatting:**

            **1: Remove 3 tab - 25 yr. - composition shingle roofing (per SHINGLE)**

            - **Quantity:** 12.00 EA

            **2: 3 tab - 25 yr. - composition shingle roofing (per SHINGLE)**

            - **Quantity:** 12.00 EA

            ---

            **Example Four of the Formatting:**

            **1: Tear off, haul and dispose of comp. shingles - 3 tab**

            - **Quantity:** 12.70 SQ

            **2: Remove Additional charge for high roof (2 stories or greater)**

            - **Quantity:** 3.91 SQ

            **3: Remove Additional charge for steep roof - 7/12 to 9/12 slope**

            - **Quantity:** 0.09 SQ

            **4: Roofing felt - 15 lb**

            - **Quantity:** 10.37 SQ

            **5: 3 tab - 25 yr. - comp. shingle roofing - w/out felt**

            - **Quantity:** 0.33 SQ

            **6: 3 tab - 25 yr. - comp. shingle roofing - w/out felt**

            - **Quantity:** 0.67 SQ

            **7: 3 tab - 25 yr. - comp. shingle roofing - w/out felt**

            - **Quantity:** 14.00 SQ

            **8: 3 tab - 25 yr. - comp. shingle roofing - w/out felt**

            - **Quantity:** 0.33 SQ

            **9: Additional charge for high roof (2 stories or greater)**

            - **Quantity:** 3.91 SQ

            **10: Additional charge for steep roof - 7/12 to 9/12 slope**

            - **Quantity:** 0.09 SQ

            **11: Continuous ridge vent - aluminum**

            - **Quantity:** 27.75 LF

            **12: Flashing - pipe jack**

            - **Quantity:** 2.00 EA

            **13: R&R Drip edge**

            - **Quantity:** 189.17 LF

            **14: Digital satellite system - Detach & reset**

            - **Quantity:** 1.00 EA

            **15: Digital satellite system - alignment and calibration only**

            - **Quantity:** 1.00 EA

            **16: R&R Power attic vent cover only - metal**

            - **Quantity:** 1.00 EA

            **17: Roofer - per hour**

            - **Quantity:** 1.00 HR

            **18: Ice & water barrier**

            - **Quantity:** 233.05 SF

            ---

            Ensure you match which number the line item is.

            Only take information from the Line Items Page. Even if the line item repeats place it on the output.

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
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Specify the model to use
            temperature=0,
            messages=messages  # Pass the list of messages
        )
        # Extract the assistant's message content from the response
        estimate = response.choices[0].message.content
        
        # Return the assistant's message
        return estimate

    