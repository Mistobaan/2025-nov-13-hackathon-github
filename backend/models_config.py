"""Model configuration for LLM benchmark."""
import os
from typing import Dict, List, Optional

# Load environment variables with fallbacks
OPENAI_PRICE = float(os.getenv("OPENAI_PRICE_PER_1K_TOKENS", "0.0008"))

MODELS: List[Dict[str, any]] = [
    # FriendliAI Models - Per Second Pricing
    {
        "id": "glm-4.6",
        "label": "FriendliAI – GLM-4.6",
        "provider": "friendli",
        "pricing_type": "per_second",
        "price_per_second_usd": 0.004,
    },
    {
        "id": "magistral-small-2506",
        "label": "FriendliAI – Magistral-Small-2506",
        "provider": "friendli",
        "pricing_type": "per_second",
        "price_per_second_usd": 0.002,
    },
    {
        "id": "a.x-3.1",
        "label": "FriendliAI – A.X-3.1",
        "provider": "friendli",
        "pricing_type": "per_second",
        "price_per_second_usd": 0.002,
    },
    {
        "id": "qwen3-235b-thinking-2507",
        "label": "FriendliAI – Qwen3-235B-Thinking-2507",
        "provider": "friendli",
        "pricing_type": "per_second",
        "price_per_second_usd": 0.004,
    },
    {
        "id": "devstral-small-2505",
        "label": "FriendliAI – Devstral-Small-2505",
        "provider": "friendli",
        "pricing_type": "per_second",
        "price_per_second_usd": 0.002,
    },
    {
        "id": "gemma-3-27b-it",
        "label": "FriendliAI – Gemma-3-27B-IT",
        "provider": "friendli",
        "pricing_type": "per_second",
        "price_per_second_usd": 0.002,
    },
    {
        "id": "qwen3-32b",
        "label": "FriendliAI – Qwen3-32B",
        "provider": "friendli",
        "pricing_type": "per_second",
        "price_per_second_usd": 0.002,
    },
    # FriendliAI Models - Per Token Pricing
    {
        "id": "llama-3.1-8b-instruct",
        "label": "FriendliAI – Llama-3.1-8B-Instruct",
        "provider": "friendli",
        "pricing_type": "per_token",
        "price_per_1M_tokens_usd": 0.1,
    },
    {
        "id": "llama-3.3-70b-instruct",
        "label": "FriendliAI – Llama-3.3-70B-Instruct",
        "provider": "friendli",
        "pricing_type": "per_token",
        "price_per_1M_tokens_usd": 0.6,
    },
    # FriendliAI Models - Per Token Split Pricing (Input/Output)
    {
        "id": "qwen3-235b-instruct-2507",
        "label": "FriendliAI – Qwen3-235B-Instruct-2507",
        "provider": "friendli",
        "pricing_type": "per_token_split",
        "price_per_1M_input_tokens_usd": 0.2,
        "price_per_1M_output_tokens_usd": 0.8,
    },
    # OpenAI Models
    {
        "id": "gpt-4o-mini",
        "label": "OpenAI – gpt-4o-mini",
        "provider": "openai",
        "pricing_type": "per_token",
        "price_per_1M_tokens_usd": 0.8,  # $0.0008 per 1k tokens = $0.8 per 1M tokens
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


