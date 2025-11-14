"""Comet ML logging wrapper."""
import os
from typing import List, Optional
from comet_ml import Experiment


_experiment: Optional[Experiment] = None


def _get_experiment() -> Optional[Experiment]:
    """Lazy initialization of Comet Experiment."""
    global _experiment
    
    if _experiment is not None:
        return _experiment
    
    comet_api_key = os.getenv("COMET_API_KEY")
    comet_project_name = os.getenv("COMET_PROJECT_NAME")
    comet_workspace = os.getenv("COMET_WORKSPACE")
    
    if not comet_api_key or not comet_project_name:
        # Comet logging is optional - return None if not configured
        return None
    
    try:
        kwargs = {
            "api_key": comet_api_key,
            "project_name": comet_project_name,
        }
        
        if comet_workspace:
            kwargs["workspace"] = comet_workspace
        
        _experiment = Experiment(**kwargs)
        return _experiment
    except Exception as e:
        print(f"Warning: Failed to initialize Comet Experiment: {e}")
        return None


def log_benchmark_run(prompt: str, results: List[dict], winner: Optional[str]) -> None:
    """
    Log a benchmark run to Comet ML.
    
    Args:
        prompt: The prompt that was used
        results: List of result dictionaries with model_id, latency_ms, estimated_cost_usd, tokens_estimate, error
        winner: The winning model_id (or None)
    """
    experiment = _get_experiment()
    if experiment is None:
        return
    
    try:
        # Log metrics per model
        for result in results:
            model_id = result.get("model_id", "unknown")
            # Sanitize model_id for metric names (replace special chars)
            safe_model_id = model_id.replace("/", "_").replace("-", "_")
            
            if result.get("error") is None:
                experiment.log_metric(f"latency_ms_{safe_model_id}", float(result.get("latency_ms", 0.0)))
                experiment.log_metric(f"cost_usd_{safe_model_id}", float(result.get("estimated_cost_usd", 0.0)))
                experiment.log_metric(f"tokens_{safe_model_id}", int(result.get("tokens_estimate", 0)))
            else:
                # Log error as a metric (0 indicates failure)
                experiment.log_metric(f"latency_ms_{safe_model_id}", 0.0)
                experiment.log_metric(f"error_{safe_model_id}", 1)
        
        # Log winner
        if winner:
            experiment.log_parameter("winner", str(winner))
        
        # Log prompt and summary (ensure strings, not iterables)
        experiment.log_text(f"Prompt: {str(prompt)}")
        
        successful_count = sum(1 for r in results if r.get("error") is None)
        experiment.log_text(f"Summary: {successful_count}/{len(results)} models succeeded")
        
    except Exception as e:
        print(f"Warning: Failed to log to Comet: {e}")

