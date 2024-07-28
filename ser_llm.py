
from Mfile_upload import load_system_prompt
from er_llm import ErIcGenerator
import re
import asyncio
from openai import OpenAI

class SerEvaluator:
    def __init__(self):
        # Initialize the OpenAI ChatCompletion client
        self.client = OpenAI(api_key="sk-None-3I0ZJzDw7rLx9868ws2fT3BlbkFJ0etzJSm1IZPz1Px6Fwry")


    def print_to_text_file(self, text_to_print):
        with open('output.txt', 'a') as f:
            print(text_to_print, file=f)
            
    async def SerDeterminer(self, measurements, contractor_estimate, insurance_estimate):
            user_message = f"""
                    Please compare the contractor's estimate with the insurance company's estimate.
                    Use the following information for the comparison:

                    **Contractor's Estimate:**
                    {contractor_estimate}

                    **Insurance Company's Estimate:**
                    {insurance_estimate}

                    **Measurements Of The Property**
                    {measurements}

                    Only determine if the insurance company either paid for Full Siding Replacements or Elevation Replacements.

                    Do not output the quantities of the line items.

                    In the case the insurance company paid for a full roof replacement output
                    “Full Siding Replacement” as a Line item.

                    In the case the insurance company paid for individual shingles output
                    “Elevation Replacements” as a Line item.

                    Output Format:
                    Explanation In Detail Of Your Reasoning:

                    Determination (should be in double brackets):
            """
            
            # Specify the path to the system prompt file
            system_prompt_path = "ser_systemprompt.txt"
            # Load the system prompt from the file
            system_prompt = load_system_prompt(system_prompt_path)
            
            # Create a list of messages for the chat
            messages = [
                {"role": "system", "content": system_prompt},  # Add the system prompt message
                {"role": "user", "content": user_message},  # Add the user message
            ]

            # Call the create method of the ChatCompletion client to get the response
            response =  self.client.chat.completions.create(
                model="gpt-4o", 
                temperature=0, # Specify the model to use
                messages=messages  # Pass the list of messages
            )
            # Extract the assistant's message content from the response
            repair_type = response.choices[0].message.content
            self.print_to_text_file(repair_type)
            # Define the regex pattern
            pattern = r"\[\[(.*?)\]\]"

            # Search for the pattern in the input string
            match = re.search(pattern, repair_type)

            # Extract the matched text if found
            if match:
                extracted_text = match.group(1)
            else:
                extracted_text = None

            # Return the generated estimate
            return extracted_text
        
    async def route_arguments_from_determiner(self, extracted_text, contractor_estimate, insurance_estimate, repair_type):
            er_ic_generator = ErIcGenerator()
            extracted_text = extracted_text.lower()
            
            if "full siding replacement" in extracted_text:
                return await er_ic_generator.IcDirectiveFullReplacement(contractor_estimate, insurance_estimate, False, True)
            
            if "elevation replacements" in extracted_text:
                return await er_ic_generator.IcDirectiveSingleReplacement(contractor_estimate, insurance_estimate, True, repair_type, False)


    async def run_and_compare_ic_determiner(self, measurements, contractor_estimate, insurance_estimate):

        first_task = asyncio.create_task(self.SerDeterminer(measurements, contractor_estimate, insurance_estimate))

        result2 = await self.SerDeterminer(measurements, contractor_estimate, insurance_estimate)

        if not first_task.done():
            result1 = await first_task
        else:
            result1 = first_task.result()

        if result1 == result2:
            return result1
        
        # If results differ, run again until a matching pair is found
        while True:
            result3 = await self.SerDeterminer(measurements, contractor_estimate, insurance_estimate)
            if result3 == result1 or result3 == result2:
                return result3
            await asyncio.sleep(1)  #avoid hitting API rate limits
           