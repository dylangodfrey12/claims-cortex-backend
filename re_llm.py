
from Mfile_upload import load_system_prompt
from er_llm import ErIcGenerator
import re
import asyncio
from openai import OpenAI

class ReEvaluator:
    def __init__(self):
        # Initialize the OpenAI ChatCompletion client
        self.client = OpenAI(api_key="sk-proj-aKV63t4s0QRHbWDNrzTRT3BlbkFJt1ZLd6RnSRu9ga6v9twf")
        
    async def ReDeterminer(self, measurements):
            user_message = f"""
                   ```markdown
                ```markdown
        Please output an Xactimate estimate. Use the system prompt to determine the formulas needed to construct the line items.

        Measurements:
        {measurements}

        Only output the line items and quantities that would be on the Xactimate estimate. Nothing else.

        ---

        **Format Examples:**

        **Example One of the Formatting:**

        1: Remove 3 tab - 25 yr. - composition shingle roofing - incl. felt:

        -**Quantity:** 0.33SQ

        2: tab - 25 yr. - comp. shingle roofing - w/out felt:

        -**Quantity:** 0.33SQ

        3: Remove Additional charge for high roof (2 stories or greater)

        -**Quantity:** 20.07 SQ

        4: Asphalt starter - universal starter course

        -**Quantity:** 135.00 LF

        5: Ridge cap - composition shingles

        -**Quantity:** 14.00 LF

        6: Drip Edge

        -**Quantity:** 321.00 LF

        7: Flashing - Pipe Jack

        -**Quantity:** 321.00 LF

        8: Continuous ridge vent - aluminum

        -**Quantity:** 54.00 LF

        ---

        **Example Two of the Formatting:**

        1: Tear off, haul and dispose of comp. shingles - 3 tab

        -**Quantity:** 20.24 SQ

        2: Roofing felt - 15 lb.

        -**Quantity:** 14.68 SQ

        3: Roofing felt - 15 lb

        -**Quantity:** 5.56 SQ

        4: 3 tab - 25 yr. - comp. shingle roofing - w/out felt

        -**Quantity:** 0.67 SQ

        5: 3 tab - 25 yr. - comp. shingle roofing - w/out felt

        -**Quantity:** 22.00 SQ

        6: 3 tab - 25 yr. - comp. shingle roofing - w/out felt

        -**Quantity:** 0.67 SQ

        7: Flashing - Pipe Jack

        -**Quantity:** 3.00 EA

        8: R&R Chimney flashing - average (32" x 36")

        -**Quantity:** 1.00 EA

        9: Drip Edge

        -**Quantity:** 229.05 LF

        10: Ice & water barrier

        -**Quantity:** 556.00 SF

        ---

        **Example Three of the Formatting:**

        1: Remove 3 tab - 25 yr. - composition shingle roofing (per SHINGLE)

        -**Quantity:** 12.00 EA

        2: 3 tab - 25 yr. - composition shingle roofing (per SHINGLE)

        -**Quantity:** 12.00 EA

        ---

        **Example Four of the Formatting:**

        1: Tear off, haul and dispose of comp. shingles - 3 tab

        -**Quantity:** 12.70 SQ

        2: Remove Additional charge for high roof (2 stories or greater)

        -**Quantity:** 3.91 SQ

        3: Remove Additional charge for steep roof - 7/12 to 9/12 slope

        -**Quantity:** 0.09 SQ

        4: Roofing felt - 15 lb

        -**Quantity:** 10.37 SQ

        5: 3 tab - 25 yr. - comp. shingle roofing - w/out felt

        -**Quantity:** 0.33 SQ

        6: 3 tab - 25 yr. - comp. shingle roofing - w/out felt

        -**Quantity:** 0.67 SQ

        7: 3 tab - 25 yr. - comp. shingle roofing - w/out felt

        -**Quantity:** 14.00 SQ

        8: 3 tab - 25 yr. - comp. shingle roofing - w/out felt

        -**Quantity:** 0.33 SQ

        9: Additional charge for high roof (2 stories or greater)

        -**Quantity:** 3.91 SQ

        10: Additional charge for steep roof - 7/12 to 9/12 slope

        -**Quantity:** 0.09 SQ

        11: Continuous ridge vent - aluminum

        -**Quantity:** 27.75 LF

        12: Flashing - pipe jack

        -**Quantity:** 2.00 EA

        13: R&R Drip edge

        -**Quantity:** 189.17 LF

        14: Digital satellite system - Detach & reset

        -**Quantity:** 1.00 EA

        15: Digital satellite system - alignment and calibration only

        -**Quantity:** 1.00 EA

        16: R&R Power attic vent cover only - metal

        -**Quantity:** 1.00 EA

        17: Roofer - per hour

        -**Quantity:** 1.00 HR

        18: Ice & water barrier

        -**Quantity:** 233.05 SF
        ```

            """
            
            # Specify the path to the system prompt file
            system_prompt_path = "re_systemprompt.txt"
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
            estimate = response.choices[0].message.content
            # # Define the regex pattern
            # pattern = r"\[\[(.*?)\]\]"

            # # Search for the pattern in the input string
            # match = re.search(pattern, repair_type)

            # # Extract the matched text if found
            # if match:
            #     extracted_text = match.group(1)
            # else:
            #     extracted_text = None

            # Return the generated estimate
            return estimate
        
    # async def route_arguments_from_determiner(self,measurements, extracted_text, contractor_estimate, insurance_estimate, repair_type):
    #         er_ic_generator = ErIcGenerator()
    #         extracted_text = extracted_text.lower()
            
    #         if "full siding replacement" in extracted_text:
    #             return await er_ic_generator.IcDirectiveFullReplacement(contractor_estimate, insurance_estimate)
            
    #         if "elevation replacements" in extracted_text:
    #             return await er_ic_generator.IcDirectiveSingleReplacement(contractor_estimate, insurance_estimate, True, repair_type)


    async def run_and_compare_ic_determiner(self, measurements):

        first_task = asyncio.create_task(self.ReDeterminer(measurements))

        result2 = await self.ReDeterminer(measurements)

        if not first_task.done():
            result1 = await first_task
        else:
            result1 = first_task.result()

        if result1 == result2:
            return result1
        
        # If results differ, run again until a matching pair is found
        while True:
            result3 = await self.ReDeterminer(measurements)
            if result3 == result1 or result3 == result2:
                return result3
            await asyncio.sleep(1)  #avoid hitting API rate limits
           