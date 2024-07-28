# ESEllm.py

# This script will create the email that will be sent from the adjuster 
# The prefix "ESE" stands for Email From Email.

import anthropic
from openai import OpenAI
from email_upload import load_system_prompt, get_adjuster_email

class EmaiFromEmail:
    def __init__(self):
        # Initialize the Anthropic client
        api_key = "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"
        self.client = anthropic.Anthropic(api_key=api_key)

          # Initialize the EmailArgumentSelector instance
    #def __init__(self):
        # Create an instance of the OpenAI ChatCompletion client
     #   self.client = OpenAI(api_key="sk-None-3I0ZJzDw7rLx9868ws2fT3BlbkFJ0etzJSm1IZPz1Px6Fwry")
        # Set the OpenAI API key
      #  api_key = "sk-None-3I0ZJzDw7rLx9868ws2fT3BlbkFJ0etzJSm1IZPz1Px6Fwry"
       # openai.api_key = api_key

    # Define the extract_arguments method to extract arguments from the adjuster's email
    def extract_arguments(self):
        # Get the adjuster's email using the get_adjuster_email function
        adjuster_email = get_adjuster_email()
        return adjuster_email

    
    def the_email_arguments(self, adjuster_email,email_jest,full_arguments,summary):
        # Specify the path to the system prompt file
        system_prompt_path = "EFE_systemprompt.txt"
        # Load the system prompt from the file
        system_prompt = load_system_prompt(system_prompt_path)
        
        # Define the user message
        user_message = f""" Structure of the Email:
        *Open by noting that you have read listing the items you believe should be included in totality before getting into the detailed arguments. Don't reveal the specific argument titles, but give an overview of what you will be arguing and why.*
        *For each item/argument, explain the relevant code requirements and manufacturing requirements. Refer to reputable sources and evidence to support your points.*
        *Use transitions like "Because of this, we now must consider..." to create a logical flow and natural progression between arguments.*
        *After covering the main points, note that you have provided more in-depth justifications with third-party evidence below for them to reference if needed.*
        *Close by reiterating your key arguments and recommendations in a concise, friendly manner.*

        Tone and Style:
        *Write in a conversational, friendly, and professional tone as if speaking to a friend in person. Be kind and relaxed but never rude.*
        *Demonstrate that you have carefully reviewed the information they submitted, including details about the insurance claim and associated paperwork. Base your justifications on these documents.*
        *Get straight to the point about the arguments you will make. Present them directly in the email body rather than in a bulleted list.*

        Content to Include:
        *This is the email directly from the adjuster. Please take it into context when writing your output:*
        {adjuster_email}

        *A rough summary explaining what the adjuster was trying to say and their perspective, as provided below*
        {email_jest}

        *The complete, fleshed out arguments that you must incorporate into the email, as provided below:*
        {full_arguments}

        *A rough summary of the overall flow and key points of the arguments, as provided below*
        {summary}
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
            model="claude-3-opus-20240229",
            max_tokens=1000,
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