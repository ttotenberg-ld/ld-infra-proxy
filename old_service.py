#!/usr/bin/env python3
"""
Old service example - responds with 25-50ms latency.
"""

import time
import random
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Old Service", description="Legacy service with 25-50ms latency")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def process_request(request: Request, path: str = ""):
    """Process any request with artificial latency."""
    
    # Simulate old service latency: 25-50ms
    latency = random.uniform(0.025, 0.050)
    await asyncio.sleep(latency)
    
    # Simulate 1% chance of failure
    if random.random() < 0.01:
        return JSONResponse(
            content={
                "service": "old-service",
                "version": "1.0.0",
                "error": "Simulated service failure",
                "timestamp": time.time()
            },
            status_code=500
        )
    
    # Get request details
    method = request.method
    headers = dict(request.headers)
    body = await request.body()
    
    # Return response
    return JSONResponse(
        content={
            "service": "old-service",
            "version": "1.0.0",
            "method": method,
            "path": path,
            "simulated_latency_ms": round(latency * 1000, 2),
            "message": "Response from old service",
            "timestamp": time.time()
        },
        status_code=200
    )

if __name__ == "__main__":
    import uvicorn
    print("Starting Old Service on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001) 