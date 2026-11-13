
import os
from pathlib import Path
from google import genai
from dotenv import load_dotenv

# Load .env from the main project directory
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

# Read environment variables
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

# Initialize client only when needed
client = None


def get_client():
    global client

    if not API_KEY:
        raise ValueError("GEMINI_API_KEY is missing in .env")

    if client is None:
        client = genai.Client(api_key=API_KEY)

    return client


def generate_response(prompt: str) -> str:
    """
    Generate a response using the Gemini API.
    """
    try:
        gemini_client = get_client()

        response = gemini_client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response")

        return response.text

    except Exception as e:
        raise RuntimeError(f"Failed to generate response: {e}") from e
