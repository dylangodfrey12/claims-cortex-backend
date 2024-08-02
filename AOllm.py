# AOllm.py

# This script organizes the arguments in order so they have a logical cohesion 
# The prefix "AO" stands for Argument Organizer.
import config
from openai import OpenAI
from Mfile_upload import load_system_prompt
import re

def print_to_text_file(text_to_print):
        with open('output.txt', 'a') as f:
            print(text_to_print, file=f)
            
class ArgumentOrganizer:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
   
            
    def organize_arguments(self, arguments):
        # Define the user message
        user_message = f"Please organize the following arguments in a logical order and do not include markdown and only return it in regular:\n\n{arguments}"
        
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
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Specify the model to use
            messages=messages  # Pass the list of messages
        )
        # Extract the assistant's message content from the response
        organized_arguments = response.choices[0].message.content
        # Remove the 'markdown\n-' and the very last '\n'
        organized_arguments_cleaned_text = re.sub(r"markdown\\n-", "", organized_arguments)
        organized_arguments_cleaned_text = re.sub(r"\\n```'$", "```'", organized_arguments_cleaned_text)
        # Return the organized arguments
        print_to_text_file(organized_arguments_cleaned_text)
        return organized_arguments_cleaned_text

    