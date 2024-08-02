# ASllm.py

# This script summarize the arguments so we understand how they will be connected 
# The prefix "AS" stands for Argument Summarizer.

import anthropic
from Mfile_upload import load_system_prompt

class ArgumentSummarizer:
    def __init__(self):
        # Initialize the Anthropic client
        api_key = "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"
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def summarize_arguments(self, full_arguments, Difference):
        # Specify the path to the system prompt file
        system_prompt_path = "AS_systemprompt.txt"
        # Load the system prompt from the file
        system_prompt = load_system_prompt(system_prompt_path)
        
        # Define the user message
        user_message = f"""
        ### General Rules to follow:
            **Rule One**: You are supposed to act like you are in person talking with the contractor you are helping. You are not writing an email to the contractor you are helping.

            Content to Include:
            *The specific missing items that need to be argued for, as indicated by what is below ensure these are idendical in the output as they are in the input:*
            {Difference}

            *The complete, fleshed out arguments that you must incorporate into the email, as provided below:*
            {full_arguments}
"""
        
        # Send a message to the Claude 3 Opus model
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0.2,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        # Extract the plain text summary from the response
        summary_text = response.content[0].text.strip()
        
        # Return the plain text summary
        return summary_text

    