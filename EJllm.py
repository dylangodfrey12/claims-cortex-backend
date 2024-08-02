#EJllm.py

#this script is responsible for roughly breaking down what the adjuster is saying and why
#it outputs what the adjuster is saying and why
# EJ stands for "Email Jest"


import config
from openai import OpenAI
# Import the load_system_prompt and get_adjuster_email functions from the email_upload module
from email_upload import load_system_prompt, get_adjuster_email

# Define the EmailArgumentSelector class
class EmailJest:
    # Initialize the EmailArgumentSelector instance
    def __init__(self):
        # Create an instance of the OpenAI ChatCompletion client
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)


    # Define the extract_arguments method to extract arguments from the adjuster's email
    def extract_arguments(self,adjuster_email):
        # Get the adjuster's email using the get_adjuster_email function

        # Define the user message that includes the adjuster's email and formatting instructions
        user_message = f"""
        Adjuster's email: {adjuster_email}

        Ensure the output  are bulleted like so, anything else is wrong:
        -
        -
        -
        -
        -
        -
        """

        # Specify the path to the system prompt file
        system_prompt_path = "EJ_systemprompt.txt"
        # Load the system prompt from the specified file using the load_system_prompt function
        system_prompt = load_system_prompt(system_prompt_path)

        # Create a list of messages for the OpenAI ChatCompletion API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        # Call the create method of the OpenAI ChatCompletion client to generate a response
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Specify the model to use
            temperature=0, 
            messages=messages  # Pass the list of messages
        )

        # Extract the generated arguments from the API response
        email_jest = response.choices[0].message.content

        # Return the extracted email arguments
        return email_jest
