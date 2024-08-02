import config
from fastapi.middleware.cors import CORSMiddleware
import threading
import os
import logging
from fastapi import FastAPI, File, UploadFile, Form, HTTPException,BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import nest_asyncio
import json

from Xfile_upload import extract_text_from_pdf as extract_text_from_xfile
from Mfile_upload import extract_text_from_pdf as extract_text_from_mfile
from EASllm import EmailArgumentSelector
from EJllm import EmailJest
from ASEllm import ArgumentSummarizerEmail
from EFEllm import EmaiFromEmail
from voice import generate_audio
from openlink import open_links
from Xllm import XactimateExtractor
from Mllm import MeasurementExtractor
from Ellm import EstimateGenerator as ContractorEstimateGenerator
from Cllm import EstimateComparator
from Dllm import ArgumentSelector
from AOllm import ArgumentOrganizer
from ASllm import ArgumentSummarizer
from ESllm import summarize_email
import httpx
import re
import smtplib
from email.message import EmailMessage
import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from sor_llm import SorEvaluator
from RE import RetrievalEvidenceProcessor
from RA import RetrievalProcessor

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

# class EmailRequest(BaseModel):
#     summary: str
#     adjuster_email: str

class EmailRequest(BaseModel):
    summary: str
    email_arguments: str
    email_jest: str
    full_arguments: str
    adjuster_email: str

class MailerRequest(BaseModel):
    to_email: str
    subject: str
    message: str
    pdf_links: list[str]

async def download_pdf(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()  # Ensure we raise an exception for HTTP errors
        return response.content


def send_email_with_attachments(to_email: str, subject: str, message: str, pdf_contents: list[bytes], pdf_links: list[str]):
    # Create a multipart email message
    msg = MIMEMultipart()
    msg['From'] = 'no-reply@slephora.com'
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(message, 'html'))

    for i, pdf_content in enumerate(pdf_contents):
        filename = f'attachment_{i + 1}.pdf'
        part = MIMEApplication(pdf_content, _subtype='pdf')
        part.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(part)

    # Add PDF links in the email body as a separate MIMEText part
    # links_message = "\n\nSources:\n" + "\n".join(pdf_links)
    # msg.attach(MIMEText(links_message, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtpout.secureserver.net', 465) as server:
            server.login('no-reply@slephora.com', 'Boniface15')
            server.send_message(msg)
            logger.info("Email sent successfully!")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise
    


@app.post("/sendEmail")
async def handle_send_email_with_attachments(email_request: MailerRequest, background_tasks: BackgroundTasks):
    try:
        pdf_contents = await asyncio.gather(*(download_pdf(url) for url in email_request.pdf_links))
        background_tasks.add_task(send_email_with_attachments, email_request.to_email, email_request.subject, email_request.message, pdf_contents, email_request.pdf_links)
        return {"message": "Email sent successfully!"}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generateFromPDF/")
async def generateFromPDF(
    estimate_pdf: UploadFile = File(...), 
    property_pdf: UploadFile = File(...), 
):
    try:
        logger.debug("Received request to summarize.")
        logger.debug(f"Received request to summarize with files: estimate_pdf={estimate_pdf.filename}, property_pdf={property_pdf.filename}")
        
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
        
        
        sor_director = SorEvaluator()
        # returns IC type
        sor_director_repair_type = await sor_director.run_and_compare_ic_determiner(insurance_estimate)
        
        result = await sor_director.route_arguments_from_determiner(sor_director_repair_type,  insurance_estimate, property_pdf_path)
       # Access the return values
        logger.debug(result)

        summary_text, full_evidence , audio_url, full_arguments, differences, organized_arguments,extracted_text = result
    
    #     measurement_extractor = MeasurementExtractor()
    # 
        # Remove the temporary files
        os.remove(estimate_pdf_path)
        os.remove(property_pdf_path)
        
        # todo:
        audio_url = generate_audio(summary_text)
        
        logger.debug("Summary generated successfully.")
        
        # return {"summary": summary_text, "email":email_summary, "links":retrieval_evidence_processor.full_evidence , "audio_url": audio_url}
        return {"summary": summary_text, "organized_arguments": organized_arguments,"audio_url": audio_url, "full_arguments":full_arguments, "differences":differences, "repair_type":extracted_text }

    except Exception as e:
        logger.error(f"Error in summarizing: {e}")
        return {"error": str(e)}

