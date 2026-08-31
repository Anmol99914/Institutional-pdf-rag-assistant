import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client():
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Check your .env file."
            )

        _client = genai.Client(api_key=api_key)

    return _client


def generate_answer(prompt, model_name="gemini-3.6-flash"):
    """Sends a prompt to Gemini and retries temporary server errors."""

    client = _get_client()

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            return response.text

        except Exception as e:

            # Retry temporary Gemini server errors
            if "503" in str(e) or "UNAVAILABLE" in str(e):

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt

                    print(
                        f"[LLM] Gemini temporarily unavailable. "
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)
                    continue

            # For other errors, or if all retries fail
            return f"[LLM ERROR] Could not generate answer: {e}"

    return "[LLM ERROR] Could not generate answer after retries."
