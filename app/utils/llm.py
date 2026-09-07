import os

import boto3
from dotenv import load_dotenv

load_dotenv()

# Credentials come from AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY; region from
# AWS_REGION. Same AWS config already used for S3 exports.
bedrock = boto3.client(
    "bedrock-runtime",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
)


def extract_text(response: dict) -> str:
    """Pull the first text block out of a Bedrock converse response."""
    try:
        blocks = response["output"]["message"]["content"]
    except (KeyError, TypeError) as e:
        raise RuntimeError("model returned no content") from e
    for block in blocks:
        if isinstance(block, dict) and block.get("text"):
            return block["text"]
    raise RuntimeError("model returned no text block")