@app.post("/emailPDF/")
async def summarize(
   summary: str = Form(...),
   organized_arguments: str = Form(...),
   full_arguments: str = Form(...),
   differences: str = Form(...), 
   repair_type: str =  Form(...)
):
    try:
        logger.debug("Received request to summarize the email.")
        repair_type = repair_type.lower()
        retrieval_evidence_processor = RetrievalEvidenceProcessor()
          # Process the organized arguments using RE.py
        retrieval_evidence_processor.process_components(organized_arguments)
        print(repair_type)

        # Print the full evidence
        # print("Full Evidence:")
        # print(retrieval_evidence_processor.full_evidence)
        pattern = r'\bshingle\b'
# Regular expression pattern
        pattern2 = r'\b(full roof|siding|roof)\b'

        # Finding matches
        if re.search(pattern, differences):
            isSiding = True
        else:
            isSiding = False
            
            
            # Finding matches
        if re.search(pattern2, repair_type):
            differences = differences
        else:
            differences = "None"
            
       
        email_summary = summarize_email(differences, summary, full_arguments,isSiding)
        print(organized_arguments)
        print("Email Summary:")
        print(differences)
        # print(email_summary)
        print()
        print(repair_type)
        # audio_url = generate_audio(email_summary)
        
        logger.debug("Summary generated successfully.")
        
        # return {"summary": summary_text, "email":email_summary, "links":retrieval_evidence_processor.full_evidence , "audio_url": audio_url}
        return {"email": email_summary, "links":retrieval_evidence_processor.full_evidence  }

    except Exception as e:
        logger.error(f"Error in summarizing: {e}")
        return {"error": str(e)}

@app.post("/generateFromEmail/")
async def generateFromEmail(adjuster_email: str = Form(...)):
    try:
        logger.debug("Received request to generate email.")
        
        email_argument_selector = EmailArgumentSelector()
        email_arguments = email_argument_selector.extract_arguments(adjuster_email)
        print("Arguments Extracted from Adjuster's Email:")

        email_jest = EmailJest()
        adjuster_jest = email_jest.extract_arguments(adjuster_email)
        print("email Jest")

        retrieval_processor = RetrievalProcessor()
        retrieval_processor.process_components(email_arguments)

        argument_summarizer_email = ArgumentSummarizerEmail()
        adjuster_email_arguments = argument_summarizer_email.extract_arguments(adjuster_email)
        summary = argument_summarizer_email.summarize_arguments(adjuster_email_arguments, email_jest, retrieval_processor.full_arguments)

        # retrieval_evidence_processor = RetrievalEvidenceProcessor()

        #  # Process the organized arguments using RE.py
        # retrieval_evidence_processor.process_components(email_arguments)
        # print()

        # # Print the full evidence
        # print("Full Evidence:")
        # print(retrieval_evidence_processor.full_evidence)
        
        # Full_Email_Argument = EmaiFromEmail()
        # final_email = Full_Email_Argument.the_email_arguments(summary, adjuster_email, email_jest, retrieval_processor.full_arguments)

        # logger.debug("Email generated successfully.")
        # print("Email To Adjuster:")
        # print(final_email)

        audio_url = generate_audio(summary)
        # return {"message": "Hello World"}
        # return {"message": "Email generated successfully", "summary": summary,"email":final_email,"links":retrieval_evidence_processor.full_evidence, "audio_url": audio_url}
        return {"message": "Email generated successfully","adjuster_email":adjuster_email,"audio_url": audio_url, "summary": summary,"email_arguments":email_arguments,"email_jest":adjuster_jest, "full_arguments": retrieval_processor.full_arguments}
        # return {"message": "Email generated successfully","adjuster_email":adjuster_email, "summary": summary,"email_arguments":email_arguments,"email_jest":email_jest, "full_arguments": retrieval_processor.full_arguments}


    
    except Exception as e:
        logger.error(f"Error in generating email: {e}")
        return {"error": str(e)}

@app.post("/emailText/")
async def generate_from_email(request: EmailRequest):
    try:
        logger.debug("Received request to generate email.")
        
        # Extract data from the request
        summary = request.summary
        email_arguments = request.email_arguments
        email_jest = request.email_jest
        full_arguments = request.full_arguments
        adjuster_email = request.adjuster_email
        

        # Process the organized arguments using RE.py (example)
        retrieval_evidence_processor = RetrievalEvidenceProcessor()
        retrieval_evidence_processor.process_components(email_arguments)
        
        logger.debug("Processed components for retrieval.")

        # Generate final email (example)
        Full_Email_Argument = EmaiFromEmail()
        final_email = Full_Email_Argument.the_email_arguments(
            summary, adjuster_email, email_jest, full_arguments
        )

        logger.debug("Email generated successfully.")
        
        return {
            "message": "Email generated successfully",
            "email": final_email,
            "links": retrieval_evidence_processor.full_evidence
        }

    except Exception as e:
        logger.error(f"Error in generating email: {e}")
        return {"error": str(e)}

