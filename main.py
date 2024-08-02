from fastapi.middleware.cors import CORSMiddleware
import threading
import os
import logging
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import nest_asyncio

# Your existing imports
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

# New imports for chatbot functionality
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.documents.base import Document

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

class ChatRequest(BaseModel):
    query: str
    chat_history: List[Dict[str, str]]

class ChatResponse(BaseModel):
    response: Dict[str, Any]


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

# Initialize OpenAI language model (ChatOpenAI) and embeddings (OpenAIEmbeddings)
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)
embeddings = OpenAIEmbeddings()

index_name = "testroof"
namespace = "roofing"
vectorstore = Pinecone.from_existing_index(index_name, embeddings, namespace=namespace)
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

# Load system prompt from file
def load_system_prompt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"System prompt file not found: {file_path}")
        return ""

system_prompt_file = "system_prompt.txt"
system_prompt = load_system_prompt(system_prompt_file)

# Create a prompt template using the system prompt and user input
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{context}\n\nConversation History:\n{chat_history}\n\nQuestion: {input}"),
    ]
)

# Create a question-answering chain using the language model and prompt template
question_answer_chain = create_stuff_documents_chain(llm, prompt)
chain = create_retrieval_chain(retriever, question_answer_chain)

def document_to_dict(doc):
    return {
        "page_content": doc.page_content,
        "metadata": doc.metadata
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.debug("Received chat request.")
        
        # Extract query and chat history from the request
        query = request.query
        chat_history = request.chat_history

        # Retrieve relevant documents based on the query
        docs = await retriever.aget_relevant_documents(query)
        if not docs:
            raise HTTPException(status_code=404, detail="No relevant documents found")

        # Combine the chat history into a single string
        chat_history_str = "\n".join([f"User: {user_input}\nAssistant: {ai_response}" for user_input, ai_response in chat_history[-5:]])

        # Generate a response using the retrieval chain
        response = await chain.ainvoke({"input": query, "context": docs[0].page_content, "chat_history": chat_history_str})

        # Convert the response to a serializable format
        def serialize(obj):
            if isinstance(obj, Document):
                return document_to_dict(obj)
            if isinstance(obj, list):
                return [serialize(item) for item in obj]
            if isinstance(obj, dict):
                return {key: serialize(value) for key, value in obj.items()}
            return obj

        serialized_response = serialize(response)
        chat_history.append((query, response))
        logger.debug(f"Content of response: {chat_history}")

        # Return the serialized response
        return ChatResponse(response=serialized_response)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
