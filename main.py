from fastapi.middleware.cors import CORSMiddleware
import threading
import os
import logging
from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
from typing import Optional
import nest_asyncio

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
from ESllm import summarize_email

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define models for requests
class VoiceRequest(BaseModel):
    summary: str

class EmailRequest(BaseModel):
    summary: str
    adjuster_email: str

@app.post("/summarize/")
async def summarize(
    estimate_pdf: UploadFile = File(...), 
    property_pdf: UploadFile = File(...), 
):
    try:
        logger.debug("Received request to summarize.")
        
        # Create a temporary directory
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save the uploaded PDFs temporarily in the temporary directory
        estimate_pdf_path = os.path.join(temp_dir, estimate_pdf.filename)
        property_pdf_path = os.path.join(temp_dir, property_pdf.filename)
        
        with open(estimate_pdf_path, "wb") as buffer:
            buffer.write(estimate_pdf.file.read())
        
        with open(property_pdf_path, "wb") as buffer:
            buffer.write(property_pdf.file.read())

        xactimate_extractor = XactimateExtractor()

        insurance_estimate = xactimate_extractor.extract_estimate(estimate_pdf_path)
        print("Insurance Company's Estimate:")
        print(insurance_estimate)
        print()

        measurement_extractor = MeasurementExtractor()
        contractor_measurements = measurement_extractor.extract_measurements(property_pdf_path)
        print("Extracted Measurements:")
        print(contractor_measurements)
        print()

        contractor_estimate_generator = ContractorEstimateGenerator()
        contractor_estimate = contractor_estimate_generator.generate_estimate(contractor_measurements)
        print("Contractor's Estimate:")
        print(contractor_estimate)
        print()

        comparator = EstimateComparator()

    # Compare the estimates using Cllm.py
        differences = comparator.compare_estimates(contractor_estimate, insurance_estimate)
        print("Differences between Contractor's and Insurance Company's Estimates:")
        print(differences)
        print()

    # Create an instance of the ArgumentGenerator from Dllm.py
        argument_generator = ArgumentSelector()

    # Generate arguments based on the differences using Dllm.py
        arguments = argument_generator.generate_arguments(differences)
        print("Selected Arguments to be Distributed to Master Models:")
        print(arguments)
        print()

    # Create an instance of the ArgumentOrganizer
        argument_organizer = ArgumentOrganizer()

    # Organize the arguments using AOllm.py
        organized_arguments = argument_organizer.organize_arguments(arguments)
        print("Organized Arguments:")
        print(organized_arguments)
        print()

    # Create an instance of the RetrievalProcessor
        retrieval_processor = RetrievalProcessor()

    # Process the organized arguments using R.py
        retrieval_processor.process_components(organized_arguments)
        print()

    # Print the full arguments
        print("Full Arguments:")
        print(retrieval_processor.full_arguments)

    # Create an instance of the ArgumentSummarizer
        argument_summarizer = ArgumentSummarizer()

    # Summarize the organized arguments using ASllm.py
        summary_text = argument_summarizer.summarize_arguments(organized_arguments)
        print("Summary of Arguments:")
        print(summary_text)
        print()

        retrieval_evidence_processor = RetrievalEvidenceProcessor()

          # Process the organized arguments using RE.py
        retrieval_evidence_processor.process_components(organized_arguments)
        print()

        # Print the full evidence
        print("Full Evidence:")
        print(retrieval_evidence_processor.full_evidence)

        # Remove the temporary files
        os.remove(estimate_pdf_path)
        os.remove(property_pdf_path)
        
        email_summary = summarize_email(differences, summary_text, retrieval_processor.full_arguments)
        print("Email Summary:")
        print(email_summary)
        print()

        audio_url = generate_audio(summary_text)
        
        logger.debug("Summary generated successfully.")
        
        return {"summary": summary_text, "email":email_summary, "links":retrieval_evidence_processor.full_evidence , "audio_url": audio_url}
    
    except Exception as e:
        logger.error(f"Error in summarizing: {e}")
        return {"error": str(e)}

@app.post("/generate-voice/")
async def generate_voice(summary: str = Form(...)):
    try:
        logger.debug("Received request to generate voice.")
        
        # Create a thread for audio generation
        audio_url = generate_audio(summary)
        
        logger.debug("Audio generated successfully.")
        
        return {"audio_url": audio_url}
    
    except Exception as e:
        logger.error(f"Error in generating voice: {e}")
        return {"error": str(e)}

@app.post("/generateFromEmail/")
async def generateFrpmEmail(adjuster_email: str = Form(...)):
    try:
        logger.debug("Received request to generate email.")
        
        email_argument_selector = EmailArgumentSelector()
        email_arguments = email_argument_selector.extract_arguments(adjuster_email)
        print("Arguments Extracted from Adjuster's Email:")
        print(email_arguments)

        email_jest = EmailJest()
        adjuster_jest = email_jest.extract_arguments(adjuster_email)

        retrieval_processor = RetrievalProcessor()
        retrieval_processor.process_components(email_arguments)

        argument_summarizer_email = ArgumentSummarizerEmail()
        adjuster_email_arguments = argument_summarizer_email.extract_arguments(adjuster_email)
        summary = argument_summarizer_email.summarize_arguments(adjuster_email_arguments, email_jest, retrieval_processor.full_arguments)

        retrieval_evidence_processor = RetrievalEvidenceProcessor()

         # Process the organized arguments using RE.py
        retrieval_evidence_processor.process_components(email_arguments)
        print()

        # Print the full evidence
        print("Full Evidence:")
        print(retrieval_evidence_processor.full_evidence)
        
        Full_Email_Argument = EmaiFromEmail()
        final_email = Full_Email_Argument.the_email_arguments(summary, adjuster_email, email_jest, retrieval_processor.full_arguments)

        logger.debug("Email generated successfully.")
        print("Email To Adjuster:")
        print(final_email)

        audio_url = generate_audio(summary)
        
        return {"message": "Email generated successfully", "summary": summary,"email":final_email,"links":retrieval_evidence_processor.full_evidence, "audio_url": audio_url}
    
    except Exception as e:
        logger.error(f"Error in generating email: {e}")
        return {"error": str(e)}

