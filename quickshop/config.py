import os

from dotenv import load_dotenv

load_dotenv()

ASU_BASE_URL = "https://openai.rc.asu.edu/v1"
MODEL_ID = "gpt-oss-120b"
GEMINI_MODEL_ID = "models/gemini-3.5-flash"


def active_model_id() -> str:
    """The model build_model() will use right now, so the API can report it truthfully."""
    return GEMINI_MODEL_ID if os.getenv("GEMINI_API_KEY") else MODEL_ID


def model_configured() -> bool:
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY"))


def build_model():
    gemini_key = os.getenv("GEMINI_API_KEY")
    asu_key = os.getenv("API_KEY")

    if gemini_key:
        from strands.models.gemini import GeminiModel

        return GeminiModel(
            model_id=GEMINI_MODEL_ID,
            api_key=gemini_key,
        )
    elif asu_key:
        from strands.models.openai import OpenAIModel

        return OpenAIModel(
            client_args={"base_url": ASU_BASE_URL, "api_key": asu_key},
            model_id=MODEL_ID,
            params={"temperature": 0},
        )
    else:
        raise RuntimeError("No API key found. Set GEMINI_API_KEY or API_KEY in .env")
