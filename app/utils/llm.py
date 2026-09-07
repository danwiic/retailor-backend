import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(
    base_url=os.getenv("AGENT_ROUTER_URL", "https://agentrouter.org"),
    auth_token=os.getenv("AGENT_ROUTER_API_KEY"),
    max_retries=0,
    timeout=60.0,
)
