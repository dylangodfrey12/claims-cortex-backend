
from Mfile_upload import load_system_prompt
import re
import asyncio
import config
from openai import OpenAI

class SdEvaluator:
    def __init__(self):
        # Initialize the OpenAI ChatCompletion client
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
       
    def print_to_text_file(self, text_to_print):
        with open('output.txt', 'a') as f:
            print(text_to_print, file=f) 
            
    async def SdDeterminer(self, differences, isRoofing:bool):
            user_message = f"""
                            {differences}

        Ensure that each argument category is listed only once in the output, even if multiple line items map to the same argument.

        Ensure the output is only the difference and they are bulleted like so, anything else is wrong:
        Ensure that every bullet point has an associated output or argument. Do not include any empty bullet points.
        -
        -
        -
        -
        -
        -
            """
            
            # Specify the path to the system prompt file
            # Load the system prompt from the file
            if isRoofing:
                    system_prompt_path = "rd_systemprompt.txt"
            else:
                    system_prompt_path = "sd_systemprompt.txt"
                    
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
            arguments = response.choices[0].message.content
            # Define the regex pattern
            # pattern = r"\[\[(.*?)\]\]"
            self.print_to_text_file("sdllm")
            self.print_to_text_file(arguments)
            # # Search for the pattern in the input string
            # match = re.search(pattern, response)

            # # Extract the matched text if found
            # if match:
            #     arguments = match.group(1)
            # else:
            #     arguments = None

            # Return the generated estimate
            return arguments
        
    # async def route_arguments_from_determiner(self,measurements, extracted_text, contractor_estimate, insurance_estimate, repair_type):
    #         er_ic_generator = ErIcGenerator()
    #         extracted_text = extracted_text.lower()
            
    #         if "full siding replacement" in extracted_text:
    #             return await er_ic_generator.IcDirectiveFullReplacement(contractor_estimate, insurance_estimate)
            
    #         if "elevation replacements" in extracted_text:
    #             return await er_ic_generator.IcDirectiveSingleReplacement(contractor_estimate, insurance_estimate, True, repair_type)


    async def run_and_compare_ic_determiner(self, measurements, contractor_estimate, insurance_estimate):

        first_task = asyncio.create_task(self.SdDeterminer(measurements, contractor_estimate, insurance_estimate))

        result2 = await self.SdDeterminer(measurements, contractor_estimate, insurance_estimate)

        if not first_task.done():
            result1 = await first_task
        else:
            result1 = first_task.result()

        if result1 == result2:
            return result1
        
        # If results differ, run again until a matching pair is found
        while True:
            result3 = await self.SdDeterminer(measurements, contractor_estimate, insurance_estimate)
            if result3 == result1 or result3 == result2:
                return result3
            await asyncio.sleep(1)  #avoid hitting API rate limits
           