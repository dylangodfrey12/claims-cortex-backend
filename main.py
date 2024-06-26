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


        # estimate_text = extract_text_from_xfile(estimate_pdf_path)
        # property_text = extract_text_from_mfile(property_pdf_path)
        
        # Remove the temporary files
        os.remove(estimate_pdf_path)
        os.remove(property_pdf_path)
        
        # Combine texts
        # combined_text = f"{estimate_text}\n{property_text}\n{adjuster_text}"
        
        # Generate summary
        # summary = summarize_text(combined_text)

        email_summary = summarize_email(differences, summary_text,  retrieval_processor.full_arguments)
        print("Email Summary:")
        print(email_summary)
        print()

        # audio=generate_audio(email_summary)
        
        logger.debug("Summary generated successfully.")
        
        return {"summary": email_summary}
    
    except Exception as e:
        logger.error(f"Error in summarizing: {e}")
        return {"error": str(e)}

@app.post("/generate-voice/")
async def generate_voice(summary: str = Form(...)):
    try:
        logger.debug("Received request to generate voice.")
        
        # Create a thread for audio generation
        audio_thread = threading.Thread(target=generate_audio_thread, args=(summary,))
        audio_thread.start()
        audio_thread.join()
        
        logger.debug("Audio generated successfully.")
        
        return {"message": "Audio generated successfully"}
    
    except Exception as e:
        logger.error(f"Error in generating voice: {e}")
        return {"error": str(e)}

@app.post("/generate-email/")
async def generate_email(
    adjuster_email: str = Form(...)
):
    try:
        logger.debug("Received request to generate email.")
        
        # Create an instance of the EmailArgumentSelector
        email_argument_selector = EmailArgumentSelector()

        # Extract arguments from the adjuster's email using EASllm.py
        email_arguments = email_argument_selector.extract_arguments(adjuster_email)

        print("Arguments Extracted from Adjuster's Email:")
        print(email_arguments)

        # Create an instance of the EmailJest
        email_jest = EmailJest()

        # Extract what the adjuster is saying and why using EJllm.py
        adjuster_jest = email_jest.extract_arguments(adjuster_email)

        # Create an instance of the RetrievalProcessor
        retrieval_processor = RetrievalProcessor()

        # Process the organized arguments using R.py
        retrieval_processor.process_components(email_arguments)

        # Create an instance of the ArgumentSummarizerEmail
        argument_summarizer_email = ArgumentSummarizerEmail()

        # Extract arguments from the adjuster's email using the extract_arguments method
        adjuster_email_arguments = argument_summarizer_email.extract_arguments(adjuster_email)

        summary = argument_summarizer_email.summarize_arguments(adjuster_email_arguments, email_jest, retrieval_processor.full_arguments)
        

        # Generate the email using the summary and adjuster_email passed to the function
        Full_Email_Argument = EmaiFromEmail()
        final_email = Full_Email_Argument.the_email_arguments(summary, adjuster_email, email_jest, retrieval_processor.full_arguments)

        logger.debug("Email generated successfully.")
        print("Email To Adjuster:")
        print(final_email)

        audio_data=generate_audio(final_email)
        
        
        return {"message": "Email generated successfully", "summary": final_email,"audio":audio_data}
    
    except Exception as e:
        logger.error(f"Error in generating email: {e}")
        return {"error": str(e)}

def summarize_text(combined_text: str) -> str:
    try:
        logger.debug("Starting text summarization.")
        
        # Initialize the required instances
        email_argument_selector = EmailArgumentSelector()
        email_jest = EmailJest()
        retrieval_processor = RetrievalProcessor()
        argument_summarizer_email = ArgumentSummarizerEmail()

        # Extract arguments from the combined text (adjuster's email part)
        adjuster_email_arguments = email_argument_selector.extract_arguments()

        # Extract what the adjuster is saying and why using EJllm.py
        adjuster_jest = email_jest.extract_arguments()

        # Process the organized arguments using R.py
        retrieval_processor.process_components(adjuster_email_arguments)

        # Summarize the arguments
        summary = argument_summarizer_email.summarize_arguments(adjuster_email_arguments, adjuster_jest, retrieval_processor.full_arguments)
        
        logger.debug("Text summarization completed.")
        
        return summary
    
    except Exception as e:
        logger.error(f"Error in text summarization: {e}")
        raise e

def generate_audio_thread(summary):
    try:
        logger.debug("Starting audio generation.")
        generate_audio(summary)
        logger.debug("Audio generation completed.")
    except Exception as e:
        logger.error(f"Error in audio generation: {e}")
        raise e

def generate_email_thread(summary, adjuster_email, email_jest, full_arguments):
    try:
        logger.debug("Starting email generation.")
        Full_Email_Argument = EmaiFromEmail()
        final_email = Full_Email_Argument.the_email_arguments(summary, adjuster_email, email_jest, full_arguments)
        logger.debug("Email generated successfully.")
        print("Email To Adjuster:")
        print(final_email)
    except Exception as e:
        logger.error(f"Error in email generation: {e}")
        raise e

def generate_email_summary_thread(differences, summary_text, full_arguments):
    email_summary = summarize_email(differences, summary_text, full_arguments)
    print("Email Summary:")
    print(email_summary)
    print()

# import uvicorn
# import asyncio

# nest_asyncio.apply()

# # Check if the event loop is already running
# if __name__ == "__main__":
#     if asyncio.get_event_loop().is_running():
#         # Use a new event loop
#         config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="debug")
#         server = uvicorn.Server(config)
#         asyncio.create_task(server.serve())
#     else:
#         # Use the default asyncio run method
#         uvicorn.run(app, host="0.0.0.0", port=8000)
