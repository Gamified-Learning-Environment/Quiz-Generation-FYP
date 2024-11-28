import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.environ.get('MONGODB_URI')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not MONGODB_URI or not OPENAI_API_KEY:
    raise ValueError("Missing required environment variables. Please check your .env file")