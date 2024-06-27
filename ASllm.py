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
    
    def summarize_arguments(self, arguments):
        # Specify the path to the system prompt file
        system_prompt_path = "AS_systemprompt.txt"
        # Load the system prompt from the file
        system_prompt = load_system_prompt(system_prompt_path)
        
        # Define the user message
        user_message = f"Please follow the system prompt based on the following \n\n{arguments}"
        
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
        summary_text = response.content[0].text.strip()
        
        # Return the plain text summary
        return summary_text

    