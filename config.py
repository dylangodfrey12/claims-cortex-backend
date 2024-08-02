import os
from dotenv import load_dotenv

def load_environment_variables():
    load_dotenv()


# Load environment variables immediately when the script runs
load_environment_variables()
# Load the .env file
load_dotenv()

# Access environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_KEY_SECRET = os.getenv('CLOUDINARY_API_KEY_SECRET')