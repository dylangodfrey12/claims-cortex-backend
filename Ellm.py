# Ellm.py

# This script serves as the Large Language Model (LLM) turning measurements from Mllm.py into an internal
# Xactimate estimate
# The prefix "E" stands for Estimate.

from openai import OpenAI
from Mfile_upload import load_system_prompt

class EstimateGenerator:
    def __init__(self):
        # Initialize the OpenAI ChatCompletion client
        self.client = OpenAI(api_key="sk-None-3I0ZJzDw7rLx9868ws2fT3BlbkFJ0etzJSm1IZPz1Px6Fwry")
    
    def generate_estimate(self, measurements):
        # Define the user message with the measurements from Mllm.py
        user_message = f"""
        ```markdown
Please output a Xactimate Roofing Estimate OR a Xactimate Siding estimate. **DO NOT MIX AND MATCH**. Use the system prompt to determine the formulas needed to construct the line items.

Measurements:
{measurements}

Only output the line items and quantities that would be on the Xactimate estimate. Nothing else.

---

**Format Examples:**

**Example One of the Formatting a Roofing Estimate:**

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

**Example Two of the Formatting Roofing Estimate:**

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

**Example Three of the Formatting Roofing Estimate:**

1: Remove 3 tab - 25 yr. - composition shingle roofing (per SHINGLE)

-**Quantity:** 12.00 EA

2: 3 tab - 25 yr. - composition shingle roofing (per SHINGLE)

-**Quantity:** 12.00 EA

---

**Example Four of the Formatting Roofing Estimate:**

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

_______________________________________________________________________________________________________________________

**Format Examples For Siding Estimates:**

**Example One of the Formatting Siding Estimates:**

1: R&R Siding - aluminum (.024 thickness):

-**Quantity:** 1450.33 SF

2: House wrap (air/moisture barrier):

-**Quantity:** 1450.33 SF

3: Fanfold foam insulation board - 3/8"

-**Quantity:** 2900.66 SF

4: Scaffolding setup and take down - (per hour/section)

-**Quantity:** 4.00 Hr

---

**Example Two of the Formatting Siding Estimates:**

1: R&R Siding - aluminum (.024 thickness):

-**Quantity:** 1,000.00 SF

2: House wrap (air/moisture barrier):

-**Quantity:** 1000.00 SF

3: Fanfold foam insulation board - 3/8"

-**Quantity:** 2000.00 SF

4: Scaffolding setup and take down - (per hour/section)

-**Quantity:** 6.00 Hr

---

**Example Three of the Formatting Siding Estimates:**

1: R&R Siding - aluminum (.024 thickness):

-**Quantity:** 3500.50 SF

2: House wrap (air/moisture barrier):

-**Quantity:** 3500.50 SF

3: Fanfold foam insulation board - 3/8"

-**Quantity:** 7001.00 SF

4: Scaffolding setup and take down - (per hour/section)

-**Quantity:** 6.00 Hr

---

**Example Four of the Formatting Siding Estimates:**

1: R&R Siding - aluminum (.024 thickness):

-**Quantity:** 300.50 SF

2: House wrap (air/moisture barrier):

-**Quantity:** 300.50 SF

3: Fanfold foam insulation board - 3/8"

-**Quantity:** 601.00 SF

4: Scaffolding setup and take down - (per hour/section)

-**Quantity:** 2.00 Hr
```


```


        """
        
        # Specify the path to the system prompt file
        system_prompt_path = "E_systemprompt.txt"
        # Load the system prompt from the file
        system_prompt = load_system_prompt(system_prompt_path)
        
        # Create a list of messages for the chat
        messages = [
            {"role": "system", "content": system_prompt},  # Add the system prompt message
            {"role": "user", "content": user_message},  # Add the user message
        ]

        # Call the create method of the ChatCompletion client to get the response
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Specify the model to use
            temperature=0,
            messages=messages  # Pass the list of messages
        )
        # Extract the assistant's message content from the response
        estimate = response.choices[0].message.content
        
        # Return the generated estimate
        return estimate