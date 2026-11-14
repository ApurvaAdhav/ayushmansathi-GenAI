import os
from pathlib import Path
from google import genai
from dotenv import load_dotenv

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env", override=True)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

client = None


def get_client():
    global client

    if not API_KEY:
        raise ValueError("GEMINI_API_KEY is missing in .env")

    if client is None:
        client = genai.Client(api_key=API_KEY)

    return client


def load_prompt(filename: str) -> str:
    """Load a prompt from the prompts folder."""
    prompt_path = BASE_DIR / "prompts" / filename

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {filename}")

    return prompt_path.read_text(encoding="utf-8")


def generate_response(prompt: str) -> str:
    """Generate a response using the Gemini API."""
    try:
        gemini_client = get_client()

        response = gemini_client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response")

        return response.text.strip()

    except Exception as e:
        raise RuntimeError(f"Failed to generate response: {e}") from e


def generate_answer(question: str, context: str, task_prompt: str = "task1.txt") -> str:
    """Generate an answer using the system and task prompts."""

    system_prompt = load_prompt("system.txt")
    task_template = load_prompt(task_prompt)

    formatted_prompt = task_template.format(
        question=question,
        context=context
    )

    complete_prompt = f"""
{system_prompt}

{formatted_prompt}
"""

    return generate_response(complete_prompt)
