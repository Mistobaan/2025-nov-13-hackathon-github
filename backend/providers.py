"""Provider functions for calling different LLM APIs."""
import os
import httpx
from typing import Optional


FRIENDLI_API_KEY = os.getenv("FRIENDLI_API_KEY") or os.getenv("FRIENDLI_TOKEN")
FRIENDLI_BASE_URL = os.getenv("FRIENDLI_BASE_URL", "https://api.friendli.ai/serverless/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class ProviderError(Exception):
    """Custom exception for provider errors."""
    pass


async def call_friendli(model_id: str, prompt: str) -> str:
    """
    Call FriendliAI API to get completion.
    Uses OpenAI-compatible API format.
    """
    if not FRIENDLI_API_KEY:
        raise ProviderError("FRIENDLI_API_KEY or FRIENDLI_TOKEN not set")
    
    # Map model_id to actual FriendliAI model name
    model_mapping = {
        "glm-4.6": "zai-org/GLM-4.6",
        "llama-3.1-8b-instruct": "meta-llama/Llama-3.1-8B-Instruct",
        "magistral-small-2506": "mistralai/Magistral-Small-2506",
        "a.x-3.1": "skt/A.X-3.1",
        "qwen3-235b-thinking-2507": "Qwen/Qwen3-235B-A22B-Thinking-2507",
        "qwen3-235b-instruct-2507": "Qwen/Qwen3-235B-A22B-Instruct-2507",
        "llama-3.3-70b-instruct": "meta-llama/Llama-3.3-70B-Instruct",
        "devstral-small-2505": "mistralai/Devstral-Small-2505",
        "gemma-3-27b-it": "google/gemma-3-27b-it",
        "qwen3-32b": "Qwen/Qwen3-32B",
        # Fallback
        "friendli-mistral": "mistralai/Mistral-7B-Instruct-v0.2",
    }
    actual_model = model_mapping.get(model_id, model_id)
    
    # FriendliAI uses OpenAI-compatible endpoint
    base_url = FRIENDLI_BASE_URL.rstrip('/')
    endpoint = f"{base_url}/chat/completions"
    
    # OpenAI-compatible payload format
    payload = {
        "model": actual_model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }
    
    # Note: extra_body for reasoning features is only supported via OpenAI client SDK,
    # not in direct HTTP API calls. Removing it for now.
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {FRIENDLI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            
            data = response.json()
            # OpenAI-compatible response structure
            if "choices" in data and len(data["choices"]) > 0:
                message = data["choices"][0].get("message", {})
                # Get main content
                content = message.get("content", "")
                # If there's reasoning content, append it (optional)
                if "reasoning_content" in message:
                    reasoning = message.get("reasoning_content", "")
                    if reasoning:
                        content = f"{content}\n\n[Reasoning: {reasoning}]"
                return content if content else message.get("text", "")
            else:
                raise ProviderError(f"FriendliAI response parsing error: no choices in response: {data}")
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            if e.response.status_code == 404:
                raise ProviderError(
                    f"FriendliAI API endpoint not found (404). "
                    f"Tried: {endpoint}. "
                    f"Please verify FRIENDLI_BASE_URL in your .env file. "
                    f"Response: {error_detail}"
                )
            raise ProviderError(f"FriendliAI API error: {e.response.status_code} - {error_detail}")
        except httpx.RequestError as e:
            raise ProviderError(f"FriendliAI request error: {str(e)}")
        except (KeyError, IndexError) as e:
            raise ProviderError(f"FriendliAI response parsing error: {str(e)}")


async def call_openai(model_id: str, prompt: str) -> str:
    """
    Call OpenAI API to get completion.
    """
    if not OPENAI_API_KEY:
        raise ProviderError("OPENAI_API_KEY not set")
    
    endpoint = "https://api.openai.com/v1/chat/completions"
    
    payload = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except httpx.HTTPStatusError as e:
            raise ProviderError(f"OpenAI API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise ProviderError(f"OpenAI request error: {str(e)}")
        except (KeyError, IndexError) as e:
            raise ProviderError(f"OpenAI response parsing error: {str(e)}")

