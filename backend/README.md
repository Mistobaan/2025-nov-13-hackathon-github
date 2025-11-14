# LLM Benchmark Backend

FastAPI backend for benchmarking LLM providers (FriendliAI + OpenAI) on latency, token count, and cost.

## Setup

1. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the `backend/` directory with the following variables:
```env
FRIENDLI_API_KEY=your_friendli_api_key
# OR use FRIENDLI_TOKEN (both are supported)
FRIENDLI_BASE_URL=https://api.friendli.ai/serverless/v1
OPENAI_API_KEY=your_openai_api_key
COMET_API_KEY=your_comet_api_key
COMET_PROJECT_NAME=latency-benchmark
COMET_WORKSPACE=your_workspace  # Optional
FRIENDLI_PRICE_PER_1K_TOKENS=0.0006  # Optional, defaults to 0.0006
OPENAI_PRICE_PER_1K_TOKENS=0.0008  # Optional, defaults to 0.0008
```

4. Run the server (make sure your virtual environment is activated):
```bash
cd backend
source venv/bin/activate  # If not already activated
uvicorn main:app --reload --port 8000
```

Or:
```bash
python main.py
```

The app will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Serves the frontend HTML page
- `GET /api/models` - Returns list of available models
- `POST /api/benchmark` - Runs benchmark on selected models

## Notes

- FriendliAI is configured to use GLM-4.6 model with the serverless API endpoint.
- The API uses OpenAI-compatible format, so it should work with standard chat completions.
- Comet logging is optional - the app will work without it if `COMET_API_KEY` is not set.
- Token estimation uses a simple approximation: `ceil((prompt_length + output_length) / 4.0)`
- You can use either `FRIENDLI_API_KEY` or `FRIENDLI_TOKEN` in your `.env` file (both are supported).

