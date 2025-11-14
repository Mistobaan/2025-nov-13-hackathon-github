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
from comet_logger import log_benchmark_run

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
        
        # Estimate tokens: approximate as ceil((prompt_length + output_length) / 4.0)
        if error is None:
            total_chars = len(request.prompt) + len(text)
            tokens_estimate = math.ceil(total_chars / 4.0)
            estimated_cost_usd = (tokens_estimate / 1000.0) * model["price_per_1k_tokens_usd"]
        else:
            tokens_estimate = 0
            estimated_cost_usd = 0.0
        
        results.append(
            BenchmarkResult(
                model_id=model_id,
                label=model["label"],
                provider=model["provider"],
                latency_ms=latency_ms,
                tokens_estimate=tokens_estimate,
                estimated_cost_usd=estimated_cost_usd,
                text=text,
                error=error,
            )
        )
    
    # Determine winner (lowest cost, tie-break by latency)
    successful_results = [r for r in results if r.error is None]
    winner = None
    winner_reason = None
    
    if successful_results:
        # Sort by cost (ascending), then latency (ascending)
        sorted_results = sorted(
            successful_results,
            key=lambda x: (x.estimated_cost_usd, x.latency_ms)
        )
        winner = sorted_results[0].model_id
        winner_reason = "lowest estimated cost, tie-broken by latency"
    
    # Log to Comet ML (fire-and-forget)
    try:
        results_dict = [
            {
                "model_id": r.model_id,
                "latency_ms": r.latency_ms,
                "estimated_cost_usd": r.estimated_cost_usd,
                "tokens_estimate": r.tokens_estimate,
                "error": r.error,
            }
            for r in results
        ]
        log_benchmark_run(request.prompt, results_dict, winner)
    except Exception as e:
        # Don't fail the request if logging fails
        print(f"Warning: Failed to log to Comet: {e}")
    
    return BenchmarkResponse(
        prompt=request.prompt,
        results=results,
        winner=winner,
        winner_reason=winner_reason,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

