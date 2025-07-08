# ld-infra-proxy

A LaunchDarkly-powered middleware that routes requests to different service endpoints based on feature flags and measures performance.

## What it does

- **Routes requests** to different service endpoints based on LaunchDarkly feature flags
- **Measures latency** for all requests (successful and failed)
- **Tracks errors** in LaunchDarkly for monitoring and analysis
- **Demonstrates A/B testing** between service versions with different performance characteristics

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your LaunchDarkly SDK key:
   ```bash
   cp .env.example .env
   # Edit .env and add your LaunchDarkly SDK key
   ```

3. Create a string feature flag in LaunchDarkly named `service-endpoint`

## Running

Start all services in separate terminals:

```bash
# Terminal 1: Old service (25-50ms latency, 1% errors)
python old_service.py

# Terminal 2: New service (30-60ms latency, 2% errors)  
python new_service.py

# Terminal 3: Middleware
python middleware.py

# Terminal 4: Test traffic
python test_middleware.py
```

## Endpoints

- **Middleware**: `http://localhost:8000`
- **Old Service**: `http://localhost:8001`
- **New Service**: `http://localhost:8002`

## Feature Flag Configuration

Set your `service-endpoint` flag in LaunchDarkly to:
- **Default**: `http://localhost:8001/api/process` (routes to old service)
- **Variation**: `http://localhost:8002/api/process` (routes to new service)

## Metrics

The middleware tracks these events in LaunchDarkly:
- `latency` - Response time for all requests
- `500-error` - Service failures
- `400-error` - Request format errors 