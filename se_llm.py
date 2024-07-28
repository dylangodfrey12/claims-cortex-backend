
from Mfile_upload import load_system_prompt
from er_llm import ErIcGenerator
import re
import asyncio
from openai import OpenAI

class SeEvaluator:
    def __init__(self):
        # Initialize the OpenAI ChatCompletion client
        self.client = OpenAI(api_key="sk-None-3I0ZJzDw7rLx9868ws2fT3BlbkFJ0etzJSm1IZPz1Px6Fwry")
        
    async def SeDeterminer(self, measurements):
            user_message = f"""
            ```markdown
Please output an Xactimate estimate. Use the system prompt to determine the formulas needed to construct the line items.

Measurements:
{measurements}

Only output the line items and quantities that would be on the Xactimate estimate. Nothing else.

---

**Format Examples:**

**Example One of the Formatting:**

1: R&R Siding - aluminum (.024 thickness):

-**Quantity:** 1450.33 SF

2: House wrap (air/moisture barrier):

-**Quantity:** 1450.33 SF

3: Fanfold foam insulation board - 3/8"

-**Quantity:** 2900.66 SF

4: Scaffolding setup and take down - (per hour/section)

-**Quantity:** 4.00 Hr

---

**Example Two of the Formatting:**

1: R&R Siding - aluminum (.024 thickness):

-**Quantity:** 1,000.00 SF

2: House wrap (air/moisture barrier):

-**Quantity:** 1000.00 SF

3: Fanfold foam insulation board - 3/8"

-**Quantity:** 2000.00 SF

4: Scaffolding setup and take down - (per hour/section)

-**Quantity:** 6.00 Hr

---

**Example Three of the Formatting:**

1: R&R Siding - aluminum (.024 thickness):

-**Quantity:** 3500.50 SF

2: House wrap (air/moisture barrier):

-**Quantity:** 3500.50 SF

3: Fanfold foam insulation board - 3/8"

-**Quantity:** 7001.00 SF

4: Scaffolding setup and take down - (per hour/section)

-**Quantity:** 6.00 Hr

---

**Example Four of the Formatting:**

1: R&R Siding - aluminum (.024 thickness):

-**Quantity:** 300.50 SF

2: House wrap (air/moisture barrier):

-**Quantity:** 300.50 SF

3: Fanfold foam insulation board - 3/8"

-**Quantity:** 601.00 SF

4: Scaffolding setup and take down - (per hour/section)

-**Quantity:** 2.00 Hr
```

            """
            
            # Specify the path to the system prompt file
            system_prompt_path = "se_systemprompt.txt"
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
            return estimate
        
    # async def route_arguments_from_determiner(self,measurements, extracted_text, contractor_estimate, insurance_estimate, repair_type):
    #         er_ic_generator = ErIcGenerator()
    #         extracted_text = extracted_text.lower()
            
    #         if "full siding replacement" in extracted_text:
    #             return await er_ic_generator.IcDirectiveFullReplacement(contractor_estimate, insurance_estimate)
            
    #         if "elevation replacements" in extracted_text:
    #             return await er_ic_generator.IcDirectiveSingleReplacement(contractor_estimate, insurance_estimate, True, repair_type)


    async def run_and_compare_ic_determiner(self, measurements):

        first_task = asyncio.create_task(self.SeDeterminer(measurements))

        result2 = await self.SeDeterminer(measurements)

        if not first_task.done():
            result1 = await first_task
        else:
            result1 = first_task.result()

        if result1 == result2:
            return result1
        
        # If results differ, run again until a matching pair is found
        while True:
            result3 = await self.SeDeterminer(measurements)
            if result3 == result1 or result3 == result2:
                return result3
            await asyncio.sleep(1)  #avoid hitting API rate limits
           