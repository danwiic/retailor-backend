import os

from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def _router_base_url() -> str:
    url = os.getenv("AGENT_ROUTER_URL", "https://agentrouter.org").rstrip("/")
    if url.endswith("/v1"):
        url = url[:-3]
    return url


def _openai_base_url() -> str:
    url = os.getenv("AGENT_ROUTER_URL", "https://agentrouter.org").rstrip("/")
    if not url.endswith("/v1"):
        url = url + "/v1"
    return url


client = Anthropic(
    base_url=_router_base_url(),
    auth_token=os.getenv("AGENT_ROUTER_API_KEY"),
    max_retries=0,
    timeout=60.0,
)

# DeepSeek is an OpenAI-compatible model, so parse calls go through this client.
openai_client = OpenAI(
    base_url=_openai_base_url(),
    api_key=os.getenv("AGENT_ROUTER_API_KEY"),
    max_retries=0,
    timeout=60.0,
)
