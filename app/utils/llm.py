import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(
    base_url="https://agentrouter.org",
    auth_token=os.getenv("AGENT_ROUTER_API_KEY"),
    max_retries=0,
)