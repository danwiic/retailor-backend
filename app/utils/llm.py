import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


def _router_base_url() -> str:
    url = os.getenv("AGENT_ROUTER_URL", "https://agentrouter.org").rstrip("/")
    if url.endswith("/v1"):
        url = url[:-3]
    return url


client = Anthropic(
    base_url=_router_base_url(),
    auth_token=os.getenv("AGENT_ROUTER_API_KEY"),
    max_retries=0,
    timeout=60.0,
)
