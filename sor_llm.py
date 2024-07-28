from openai import OpenAI
import re
import asyncio
import logging
import time
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from Xllm import XactimateExtractor
from Mllm import MeasurementExtractor
from Ellm import EstimateGenerator as ContractorEstimateGenerator
from Cllm import EstimateComparator
from er_llm import ErIcGenerator
from ser_llm import SerEvaluator
from Xfile_upload import extract_text_from_pdf as extract_text_from_xfile
from Mfile_upload import extract_text_from_pdf as extract_text_from_mfile
from EASllm import EmailArgumentSelector
from EJllm import EmailJest
from RA import RetrievalProcessor
from ASEllm import ArgumentSummarizerEmail
from EFEllm import EmaiFromEmail
from voice import generate_audio
from RE import RetrievalEvidenceProcessor
from openlink import open_links
from Xllm import XactimateExtractor
from Mllm import MeasurementExtractor
from Ellm import EstimateGenerator as ContractorEstimateGenerator
from Cllm import EstimateComparator
from Dllm import ArgumentSelector
from AOllm import ArgumentOrganizer
from ASllm import ArgumentSummarizer
from is_ss import Argument_Selector_Is_Ss
from sm_llm import SmEvaluator
from se_llm import SeEvaluator
from rm_llm import RmEvaluator
from re_llm import ReEvaluator
from ESllm import summarize_email
from Mfile_upload import load_system_prompt
from langsmith.wrappers import wrap_openai
from langsmith import traceable

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SorEvaluator:
    def __init__(self):
        # Initialize the OpenAI ChatCompletion client
        self.client = wrap_openai(OpenAI(api_key="sk-None-3I0ZJzDw7rLx9868ws2fT3BlbkFJ0etzJSm1IZPz1Px6Fwry"))
    async def sor_ic_determiner(self, insurance_estimate):
        user_message = f"""
       Please review the estimate from the insurance company to determine if it is a roofing estimate or a siding estimate.
        Use the following information for the comparison:

        **Insurance Company's Estimate:**
        {insurance_estimate}

        Only determine if the insurance company either paid for siding job or a roofing job.

        Do not output the quantities of the line items.

        In the case the insurance company paid for a roof job output
        “Roofing Estimate” as a Line item.

        In the case the insurance company paid for a siding job output
        “Siding Estimate” as a Line item.

        Output Format:
        Explanation In Detail Of Your Reasoning:

        Determination (should be in double brackets):

        """
        # Load the system prompt from the file
        system_prompt = "follow the prompt"
        
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
        repair_type = response.choices[0].message.content
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
    
    async def run_and_compare_ic_determiner(self, insurance_estimate):
        first_task = asyncio.create_task(self.sor_ic_determiner(insurance_estimate))

        result2 = await self.sor_ic_determiner(insurance_estimate)

        if not first_task.done():
            result1 = await first_task
        else:
            result1 = first_task.result()

        if result1 == result2:
            return result1
        
        while True:
            result3 = await self.sor_ic_determiner(insurance_estimate)
            if result3 == result1 or result3 == result2:
                return result3
            await asyncio.sleep(1)  # avoid hitting API rate limits
    
    async def route_arguments_from_determiner(self,repair_type, insurance_estimate, measurements_pdf_path):
        repair_type = repair_type.lower()
        
        if "roofing" in repair_type:
            return await roofing_llm_router( insurance_estimate, measurements_pdf_path)
        
        if "siding" in repair_type:
            return await siding_llm_router( insurance_estimate, repair_type, measurements_pdf_path)

                
# async def er_llm_router(measurements, contractor_estimate, insurance_estimate):
#         ic_director = ErIcGenerator()
#         # returns IC type
#         ic_director_type = await ic_director.run_and_compare_ic_determiner(measurements, contractor_estimate, insurance_estimate)
#         email_summary_result = await ic_director.route_arguments_from_determiner(ic_director_type, contractor_estimate, insurance_estimate)
#         return email_summary_result
    
# async def ser_llm_router(measurements, contractor_estimate, insurance_estimate, repair_type):
#         ser_evaluator = SerEvaluator()
#         # returns IC type
#         ic_director_type = await ser_evaluator.run_and_compare_ic_determiner(measurements, contractor_estimate, insurance_estimate)
#         email_summary_result = await ser_evaluator.route_arguments_from_determiner(measurements, ic_director_type, contractor_estimate, insurance_estimate, repair_type)
#         return email_summary_result

async def siding_llm_router( insurance_estimate, repair_type, measurements_pdf_path):
        sm_evaluator = SmEvaluator()
        se_evaluator = SeEvaluator()
        ser_evaluator = SerEvaluator()
        # returns measurements
        sm_measurements = await sm_evaluator.run_and_compare_ic_determiner(measurements_pdf_path)
        constractor_estimate = await se_evaluator.run_and_compare_ic_determiner(sm_measurements)
        extracted_response = await ser_evaluator.run_and_compare_ic_determiner(sm_measurements, constractor_estimate, insurance_estimate)

        email_summary_result = await ser_evaluator.route_arguments_from_determiner( extracted_response, constractor_estimate, insurance_estimate, repair_type)
        return email_summary_result
    
async def roofing_llm_router( insurance_estimate, measurements_pdf_path):
        rm_evaluator = RmEvaluator()
        re_evaluator = ReEvaluator()
        er_evaluator = ErIcGenerator()
        # returns IC type
        roofing_measurements = await rm_evaluator.run_and_compare_ic_determiner(measurements_pdf_path)
        contractor_estimate = await re_evaluator.ReDeterminer(roofing_measurements)
        extracted_response = await er_evaluator.run_and_compare_ic_determiner(roofing_measurements, contractor_estimate, insurance_estimate)

        email_summary_result = await er_evaluator.route_arguments_from_determiner(extracted_response,  contractor_estimate, insurance_estimate)
        return email_summary_result
    
async def main():
    evaluator = SorEvaluator()
    measurements = "Lorum who gives af" 
    contractor_estimate = "idc"
    insurance_estimate = "idgaf this doesnt work anyways"

    result = await evaluator.run_and_compare_ic_determiner(measurements, contractor_estimate, insurance_estimate)
    print(f"Final Matching Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
