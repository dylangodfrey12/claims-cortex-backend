# Dllm.py

# This script serves as the Large Language Model (LLM) for processing the output from Cllm.py
# and generating arguments based on the differences between the contractor's and insurance company's estimates.
# The prefix "D" stands for Dispatching.

import openai
from Mfile_upload import load_system_prompt

class ArgumentSelector:
    def __init__(self):
        # Initialize the OpenAI ChatCompletion client
        self.client = openai.ChatCompletion()
        api_key = "sk-proj-aKV63t4s0QRHbWDNrzTRT3BlbkFJt1ZLd6RnSRu9ga6v9twf"
        openai.api_key = api_key
    
    def generate_arguments(self, differences):
        # Define the user message with the differences from Cllm.py
        user_message = f"""

        {differences}

        Ensure that each argument category is listed only once in the output, even if multiple line items map to the same argument.

        Ensure the output is only the difference and they are bulleted like so, anything else is wrong:
        -
        -
        -
        -
        -
        -

        
        """
        
        # Specify the path to the system prompt file
        system_prompt_path = "D_systemprompt.txt"
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
        arguments = response.choices[0].message.content
        
        # Return the generated arguments
        return arguments