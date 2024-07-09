#EASllm.py

#this script is responsible for determining which arguments to use for the given email presented
#it outputs a list of arguments that need to be used.
# EAS stands for "Email Argument Selector"


from openai import OpenAI
from email_upload import load_system_prompt

class EmailArgumentSelector:
    def __init__(self):
        self.client = OpenAI(api_key="sk-proj-aKV63t4s0QRHbWDNrzTRT3BlbkFJt1ZLd6RnSRu9ga6v9twf")


    def extract_arguments(self, adjuster_email):
        user_message = f"""
        Adjuster's email: {adjuster_email}

        Ensure the output are bulleted like so, anything else is wrong:
        -
        -
        -
        -
        -
        -
        """

        system_prompt_path = "EAS_systemprompt.txt"
        system_prompt = load_system_prompt(system_prompt_path)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o",  # Specify the model to use
            temperature=0, 
            messages=messages  # Pass the list of messages
        )

        email_arguments = response.choices[0].message.content

        return email_arguments
