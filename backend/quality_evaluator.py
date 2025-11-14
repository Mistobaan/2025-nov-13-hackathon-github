"""Response quality evaluator using LLM."""
import os
import httpx
from typing import Optional


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class QualityEvaluationError(Exception):
    """Custom exception for quality evaluation errors."""
    pass


async def evaluate_response_quality(prompt: str, response: str) -> float:
    """
    Evaluate the quality of a response using gpt-4o-mini.
    Returns a score from 1.0 to 10.0.
    
    Args:
        prompt: The original prompt
        response: The response to evaluate
        
    Returns:
        Quality score (1.0 to 10.0)
    """
    if not OPENAI_API_KEY:
        # If no OpenAI key, return a default score based on length and basic heuristics
        return _fallback_quality_score(prompt, response)
    
    evaluation_prompt = f"""You are an expert evaluator of LLM responses. Evaluate the following response for quality.

Original Prompt:
{prompt}

Response to Evaluate:
{response}

Please evaluate this response on a scale of 1.0 to 10.0 based on:
1. Relevance: Does it directly address the prompt?
2. Completeness: Does it provide a thorough answer?
3. Accuracy: Is the information correct?
4. Clarity: Is it well-written and easy to understand?

Respond with ONLY a single number between 1.0 and 10.0 (e.g., "7.5"). Do not include any explanation or other text."""

    endpoint = "https://api.openai.com/v1/chat/completions"
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": evaluation_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 10,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response_obj = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response_obj.raise_for_status()
            
            data = response_obj.json()
            score_text = data["choices"][0]["message"]["content"].strip()
            
            # Extract numeric score
            try:
                score = float(score_text)
                # Clamp to 1.0-10.0 range
                score = max(1.0, min(10.0, score))
                return score
            except ValueError:
                # If parsing fails, use fallback
                return _fallback_quality_score(prompt, response)
            
        except Exception as e:
            # If evaluation fails, use fallback
            print(f"Warning: Quality evaluation failed: {e}")
            return _fallback_quality_score(prompt, response)


def _fallback_quality_score(prompt: str, response: str) -> float:
    """
    Fallback quality scoring when LLM evaluation is not available.
    Uses simple heuristics based on response length and basic metrics.
    """
    if not response or len(response.strip()) == 0:
        return 1.0
    
    # Base score on response length relative to prompt
    response_length = len(response)
    prompt_length = len(prompt)
    
    # Normalize: responses should be at least as long as prompt for good quality
    length_ratio = response_length / max(prompt_length, 10)
    
    # Base score from 3.0 to 7.0 based on length
    base_score = min(7.0, max(3.0, 3.0 + (length_ratio * 2.0)))
    
    # Bonus for longer, more detailed responses
    if response_length > 200:
        base_score += 1.0
    if response_length > 500:
        base_score += 1.0
    
    # Clamp to 1.0-10.0
    return max(1.0, min(10.0, base_score))

