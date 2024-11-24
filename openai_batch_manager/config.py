# openai_batch_manager/config.py

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
COMPLETION_WINDOW = os.getenv("COMPLETION_WINDOW", "24h")
ENDPOINT = os.getenv("ENDPOINT", "/v1/completions")

# Validate essential configurations
if not API_KEY:
    raise ValueError("API_KEY is not set in the environment variables.")
