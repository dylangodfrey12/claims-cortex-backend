
from Mfile_upload import load_system_prompt
from er_llm import ErIcGenerator
import re
import asyncio
from Xfile_upload import extract_text_from_pdf, get_pdf_path
import config
from openai import OpenAI

class SmEvaluator:
    def __init__(self):
        # Initialize the OpenAI ChatCompletion client
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        
    async def SmDeterminer(self, measurements_pdf_path):
            pdf_text = extract_text_from_pdf(measurements_pdf_path)

            user_message = f"""
Please output the measurements on the hover report. Use the system prompt to guide you on which measurements to remove.

For the hover measurements output them like this example below:

1. Siding Facades:** 1350.00 ft²
2. Siding Per Elevation
* Total Front: 345'
* Total Right: 350'
* Total Left: 380' 
* Total Back: 275'

The data must look identical to what the format. No changes can be made to the format. 
Do not use markdown or bolding either.
            """
            
            # Specify the path to the system prompt file
            system_prompt_path = "sm_systemprompt.txt"
            # Load the system prompt from the file
            system_prompt = load_system_prompt(system_prompt_path)
            
            # Create a list of messages for the chat
            messages = [
                {"role": "system", "content": system_prompt},  # Add the system prompt message
                {"role": "user", "content": user_message},
                {"role": "user", "content": f"PDF Text: {pdf_text}"}# Add the user message
            ]

            # Call the create method of the ChatCompletion client to get the response
            response = self.client.chat.completions.create(
                model="gpt-4o", 
                temperature=0, # Specify the model to use
                messages=messages  # Pass the list of messages
            )
            # Extract the assistant's message content from the response
            measurements = response.choices[0].message.content
            # Define the regex pattern
            # pattern = r"\[\[(.*?)\]\]"

            # # Search for the pattern in the input string
            # match = re.search(pattern, repair_type)

            # # Extract the matched text if found
            # if match:
            #     extracted_text = match.group(1)
            # else:
            #     extracted_text = None

            # Return the generated estimate
            return measurements
        
    # async def route_arguments_from_determiner(self,measurements, extracted_text, contractor_estimate, insurance_estimate, repair_type):
    #         er_ic_generator = ErIcGenerator()
    #         extracted_text = extracted_text.lower()
            
    #         if "full siding replacement" in extracted_text:
    #             return await er_ic_generator.IcDirectiveFullReplacement(contractor_estimate, insurance_estimate)
            
    #         if "elevation replacements" in extracted_text:
    #             return await er_ic_generator.IcDirectiveSingleReplacement(contractor_estimate, insurance_estimate, True, repair_type)


    async def run_and_compare_ic_determiner(self,estimate_pdf_path):

        first_task = asyncio.create_task(self.SmDeterminer(estimate_pdf_path))

        result2 = await self.SmDeterminer(estimate_pdf_path)

        if not first_task.done():
            result1 = await first_task
        else:
            result1 = first_task.result()

        if result1 == result2:
            return result1
        
        # If results differ, run again until a matching pair is found
        while True:
            result3 = await self.SmDeterminer(estimate_pdf_path)
            if result3 == result1 or result3 == result2:
                return result3
            await asyncio.sleep(1)  #avoid hitting API rate limits
           