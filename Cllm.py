# Cllm.py

# This script serves as the Large Language Model (LLM) for comparing estimates
# from Ellm.py and Xllm.py to find the differences.
# The prefix "C" stands for Compare Estimates.

import openai

class EstimateComparator:
    def __init__(self):
        # Initialize the OpenAI ChatCompletion client
        self.client = openai.ChatCompletion()
        api_key = "sk-proj-aKV63t4s0QRHbWDNrzTRT3BlbkFJt1ZLd6RnSRu9ga6v9twf"
        openai.api_key = api_key
    
    def compare_estimates(self, contractor_estimate, insurance_estimate):
        # Define the user message with the estimates from Ellm.py and Xllm.py
        user_message = f"""
        Please compare the contractor's estimate with the insurance company's estimate. 
        Identify and output the line items that are present in the contractor's estimate but missing in the insurance company's estimate. 
        Use the following estimates for the comparison:

        Contractor's Estimate:
        {contractor_estimate}

        Insurance Company's Estimate:
        {insurance_estimate}

        Only output the line items that are present in the contractor's estimate but missing in the insurance company's estimate. 
        Do not output the quantities of the line items.
        """
        
        # Specify the path to the system prompt file
        #system_prompt_path = "C_systemprompt.txt"
        # Load the system prompt from the file
        system_prompt = "follow the prompt"
        
        # Create a list of messages for the chat
        messages = [
            {"role": "system", "content": system_prompt},  # Add the system prompt message
            {"role": "user", "content": user_message},  # Add the user message
        ]

        # Call the create method of the ChatCompletion client to get the response
        response = self.client.create(
            model="gpt-4o",  # Specify the model to use
            messages=messages  # Pass the list of messages
        )
        # Extract the assistant's message content from the response
        differences = response.choices[0].message.content
        
        # Return the identified differences
        return differences