"""
LLM configuration and initialization for the Professional Fingerprint application.
Supports both Google Gemini and local LLM via LM Studio.
"""
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


# LLM configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
LOCAL_LLM_BASE_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:1234/v1")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "local-model")


def get_llm_with_temp(temp: float):
    """Return a chat model with the requested temperature."""
    if LLM_PROVIDER == "local":
        return ChatOpenAI(
            base_url=LOCAL_LLM_BASE_URL,
            api_key="lm-studio",
            model=LOCAL_LLM_MODEL,
            temperature=temp,
            max_tokens=4096,
        )
    else:
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            temperature=temp,
            max_output_tokens=4096,
            max_retries=3,
            google_api_key=GOOGLE_API_KEY,
        )


def get_llm_for_code_generation(temperature: float = 0.2):
    """Code generation model with longer timeout."""
    if LLM_PROVIDER == "local":
        return ChatOpenAI(
            base_url=LOCAL_LLM_BASE_URL,
            api_key="lm-studio",
            model=LOCAL_LLM_MODEL,
            temperature=temperature,
            max_tokens=8192,
        )
    else:
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            temperature=temperature,
            max_output_tokens=8192,
            max_retries=3,
            google_api_key=GOOGLE_API_KEY,
        )


# Default general-purpose LLM
# Only initialize if API key is present to avoid import errors
try:
    llm = get_llm_with_temp(0.3)
except Exception as e:
    print(f"[WARNING] Could not initialize default LLM: {e}")
    llm = None
