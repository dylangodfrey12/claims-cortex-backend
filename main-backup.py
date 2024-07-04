from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import nest_asyncio

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

class ChatRequest(BaseModel):
    query: str
    chat_history: list

class ChatResponse(BaseModel):
    response: Dict[str, Any]

os.environ["OPENAI_API_KEY"] = "sk-proj-Rqy3FSVajisBJM2F3ZumT3BlbkFJTn6IhtAIHSzzvwpSrUke"
os.environ["PINECONE_API_KEY"] = "def37dc3-c862-48be-abb6-dcc6c6a6cac0"

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
        chat_history_str = "\n".join([f"User: {msg['user']}\nAssistant: {msg['assistant']}" for msg in chat_history[-5:]])

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
        logger.debug(f"Content of response: {chat_history_str}")
        logger.debug(f"Type of chat_history: {type(chat_history)}")

        # Return the serialized response
        return ChatResponse(response=serialized_response)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
