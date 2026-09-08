import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import AzureOpenAI, RateLimitError

load_dotenv()


class LLMRateLimitError(RuntimeError):
    """The upstream model provider rejected the request due to quota/rate limits."""


@lru_cache(maxsize=1)
def _client() -> AzureOpenAI:
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("FOUNDRY_API_KEY")
    if not endpoint or not api_key:
        raise RuntimeError(
            "Azure Foundry is not configured; set AZURE_OPENAI_ENDPOINT and "
            "AZURE_OPENAI_API_KEY"
        )
    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        max_retries=0,
        timeout=120.0,
    )


def complete_chat(
    system: str,
    messages: list[dict],
    model: str,
    max_tokens: int = 4096,
) -> str:
    """Run an Azure OpenAI deployment and return its text response."""
    try:
        response = _client().chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, *messages],
            max_completion_tokens=max_tokens,
        )
    except RateLimitError as e:
        raise LLMRateLimitError("Azure Foundry rate limit or quota exceeded") from e
    try:
        text = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as e:
        raise RuntimeError("model returned no content") from e
    if not text:
        raise RuntimeError("model returned no text")
    return text
