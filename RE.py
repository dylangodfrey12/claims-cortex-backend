import os
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings

# Set API keys
os.environ["OPENAI_API_KEY"] = "sk-proj-Rqy3FSVajisBJM2F3ZumT3BlbkFJTn6IhtAIHSzzvwpSrUke"
os.environ["PINECONE_API_KEY"] = "def37dc3-c862-48be-abb6-dcc6c6a6cac0"

# Initialize embeddings
embeddings = OpenAIEmbeddings()

# Load vector store and retriever
index_name = "testroof"
namespace = "roofing"
try:
    vectorstore = Pinecone.from_existing_index(index_name, embeddings, namespace=namespace)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

    # Print troubleshooting information
    print(f"Number of items in vectorstore: {len(vectorstore.similarity_search('', k=1))}")
    print(f"Retriever index: {retriever.vectorstore._index}")

    if len(vectorstore.similarity_search('', k=1)) == 0:
        print("The vectorstore appears to be empty. Please check if data has been added to the index.")
except Exception as e:
    print(f"An error occurred while loading the vectorstore: {str(e)}")
    print("Please check your Pinecone index name, namespace, and API key.")
    exit(1)

class RetrievalEvidenceProcessor:
    def __init__(self):
        self.full_evidence = ""

    def process_components(self, organized_components):
        # Split the organized components into a list
        components = [component.strip() for component in organized_components.split('\n') if component.strip()]

        # Process each component
        for component in components:
            print(f"Processing component: {component}")

            try:
                # Retrieve relevant documents for the component
                docs = retriever.get_relevant_documents(component)

                # Append the retrieved documents to full_evidence
                self.full_evidence += f"Component: {component}\n"
                self.full_evidence += "Documents:\n"
                for doc in docs:
                    self.full_evidence += f"Metadata: {doc.metadata}\n"
                    self.full_evidence += "---\n"
                self.full_evidence += "\n"
            except Exception as e:
                print(f"An error occurred while processing component '{component}': {str(e)}")
                print("Continuing to the next component.")
                print("---")

        print("All components processed.")