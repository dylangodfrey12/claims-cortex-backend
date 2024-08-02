
from Xllm import XactimateExtractor as InsuranceGenerator
from Mllm import MeasurementExtractor as MeasurementGenerator
from Ellm import EstimateGenerator as ContractorEstimateGenerator
from Mfile_upload import load_system_prompt
import config
from openai import OpenAI

class EstimateComparator:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def compare_estimates(self, contractor_estimate, insurance_estimate):
        # Define the user message with the estimates from Ellm.py and Xllm.py
        user_message = f"""
        Please compare the contractor's estimate with the insurance company's estimate. 
        Identify and output the line items that are present in the contractor's estimate but missing in the insurance company's estimate. 
        Use the following estimates for the comparison:

        **Contractor's Estimate:**
        {contractor_estimate}

        **Insurance Company's Estimate:**
        {insurance_estimate}

        Only output the line items that are present in the contractor's estimate but missing in the insurance company's estimate. 

        ## Rules:
        One: Ignore Siding panels and shingles. Meaning that if one of the line items that are different are siding panels or shingles do not output them as a difference.

        Two: Ignore methods of disposal of the shingles or siding, in the output.

        Three: Ignore anytime of felt paper or underlayment.

        Do not output the quantities of the line items.
        """
        
        # Specify the path to the system prompt file
        #system_prompt_path = "C_systemprompt.txt"
        # Load the system prompt from the file
            # Specify the path to the system prompt file
        system_prompt_path = "c_systemprompt.txt"
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
            messages=messages  # Pass the list of messages
        )
        # Extract the assistant's message content from the response
        differences = response.choices[0].message.content
        
        # Return the identified differences
        return differences