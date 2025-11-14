"""Model configuration for LLM benchmark."""
import os
from typing import Dict, List, Optional

# Load environment variables with fallbacks
FRIENDLI_PRICE = float(os.getenv("FRIENDLI_PRICE_PER_1K_TOKENS", "0.0006"))
OPENAI_PRICE = float(os.getenv("OPENAI_PRICE_PER_1K_TOKENS", "0.0008"))

MODELS: List[Dict[str, any]] = [
    # FriendliAI Models
    {
        "id": "glm-4.6",
        "label": "FriendliAI – GLM-4.6",
        "provider": "friendli",
        "price_per_1k_tokens_usd": FRIENDLI_PRICE,
    },
    {
        "id": "llama-3.1-8b-instruct",
        "label": "FriendliAI – Llama-3.1-8B-Instruct",
        "provider": "friendli",
        "price_per_1k_tokens_usd": FRIENDLI_PRICE,
    },
    {
        "id": "magistral-small-2506",
        "label": "FriendliAI – Magistral-Small-2506",
        "provider": "friendli",
        "price_per_1k_tokens_usd": FRIENDLI_PRICE,
    },
    {
        "id": "a.x-3.1",
        "label": "FriendliAI – A.X-3.1",
        "provider": "friendli",
        "price_per_1k_tokens_usd": FRIENDLI_PRICE,
    },
    {
        "id": "qwen3-235b-thinking-2507",
        "label": "FriendliAI – Qwen3-235B-Thinking-2507",
        "provider": "friendli",
        "price_per_1k_tokens_usd": FRIENDLI_PRICE,
    },
    {
        "id": "qwen3-235b-instruct-2507",
        "label": "FriendliAI – Qwen3-235B-Instruct-2507",
        "provider": "friendli",
        "price_per_1k_tokens_usd": FRIENDLI_PRICE,
    },
    {
        "id": "llama-3.3-70b-instruct",
        "label": "FriendliAI – Llama-3.3-70B-Instruct",
        "provider": "friendli",
        "price_per_1k_tokens_usd": FRIENDLI_PRICE,
    },
    {
        "id": "devstral-small-2505",
        "label": "FriendliAI – Devstral-Small-2505",
        "provider": "friendli",
        "price_per_1k_tokens_usd": FRIENDLI_PRICE,
    },
    {
        "id": "gemma-3-27b-it",
        "label": "FriendliAI – Gemma-3-27B-IT",
        "provider": "friendli",
        "price_per_1k_tokens_usd": FRIENDLI_PRICE,
    },
    {
        "id": "qwen3-32b",
        "label": "FriendliAI – Qwen3-32B",
        "provider": "friendli",
        "price_per_1k_tokens_usd": FRIENDLI_PRICE,
    },
    # OpenAI Models
    {
        "id": "gpt-4o-mini",
        "label": "OpenAI – gpt-4o-mini",
        "provider": "openai",
        "price_per_1k_tokens_usd": OPENAI_PRICE,
    },
]


def get_all_models() -> List[Dict[str, any]]:
    """Return all available models."""
    return [
        {
            "id": model["id"],
            "label": model["label"],
            "provider": model["provider"],
        }
        for model in MODELS
    ]


def get_model_by_id(model_id: str) -> Optional[Dict[str, any]]:
    """Get a model by its ID, or None if not found."""
    for model in MODELS:
        if model["id"] == model_id:
            return model
    return None

