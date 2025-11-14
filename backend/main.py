"""FastAPI app for LLM benchmark."""
import os
import time
import math
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

from models_config import get_all_models, get_model_by_id
from providers import call_friendli, call_openai, ProviderError
from quality_evaluator import evaluate_response_quality

app = FastAPI(title="LLM Benchmark API")

# Get the directory where this file is located
BACKEND_DIR = Path(__file__).parent
STATIC_DIR = BACKEND_DIR / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class BenchmarkRequest(BaseModel):
    """Request model for benchmark endpoint."""
    prompt: str
    model_ids: List[str]


class BenchmarkResult(BaseModel):
    """Result for a single model benchmark."""
    model_id: str
    label: str
    provider: str
    latency_ms: float
    tokens_estimate: int
    estimated_cost_usd: float
    text: str
    quality_score: Optional[float] = None
    error: Optional[str] = None


class BenchmarkResponse(BaseModel):
    """Response model for benchmark endpoint."""
    prompt: str
    results: List[BenchmarkResult]
    winner: Optional[str] = None
    winner_reason: Optional[str] = None


@app.get("/")
async def root():
    """Serve the main HTML page."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/models")
async def get_models():
    """Return list of available models."""
    return {"models": get_all_models()}


@app.post("/api/benchmark", response_model=BenchmarkResponse)
async def benchmark(request: BenchmarkRequest):
    """Run benchmark on selected models."""
    # Validate input
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    if not request.model_ids:
        raise HTTPException(status_code=400, detail="At least one model must be selected")
    
    results = []
    
    # Run benchmark for each model
    for model_id in request.model_ids:
        model = get_model_by_id(model_id)
        if not model:
            results.append(
                BenchmarkResult(
                    model_id=model_id,
                    label="Unknown",
                    provider="unknown",
                    latency_ms=0.0,
                    tokens_estimate=0,
                    estimated_cost_usd=0.0,
                    text="",
                    error=f"Model {model_id} not found",
                )
            )
            continue
        
        # Measure latency and call provider
        start_time = time.time()
        error = None
        text = ""
        
        try:
            if model["provider"] == "friendli":
                text = await call_friendli(model_id, request.prompt)
            elif model["provider"] == "openai":
                text = await call_openai(model_id, request.prompt)
            else:
                error = f"Unknown provider: {model['provider']}"
        except ProviderError as e:
            error = str(e)
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000.0
        latency_seconds = (end_time - start_time)
        
        # Estimate tokens: approximate as ceil((prompt_length + output_length) / 4.0)
        if error is None:
            input_chars = len(request.prompt)
            output_chars = len(text)
            input_tokens_estimate = math.ceil(input_chars / 4.0)
            output_tokens_estimate = math.ceil(output_chars / 4.0)
            total_tokens_estimate = input_tokens_estimate + output_tokens_estimate
            
            # Calculate cost based on pricing type
            pricing_type = model.get("pricing_type", "per_token")
            
            if pricing_type == "per_second":
                # Per-second pricing: cost = latency_seconds * price_per_second
                estimated_cost_usd = latency_seconds * model.get("price_per_second_usd", 0.0)
            elif pricing_type == "per_token_split":
                # Split pricing: separate input and output rates
                input_cost = (input_tokens_estimate / 1_000_000.0) * model.get("price_per_1M_input_tokens_usd", 0.0)
                output_cost = (output_tokens_estimate / 1_000_000.0) * model.get("price_per_1M_output_tokens_usd", 0.0)
                estimated_cost_usd = input_cost + output_cost
            else:
                # Default: per_token pricing
                estimated_cost_usd = (total_tokens_estimate / 1_000_000.0) * model.get("price_per_1M_tokens_usd", 0.0)
            
            tokens_estimate = total_tokens_estimate
        else:
            tokens_estimate = 0
            estimated_cost_usd = 0.0
            input_tokens_estimate = 0
            output_tokens_estimate = 0
        
        results.append(
            BenchmarkResult(
                model_id=model_id,
                label=model["label"],
                provider=model["provider"],
                latency_ms=latency_ms,
                tokens_estimate=tokens_estimate,
                estimated_cost_usd=estimated_cost_usd,
                text=text,
                quality_score=None,  # Will be evaluated after all responses are collected
                error=error,
            )
        )
    
    # Evaluate quality for all successful responses
    for result in results:
        if result.error is None and result.text:
            try:
                result.quality_score = await evaluate_response_quality(request.prompt, result.text)
            except Exception as e:
                print(f"Warning: Failed to evaluate quality for {result.model_id}: {e}")
                result.quality_score = None
    
    # Determine winner (lowest cost, tie-break by latency, then quality)
    successful_results = [r for r in results if r.error is None]
    winner = None
    winner_reason = None
    
    if successful_results:
        # Sort by cost (ascending), then latency (ascending), then quality (descending)
        sorted_results = sorted(
            successful_results,
            key=lambda x: (
                x.estimated_cost_usd,
                x.latency_ms,
                -(x.quality_score or 0)  # Negative for descending quality
            )
        )
        winner = sorted_results[0].model_id
        winner_reason = "lowest estimated cost, tie-broken by latency, then quality"
    
    return BenchmarkResponse(
        prompt=request.prompt,
        results=results,
        winner=winner,
        winner_reason=winner_reason,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

