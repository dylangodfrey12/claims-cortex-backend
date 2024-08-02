import os
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings

# Load the .env file
load_dotenv()


# Initialize embeddings
embeddings = OpenAIEmbeddings()

# Load vector store and retriever
index_name = "testroof"
namespace = "roofing"

def print_to_text_file(text_to_print):
        with open('output.txt', 'a') as f:
            print(text_to_print, file=f)
            
try:
    vectorstore = Pinecone.from_existing_index(index_name, embeddings, namespace=namespace)
    print_to_text_file(vectorstore)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
    print_to_text_file(vectorstore)
    # Print troubleshooting information
    print(f"Number of items in vectorstore: {len(vectorstore.similarity_search('', k=1))}")
    print(f"Retriever index: {retriever.vectorstore._index}")

    if len(vectorstore.similarity_search('', k=1)) == 0:
        print("The vectorstore appears to be empty. Please check if data has been added to the index.")
except Exception as e:
    print(f"An error occurred while loading the vectorstore: {str(e)}")
    print("Please check your Pinecone index name, namespace, and API key.")
    exit(1)

class RetrievalProcessor:
    def __init__(self):
        self.full_arguments = ""

    def process_components(self, organized_components):
        # Split the organized components into a list
        components = [component.strip() for component in organized_components.split('\n') if component.strip()]
        print_to_text_file(f"All RA.py components: {components}")
        # Process each component
        for component in components:
            print(f"Processing component: {component}")
            print_to_text_file(f"Processing component: {component}")
            try:
                # Retrieve relevant documents for the component
                docs = retriever.get_relevant_documents(component)

                # Append the retrieved documents to full_arguments
                self.full_arguments += f"Component: {component}\n"
                self.full_arguments += "Documents:\n"
                for doc in docs:
                    self.full_arguments += f"Content: {doc.page_content}\n"
                    self.full_arguments += f"Metadata: {doc.metadata}\n"
                    self.full_arguments += "---\n"
                self.full_arguments += "\n"
            except Exception as e:
                print(f"An error occurred while processing component '{component}': {str(e)}")
                print("Continuing to the next component.")
                print("---")

        print("All components processed.")