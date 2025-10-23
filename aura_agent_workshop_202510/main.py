"""
"""
import asyncio
import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()
NEO4J_CREDENTIALS_FILE = os.environ.get("NEO4J_CREDENTIALS_FILE")
AURA_AGENT_API_URL = os.environ.get("AURA_AGENT_API_URL")

load_dotenv(NEO4J_CREDENTIALS_FILE)
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

AURA_AUTH_URL = "https://api.neo4j.io/oauth/token"


async def get_bearer_token() -> None:
    """Get OAuth bearer token"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                AURA_AUTH_URL,
                auth=(CLIENT_ID, CLIENT_SECRET),
                # headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={"grant_type": "client_credentials"},
            )
            response.raise_for_status()

            response_data = response.json()
            bearer_token = response_data.get("access_token")

            if not bearer_token:
                raise ValueError("No access token in response")
        except httpx.HTTPError as e:
            raise Exception(f"Failed to get bearer token: {e}")
        return bearer_token


async def call_aura_agent_api(question: str) -> dict[str, Any]:
    """Call the Aura Agent API endpoint"""
    token = await get_bearer_token()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                AURA_AGENT_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {token}"
                },
                json={"input": question},
                timeout=60.0
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            raise Exception(f"API call failed: {e}")


async def main() -> None:
    question = input("> ")
    full_answer = await call_aura_agent_api(
        question,
    )
    for a in full_answer["content"]:
        if a["type"] == "text":
            print(a["text"])
    print()


if __name__ == "__main__":
    asyncio.run(main())
