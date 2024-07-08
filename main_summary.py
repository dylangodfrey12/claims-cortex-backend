from fastapi.middleware.cors import CORSMiddleware
import threading
import os
import logging
from fastapi import FastAPI, File, UploadFile, Form, HTTPException,BackgroundTasks,WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import nest_asyncio
import json

from Xfile_upload import extract_text_from_pdf as extract_text_from_xfile
from Mfile_upload import extract_text_from_pdf as extract_text_from_mfile
from EASllm import EmailArgumentSelector
from EJllm import EmailJest
from RA import RetrievalProcessor
from ASEllm import ArgumentSummarizerEmail
from EFEllm import EmaiFromEmail
from voice import generate_audio
import redis
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
import httpx
import smtplib
from email.message import EmailMessage
import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from celery_app import celery

app = FastAPI()

clients = {}

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

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = redis.StrictRedis.from_url(redis_url, decode_responses=True)

# Initialize the clients dictionary to store WebSocket connections in memory
clients = {}

async def save_client_to_redis(client_id: str):
    redis_client.set(client_id, "1")  # Store client ID as string

async def remove_client_from_redis(client_id: str):
    redis_client.delete(client_id)

async def load_clients_from_redis():
    keys = redis_client.keys('*')
    return {key: True for key in keys}


# Define models for requests
class VoiceRequest(BaseModel):
    summary: str

# class EmailRequest(BaseModel):
#     summary: str
#     adjuster_email: str

class EmailRequest(BaseModel):
    summary: str
    email_arguments: str
    full_arguments: str
    adjuster_email: str
    client_id: str

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



@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    clients[client_id] = websocket
    await save_client_to_redis(client_id)
    logger.info(f"Client connected: {client_id}")

    try:
        while True:
            # Check for messages in Redis
            message = redis_client.lpop(f"messages:{client_id}")
            if message:
                await websocket.send_text(message)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {client_id}")
        del clients[client_id]
        await remove_client_from_redis(client_id)

async def notify_client(client_id: str, message: str):
    redis_client.rpush(f"messages:{client_id}", message)
    logger.info(f"Message pushed to Redis for client {client_id}")


@celery.task(name="process_pdf_files")
def process_pdf_files(estimate_pdf_content, property_pdf_content, client_id):
    logger.info("Started processing PDF files")
    try:
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)

        estimate_pdf_path = os.path.join(temp_dir, "estimate.pdf")
        property_pdf_path = os.path.join(temp_dir, "property.pdf")

        with open(estimate_pdf_path, "wb") as buffer:
            buffer.write(estimate_pdf_content)

        with open(property_pdf_path, "wb") as buffer:
            buffer.write(property_pdf_content)

       # Your existing logic
        xactimate_extractor = XactimateExtractor()
        insurance_estimate = xactimate_extractor.extract_estimate(estimate_pdf_path)
        logger.info("Insurance Company's Estimate extracted")

        measurement_extractor = MeasurementExtractor()
        contractor_measurements = measurement_extractor.extract_measurements(property_pdf_path)
        logger.info("Extracted contractor measurements")

        contractor_estimate_generator = ContractorEstimateGenerator()
        contractor_estimate = contractor_estimate_generator.generate_estimate(contractor_measurements)
        logger.info("Generated contractor estimate")

        comparator = EstimateComparator()
        differences = comparator.compare_estimates(contractor_estimate, insurance_estimate)
        logger.info("Compared estimates")

        argument_generator = ArgumentSelector()
        arguments = argument_generator.generate_arguments(differences)
        logger.info("Generated arguments")

        argument_organizer = ArgumentOrganizer()
        organized_arguments = argument_organizer.organize_arguments(arguments)
        logger.info("Organized arguments")

        retrieval_processor = RetrievalProcessor()
        retrieval_processor.process_components(organized_arguments)
        logger.info("Processed retrieval components")

        argument_summarizer = ArgumentSummarizer()
        summary_text = argument_summarizer.summarize_arguments(organized_arguments)
        logger.info("Summarized arguments")

        # audio_url = generate_audio(summary_text)
        logger.info("Generated audio URL")

        os.remove(estimate_pdf_path)
        os.remove(property_pdf_path)
        logger.info("Removed temporary files")

        result = {
            "summary": summary_text,
            "organized_arguments": organized_arguments,
            # "audio_url": audio_url,
            "full_arguments": retrieval_processor.full_arguments,
            "differences": differences
        }

        asyncio.run(notify_client(client_id, json.dumps(result)))
        return result

    except Exception as e:
        logger.error(f"Error in summarizing: {e}")
        notify_client(client_id, json.dumps({"error": str(e)}))
        return {"error": str(e)}
    


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
async def generate_from_pdf(
    estimate_pdf: UploadFile = File(...), 
    property_pdf: UploadFile = File(...),
    client_id: str = Form(...)
):
    try:
        estimate_pdf_content = await estimate_pdf.read()
        property_pdf_content = await property_pdf.read()
        
        task = process_pdf_files.delay(estimate_pdf_content, property_pdf_content, client_id)
        return {"task_id": task.id, "message": "PDF processing started. You will be notified once it's done."}
    
    except Exception as e:
        logging.error(f"Error in processing PDFs: {e}")
        return {"error": str(e)}

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    task = celery.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'status': str(task.info),
        }
    return response

