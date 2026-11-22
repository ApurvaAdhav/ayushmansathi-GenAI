
import logging
import os
import time
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env", override=True)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


@lru_cache(maxsize=100)
def cached_gemini_response(prompt: str):
    """Generate and cache Gemini responses."""
    gemini_client = get_client()

    response = gemini_client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")

    usage = response.usage_metadata

    input_tokens = usage.prompt_token_count if usage else 0
    output_tokens = usage.candidates_token_count if usage else 0
    total_tokens = usage.total_token_count if usage else 0

    return (
        response.text.strip(),
        input_tokens,
        output_tokens,
        total_tokens
    )


def generate_response(prompt: str) -> str:
    """Generate a response with caching and request logging."""
    start_time = time.perf_counter()

    try:
        previous_hits = cached_gemini_response.cache_info().hits

        result = cached_gemini_response(prompt)

        cache_hit = cached_gemini_response.cache_info().hits > previous_hits

        latency = time.perf_counter() - start_time

        response_text, input_tokens, output_tokens, total_tokens = result

        if cache_hit:
            input_tokens = 0
            output_tokens = 0
            total_tokens = 0

        logger.info(
            "Gemini request | Latency: %.2f seconds | "
            "Input tokens: %s | Output tokens: %s | "
            "Total tokens: %s | Cache hit: %s",
            latency,
            input_tokens,
            output_tokens,
            total_tokens,
            cache_hit
        )

        return response_text

    except Exception as e:
        latency = time.perf_counter() - start_time

        logger.exception(
            "Gemini request failed | Latency: %.2f seconds",
            latency
        )

        raise RuntimeError(f"Failed to generate response: {e}") from e


def generate_answer(
    question: str,
    context: str,
    task_prompt: str = "task1.txt"
) -> str:
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
