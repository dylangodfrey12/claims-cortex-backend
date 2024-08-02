import os
import asyncio
import config
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import BaseMessage


# Initialize OpenAI language model (ChatOpenAI) and embeddings (OpenAIEmbeddings)
llm = ChatOpenAI(
    model="gpt-4o",  # Use the GPT-4 model
    temperature=0,  # Set temperature to 0 for deterministic output
    streaming=True,  # Enable streaming output
    callbacks=[StreamingStdOutCallbackHandler()]  # Use streaming callback to print output in real-time
)
embeddings = OpenAIEmbeddings()  # Initialize OpenAI embeddings

# Load Pinecone vector store and retriever
index_name = "testroof"  # Name of the Pinecone index
namespace = "roofing"  # Namespace within the Pinecone index

# Load the vector store from an existing Pinecone index
vectorstore = Pinecone.from_existing_index(index_name, embeddings, namespace=namespace)
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})  # Create a retriever to fetch the top 1 relevant document

# Load system prompt from file
def load_system_prompt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()  # Read the system prompt from the file
    except FileNotFoundError:
        print(f"System prompt file not found: {file_path}")
        return ""  # Return an empty string if the file is not found

system_prompt_file = "system_prompt.txt"  # Path to the system prompt file
system_prompt = load_system_prompt(system_prompt_file)  # Load the system prompt

# Create a prompt template using the system prompt and user input
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),  # Set the system prompt
        ("human", "{context}\n\nConversation History:\n{chat_history}\n\nQuestion: {input}"),  # Set the user prompt with context, chat history, and input
    ]
)

# Create a question-answering chain using the language model and prompt template
question_answer_chain = create_stuff_documents_chain(llm, prompt)
chain = create_retrieval_chain(retriever, question_answer_chain)  # Combine the retriever and question-answering chain

async def main():
    conversation_history = []  # Initialize an empty list to store the conversation history

    while True:
        query = input("\n\nUser: ")  # Prompt the user for input
        if query.lower() in ["quit", "exit", "bye"]:
            print("Assistant: Goodbye!")
            break  # Exit the loop if the user enters "quit", "exit", or "bye"
        
        docs = await retriever.aget_relevant_documents(query)  # Retrieve relevant documents based on the user's query
        
        print("\nRetrieved Document Metadata:")
        for doc in docs:
            doc_id = doc.metadata.get('id', 'N/A')
            doc_source = doc.metadata.get('source', 'N/A')
            print(f"Document ID: {doc_id}")
            print(f"Source: {doc_source}")
            print(f"Metadata: {doc.metadata}")
            print("---")  # Print the metadata of the retrieved documents
        
        # Generate conversation history string by joining the last 5 user inputs and assistant responses
        chat_history = "\n".join([f"User: {user_input}\nAssistant: {ai_response}" for user_input, ai_response in conversation_history[-5:]])
        
        print("\nAssistant: ", end="", flush=True)  # Print "Assistant: " to indicate the start of the assistant's response
        response = await chain.ainvoke({"input": query, "context": docs[0].page_content, "chat_history": chat_history})  # Generate a response using the retrieval chain
        
        conversation_history.append((query, response))  # Append the current user input and assistant response to the conversation history

if __name__ == "__main__":
    asyncio.run(main())  # Run the main function asynchronously












