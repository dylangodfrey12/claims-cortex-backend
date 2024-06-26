# Ellm.py

# This script serves as the Large Language Model (LLM) turning measurements from Mllm.py into an internal
# Xactimate estimate
# The prefix "E" stands for Estimate.

import openai
from Mfile_upload import load_system_prompt

class EstimateGenerator:
    def __init__(self):
        # Initialize the OpenAI ChatCompletion client
        self.client = openai.ChatCompletion()
    
    def generate_estimate(self, measurements):
        # Define the user message with the measurements from Mllm.py
        user_message = f"""
        Please output an xactimate estimate. Use the system prompt determine the formulas needed to construct the line items.
        
        Measurements:
        {measurements}

        Only output the line items that would be on the xactimate estimate. Nothing else.
        Do not output the quantities of the line items.

        """
        
        # Specify the path to the system prompt file
        system_prompt_path = "E_systemprompt.txt"
        # Load the system prompt from the file
        system_prompt = load_system_prompt(system_prompt_path)
        
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
        estimate = response.choices[0].message.content
        
        # Return the generated estimate
        return estimate