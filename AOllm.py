# AOllm.py

# This script organizes the arguments in order so they have a logical cohesion 
# The prefix "AO" stands for Argument Organizer.

import openai
from Mfile_upload import load_system_prompt

class ArgumentOrganizer:
    def __init__(self):
        # Initialize the OpenAI ChatCompletion client
        self.client = openai.ChatCompletion()
        api_key = "sk-proj-aKV63t4s0QRHbWDNrzTRT3BlbkFJt1ZLd6RnSRu9ga6v9twf"
        openai.api_key = api_key
    
    def organize_arguments(self, arguments):
        # Define the user message
        user_message = f"Please organize the following arguments in a logical order:\n\n{arguments}"
        
        # Specify the path to the system prompt file
        system_prompt_path = "AO_systemprompt.txt"
        # Load the system prompt from the file
        system_prompt = load_system_prompt(system_prompt_path)
        
        # Create a list of messages for the chat
        messages = [
            {"role": "system", "content": system_prompt},  # Add the system prompt message
            {"role": "user", "content": user_message}  # Add the user message
        ]

        # Call the create method of the ChatCompletion client to get the response
        response = self.client.create(
            model="gpt-4o",  # Specify the model to use
            messages=messages  # Pass the list of messages
        )
        # Extract the assistant's message content from the response
        organized_arguments = response.choices[0].message.content
        
        # Return the organized arguments
        return organized_arguments

    