from typing import Dict, List, Optional

import logging
import os

import openai
import tiktoken
from backoff import expo, on_exception
from openai import APIError
from ratelimit import RateLimitException, limits
from reretry import retry

CODER_ROLE = {
    "role": "system",
    "content": "You are a helpful and efficient developer.",
}
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


def generate_code(
    prompt: str,
) -> str:
    """Sends request to Chat function and returns response."""
    openai.api_key = get_api_key_from_env()
    messages = [
        CODER_ROLE,
        {
            "role": "user",
            "content": prompt,
        },
    ]
    return chat(messages)


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


def num_tokens_from_messages(messages, model=CHAT_MODEL) -> int:
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == CHAT_MODEL:  # note: future models may deviate from this
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{
            # role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1
                    # token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not presently implemented for
            model {model}.
  See https://github.com/openai/openai-python/blob/main/chatml.md for
  information on how messages are converted to tokens."""
        )
