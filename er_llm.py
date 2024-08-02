from openai import OpenAI
import re
import asyncio
from Xllm import XactimateExtractor
from Mllm import MeasurementExtractor
from Ellm import EstimateGenerator as ContractorEstimateGenerator
from Cllm import EstimateComparator
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
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
from sd_llm import SdEvaluator
from ESllm import summarize_email
from Mfile_upload import load_system_prompt

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


global_er_result = None
class ErIcGenerator:
    def __init__(self):
        # Initialize the OpenAI ChatCompletion client
        self.client = OpenAI(api_key="sk-None-3I0ZJzDw7rLx9868ws2fT3BlbkFJ0etzJSm1IZPz1Px6Fwry")
    # we need to determine if this is a single slope, individual repair, or full replacement
    
# Define the print_to_text_file method
    def print_to_text_file(self, text_to_print):
        with open('output.txt', 'a') as f:
            print(text_to_print, file=f)

    async def er_ic_determiner(self, measurements, contractor_estimate, insurance_estimate):
        user_message = f"""
        Please compare the contractor's estimate with the insurance company's estimate.
Use the following information for the comparison:

**Contractor's Estimate:**
{contractor_estimate}

**Insurance Company's Estimate:**
{insurance_estimate}

**Measurements Of The Property**
{measurements}

Only determine if the insurance company either paid for individual shingle repairs, individual slope repairs, or an entire roof replacement.

Do not output the quantities of the line items.

In the case the insurance company paid for a full roof replacement output
“Full Roof Replacement” as a Line item

In the case the insurance company paid for a slope replacement output
“slope replacement” as a Line item

In the case the insurance company paid for individual shingles output
“Individual shingle replacement” as a Line item

Output Format:
Explanation In Detail Of Your Reasoning:

Determination (should be in double brackets):

        """
        
        # Specify the path to the system prompt file
        system_prompt_path = "er_systemprompt.txt"
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
            temperature=0,# Specify the model to use
            messages=messages  # Pass the list of messages
        )
        # Extract the assistant's message content from the response
        repair_type = response.choices[0].message.content
        self.print_to_text_file(repair_type)
        global global_ser_result
        global_ser_result = repair_type
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
    
    async def route_arguments_from_determiner(self, extracted_text, contractor_estimate, insurance_estimate):
        extracted_text = extracted_text.lower()
        result = None
        if any(phrase in extracted_text for phrase in ["full roof replacement", "roof replacement"]):
            result = await self.IcDirectiveFullReplacement(contractor_estimate, insurance_estimate, True, False)
        
        if any(phrase in extracted_text for phrase in ["individual shingle repairs", "individual shingle repair", "individual shingle replacement",  "shingle repairs", "shingle repair"]):
            result = await self.IcDirectiveSingleReplacement(contractor_estimate, insurance_estimate, False, None, True)

        if any(phrase in extracted_text for phrase in ["individual slope repairs", "individual slope repair", "individual slope replacement", "slope repairs", "slope repair", "slope replacement"]):
            result = await self.IcDirectiveSingleReplacement(contractor_estimate, insurance_estimate, False, None, False)
        
        result = list(result)
        result.append(extracted_text)
        result = tuple(result)
        return result


    async def run_and_compare_ic_determiner(self, measurements, contractor_estimate, insurance_estimate):

        first_task = asyncio.create_task(self.er_ic_determiner(measurements, contractor_estimate, insurance_estimate))

        result2 = await self.er_ic_determiner(measurements, contractor_estimate, insurance_estimate)

        if not first_task.done():
            result1 = await first_task
        else:
            result1 = first_task.result()

        if result1 == result2:
            return result1
        
        # If results differ, run again until a matching pair is found
        while True:
            result3 = await self.er_ic_determiner(measurements, contractor_estimate, insurance_estimate)
            if result3 == result1 or result3 == result2:
                return result3
            await asyncio.sleep(1)  #avoid hitting API rate limits
            
    async def er_router(self, measurements, contractor_estimate, insurance_estimate):
        repairType = await self.run_and_compare_ic_determiner(measurements, contractor_estimate, insurance_estimate)
        result = self.route_arguments_from_determiner(repairType, measurements, contractor_estimate, insurance_estimate)
        return result
            
    # Ensure this method uses await for async function calls
    async def IcDirectiveFullReplacement(self, contractor_estimate, insurance_estimate, isRoofing:bool, isSiding: bool):
        comparator = EstimateComparator()
        summarizer = ArgumentSummarizer()

        # Compare the estimates using Cllm.py
        differences = comparator.compare_estimates(contractor_estimate, insurance_estimate)
        
        organized_arguments = await self.generate_and_organize_arguments(differences, isRoofing)
        
        # Process the retrieval (also async)
        full_arguments, full_evidence = await self.process_retrieval(organized_arguments)
        summary_text = summarizer.summarize_arguments(full_arguments,differences)
        # email_summary = summarize_email(differences, summary_text, full_arguments, isSiding)
        # audio_url = generate_audio(summary_text)
        audio_url = None
        return  summary_text,  full_evidence , audio_url, full_arguments, differences, organized_arguments

    # Ensure this method uses await for async function calls
    async def IcDirectiveSingleReplacement(self, contractor_estimate, insurance_estimate, isSiding: bool, differences_argument, isShingle: bool):
        differences = None
        # Compare the estimates using Cllm.py
        if(isSiding == True):
            differences = differences_argument
           
        # Use await to call the async function
        organized_arguments = await self.dispatch_arguments(isSiding, isShingle)
        # Process the retrieval (also async)
        full_arguments, full_evidence = await self.process_retrieval(organized_arguments)
        
        return self.er_summarize_email(differences, organized_arguments, full_arguments, full_evidence, isSiding, differences_argument, contractor_estimate, insurance_estimate) #todo remove constractor and insurance

    def er_summarize_email(self, differences, organized_arguments, full_arguments, full_evidence, isSiding: bool, repair_type, contractor_estimate, insurance_estimate):
            # Create an instance of the ArgumentSummarizer
            comparator = EstimateComparator()
            argument_summarizer = ArgumentSummarizer()
            summary_text = argument_summarizer.summarize_arguments(full_arguments, Difference=differences)
            # email_summary = summarize_email(differences, summary_text, full_arguments, isSiding)
            # audio_url = generate_audio(summary_text)
            audio_url = None
            if differences == None:
                differences = differences = comparator.compare_estimates(contractor_estimate, insurance_estimate)
                
            return summary_text, full_evidence , audio_url, full_arguments, differences, organized_arguments

    async def process_retrieval(self, organized_arguments):
        try:
            retrieval_processor = RetrievalProcessor()

            retrieval_processor.process_components(organized_arguments)

            retrieval_evidence_processor = RetrievalEvidenceProcessor()

            retrieval_evidence_processor.process_components(organized_arguments)

            return retrieval_processor.full_arguments, retrieval_evidence_processor.full_evidence
        except Exception as e:
            logger.error(f"Error in retrieval processing: {e}")
            raise e
        
    # Move these functions outside of the IcEvaluator class
    #  is_ss.py
    async def dispatch_arguments(self, isSiding, isShingle):
        try:
            argument_generator =  Argument_Selector_Is_Ss()

            if isShingle:
                arguments = argument_generator.se_generate_arguments()
            elif isSiding:
                arguments = argument_generator.ser_generate_arguments()
            else:
                arguments = argument_generator.generate_arguments()

            argument_organizer = ArgumentOrganizer()

            # Organize the arguments using AOllm.py
            organized_arguments = argument_organizer.organize_arguments(arguments)

            return organized_arguments
        except Exception as e:
            logger.error(f"Error in generating and organizing arguments: {e}")
            raise e
        
        
    async def generate_and_organize_arguments(self, differences, isRoofing):
        try:
            argument_generator = SdEvaluator()

            # Generate arguments based on the differences using Dllm.py
            arguments = await argument_generator.SdDeterminer(differences, isRoofing=isRoofing)

            argument_organizer = ArgumentOrganizer()

            # Organize the arguments using AOllm.py
            organized_arguments = argument_organizer.organize_arguments(arguments)

            return organized_arguments
        except Exception as e:
            logger.error(f"Error in generating and organizing arguments: {e}")
            raise e
            
