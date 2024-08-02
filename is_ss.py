# is_ss.py
# The purpose of the is_ss.py script is to serve as the Large Language Model (LLM) for 
# processing the output from er_llm.py and generating arguments based on the determined repair type. 
# The script focuses on organizing the identified differences into a structured list of arguments for further processing.

import config
from openai import OpenAI
from Mfile_upload import load_system_prompt

class Argument_Selector_Is_Ss:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def generate_arguments(self):
        
        arguments = '```\n- Single Slope Replacement Argument\n- Shingle Repairability\n- Maintaining Shingle Matching and Uniformity\n```'

        # Return the generated arguments
        return arguments
    
    def ser_generate_arguments(self):
        
        arguments = '```\n-Maintaining Siding Matching and Uniformity\n- Partial Siding Approval Repairability\n-Detach and Reset Aluminum Siding Argument\n```'

        # Return the generated arguments
        return arguments
    
    def se_generate_arguments(self):
        
        arguments = '```\n- Shingle Repairability\n- Maintaining Shingle Matching and Uniformity\n```'

        # Return the generated arguments
        return arguments   