@celery.task(name="summarize_email_task")
def summarize_email_task(summary, organized_arguments, full_arguments, differences, client_id):
    logger.info("Started summarizing email task")
    try:
        retrieval_evidence_processor = RetrievalEvidenceProcessor()
        retrieval_evidence_processor.process_components(organized_arguments)

        email_summary = summarize_email(differences, summary, full_arguments)

        result = {
            "email": email_summary,
            "links": retrieval_evidence_processor.full_evidence
        }

        asyncio.run(notify_client(client_id, json.dumps(result)))
        return result

    except Exception as e:
        logger.error(f"Error in summarizing email: {e}")
        asyncio.run(notify_client(client_id, json.dumps({"error": str(e)})))
        return {"error": str(e)}

@app.post("/emailPDF/")
async def summarize(
    summary: str = Form(...),
    organized_arguments: str = Form(...),
    full_arguments: str = Form(...),
    differences: str = Form(...),
    client_id: str = Form(...)
):
    try:
        logger.debug("Received request to summarize the email.")

        task = summarize_email_task.delay(summary, organized_arguments, full_arguments, differences, client_id)
        return {"task_id": task.id, "message": "Email summarization started. You will be notified once it's done."}

    except Exception as e:
        logger.error(f"Error in summarizing: {e}")
        return {"error": str(e)}



@celery.task(name="generate_from_email_task")
def generate_from_email_task(adjuster_email, client_id):
    logger.info("Started generating email task")
    try:
        email_argument_selector = EmailArgumentSelector()
        email_arguments = email_argument_selector.extract_arguments(adjuster_email)
        logger.info("Arguments Extracted from Adjuster's Email")

        email_jest = EmailJest()
        adjuster_jest = email_jest.extract_arguments(adjuster_email)
        logger.info("Email Jest Extracted")

        retrieval_processor = RetrievalProcessor()
        retrieval_processor.process_components(email_arguments)
        logger.info("Processed components for retrieval")

        argument_summarizer_email = ArgumentSummarizerEmail()
        adjuster_email_arguments = argument_summarizer_email.extract_arguments(adjuster_email)
        summary = argument_summarizer_email.summarize_arguments(adjuster_email_arguments, email_jest, retrieval_processor.full_arguments)
        logger.info("Summarized arguments")

        # audio_url = generate_audio(summary_text)


        result = {
            "message": "Email generated successfully",
            "adjuster_email": adjuster_email,
            "summary": summary,
            "email_arguments": email_arguments,
            "full_arguments": retrieval_processor.full_arguments,
             # "audio_url": audio_url,
        }
        print("results:")

        print(result)

        asyncio.run(notify_client(client_id, json.dumps(result)))
        return result

    except Exception as e:
        logger.error(f"Error in generating email: {e}")
        asyncio.run(notify_client(client_id, json.dumps({"error": str(e)})))
        return {"error": str(e)}

# Update the endpoint to use the Celery task
@app.post("/generateFromEmail/")
async def generateFromEmail(adjuster_email: str = Form(...), client_id: str = Form(...)):
    try:
        logger.debug("Received request to generate email.")
        
        task = generate_from_email_task.delay(adjuster_email, client_id)
        return {"task_id": task.id, "message": "Email generation started. You will be notified once it's done."}

    except Exception as e:
        logger.error(f"Error in generating email: {e}")
        return {"error": str(e)}

# Create the Celery task
@celery.task(name="generate_email_text_task")
def generate_email_text_task(summary, email_arguments, full_arguments, adjuster_email, client_id):
    logger.info("Started generating email text task")
    try:
        # Process the organized arguments using RE.py (example)
        retrieval_evidence_processor = RetrievalEvidenceProcessor()
        email_jest = EmailJest()
        adjuster_jest = email_jest.extract_arguments(adjuster_email)
        retrieval_evidence_processor.process_components(email_arguments)
        logger.info("Processed components for retrieval.")

        # Generate final email (example)
        Full_Email_Argument = EmaiFromEmail()
        final_email = Full_Email_Argument.the_email_arguments(
            summary, adjuster_email, email_jest, full_arguments
        )

        result = {
            "message": "Email generated successfully",
            "email": final_email,
            "links": retrieval_evidence_processor.full_evidence
        }

        asyncio.run(notify_client(client_id, json.dumps(result)))
        return result

    except Exception as e:
        logger.error(f"Error in generating email: {e}")
        asyncio.run(notify_client(client_id, json.dumps({"error": str(e)})))
        return {"error": str(e)}

# Update the endpoint to use the Celery task
@app.post("/emailText/")
async def generate_from_email(request: EmailRequest):
    try:
        logger.debug("Received request to generate email.")
        
        # Extract data from the request
        summary = request.summary
        email_arguments = request.email_arguments # Assuming this is already JSON-serializable
        full_arguments = request.full_arguments
        adjuster_email = request.adjuster_email
        client_id = request.client_id

        task = generate_email_text_task.delay(summary, email_arguments, full_arguments, adjuster_email, client_id)
        return {"task_id": task.id, "message": "Email generation started. You will be notified once it's done."}

    except Exception as e:
        logger.error(f"Error in generating email: {e}")
        return {"error": str(e)}


