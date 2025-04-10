# ASEllm.py

# This script summarize the arguments for the email presented so the user understand how they will be connected 
# The prefix "ASE" stands for Argument Summarizer Email.

import anthropic
import config
from openai import OpenAI
from email_upload import load_system_prompt, get_adjuster_email

class ArgumentSummarizerEmail:
    def __init__(self):
         #Initialize the Anthropic client
        api_key = config.ANTHROPIC_API_KEY
        self.client = anthropic.Anthropic(api_key=api_key)

          # Initialize the EmailArgumentSelector instance
    #def __init__(self):
        # Create an instance of the OpenAI ChatCompletion client
     #   self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        # Set the OpenAI API key
      #  api_key = "sk-None-3I0ZJzDw7rLx9868ws2fT3BlbkFJ0etzJSm1IZPz1Px6Fwry"
       # openai.api_key = api_key

    # Define the extract_arguments method to extract arguments from the adjuster's email
    def extract_arguments(self,adjuster_email):
        # Get the adjuster's email using the get_adjuster_email function
        # adjuster_email = get_adjuster_email(adjuster_email)
        return adjuster_email

    
    def summarize_arguments(self, adjuster_email,email_jest,full_arguments):
        # Specify the path to the system prompt file
        system_prompt_path = "ASE_systemprompt.txt"
        # Load the system prompt from the file
        system_prompt = load_system_prompt(system_prompt_path)
        
        # Define the user message
        user_message = f"""

        Content to Include:
        *This is the email directly from the adjuster. Please take it into context when writing your output:*
        {adjuster_email}

        *A rough summary of the overall flow and key points of the arguments, as provided below*
        {email_jest}

        *The complete, fleshed out arguments that you must incorporate into the email, as provided below:*
        {full_arguments}
        """
        
        # Create a list of messages for the OpenAI ChatCompletion API
        #messages = [
         #   {"role": "system", "content": system_prompt},
          #  {"role": "user", "content": user_message},
        #]

        # Call the create method of the OpenAI ChatCompletion client to generate a response
        #response = self.client.create(
         #   model="gpt-4o",  # Specify the model to use
          #  messages=messages  # Pass the list of messages
        #)

        # Send a message to the Claude 3 Opus model
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1500,
            temperature=0.2,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        # Extract the plain text summary from the response
        summary_email = response.content[0].text.strip()
        #summary_email = response.choices[0].message.content

        # Return the plain text summary
        return summary_email