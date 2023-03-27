from typing import Dict, List, Optional

import logging
import os

import openai
from backoff import expo, on_exception
from openai import APIError
from ratelimit import RateLimitException, limits
from reretry import retry

CODE_MODEL = "code-davinci-002"
CM_MAX_TOKENS = 8001
MINUTE = 60
CHAT_MODEL = "gpt-3.5-turbo"
CH_MAX_TOKENS = 4096

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


def get_api_key_from_env() -> Optional[str]:
    """Returns API Key if available as environment variable."""
    if "OPENAI_API_KEY" not in os.environ:
        logger.critical(
            "OPENAI_API_KEY does not exist as environment variable.",
        )
        logger.debug(os.environ)
    return os.getenv("OPENAI_API_KEY")


@retry(APIError, tries=8, delay=1, backoff=2)
@on_exception(expo, RateLimitException, max_tries=8)
@limits(calls=20, period=MINUTE)
def generate_code(
    prompt: str,
    temp: Optional[float] = 0.1,
    max_tokens: Optional[int] = int(CM_MAX_TOKENS / 2),
    stop: Optional[List[str]] = None,
) -> str:
    """Sends request to Codex Completion service and returns response."""
    openai.api_key = get_api_key_from_env()
    try:
        response = openai.Completion.create(
            engine=CODE_MODEL,
            prompt=prompt,
            temperature=temp,
            max_tokens=max_tokens,
            stop=stop,
        )
        return str(response["choices"][0]["text"])
    except Exception as e:
        logger.error(e)
        logger.debug(
            f" from: {prompt} with temp: {temp}, " f" max_tokens: {max_tokens}"
        )
        return ""


@retry(APIError, tries=8, delay=1, backoff=2)
@on_exception(expo, RateLimitException, max_tries=8)
@limits(calls=20, period=MINUTE)
def chat(
    messages: List[Dict[str, str]],
) -> str:
    """Sends request to ChatGPT service and returns response."""
    openai.api_key = get_api_key_from_env()
    try:
        response = openai.ChatCompletion.create(
            model=CHAT_MODEL,
            messages=messages,
        )
        return str(response["choices"][0]["message"]["content"])
    except Exception as e:
        logger.error(e)
        logger.debug(f" from: {messages}")
        return ""
