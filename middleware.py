import ldclient
from ldclient.config import Config
from ldclient import Context
from dotenv import load_dotenv
import os
import time
import uuid
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

load_dotenv()

# Set sdk_key to your LaunchDarkly key
sdk_key = os.getenv("LAUNCHDARKLY_SDK_KEY")

'''
Config Notes:
Relevant configuration options for request-based events are included below. 
If you see the logged warning "Exceeded event queue capacity. Increase capacity to avoid dropping events.", you should adjust the events_max_pending and flush_interval.
Full Python configuration documentation: https://launchdarkly-python-sdk.readthedocs.io/en/latest/api-main.html#module-ldclient.config
'''

config = Config(
    sdk_key=sdk_key, 
    omit_anonymous_contexts=True, # prevents index and identify events from being sent. Defaults to False. Keeps traffic lean while still sending variation() and track() events.
    events_max_pending=10000, # limits the number of events that can be buffered in memory. Defaults to 10000.
    flush_interval=5, # sets the interval at which events are flushed to LaunchDarkly. Defaults to 5 seconds.
    enable_event_compression=True # compresses events before sending them to LaunchDarkly. Defaults to False. Setting to True will slightly increase CPU usage, but likely will significantly reduce bandwidth.
    ) 


ldclient.set_config(config)

app = FastAPI(title="LD Infra Proxy", description="LaunchDarkly-powered service routing middleware")

class ProxyRequest(BaseModel):
    feature_flag_key: str
    default_endpoint: str

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy_request(request: Request, path: str = ""):
    # Create LaunchDarkly context for this request
    # set anonymous to True to prevent request contexts from cluttering the Contexts List
    context = Context.builder(str(uuid.uuid4())) \
        .set("kind", "request") \
        .set("timestamp", time.time()) \
        .set("anonymous", True) \
        .build()
    
    try:
        # Parse the request body to get routing configuration
        body = await request.body()
        if not body:
            ldclient.get().track("400-error", context, data={"error": "Request body required"})
            raise HTTPException(status_code=400, detail="Request body required")
        
        # Parse JSON body
        import json
        try:
            proxy_config = json.loads(body)
            feature_flag_key = proxy_config["feature_flag_key"]
            default_endpoint = proxy_config["default_endpoint"]
        except (json.JSONDecodeError, KeyError) as e:
            ldclient.get().track("400-error", context, data={"error": "Invalid request format"})
            raise HTTPException(status_code=400, detail=f"Invalid request format: {e}")

        # Evaluate feature flag to get service endpoint
        target_endpoint = ldclient.get().variation(feature_flag_key, context, default_endpoint)
        
        # Make HTTP request to chosen service
        async with httpx.AsyncClient() as client:
            start_time = time.time()
            try:
                response = await client.request(
                    method=request.method,
                    url=target_endpoint,
                    headers=dict(request.headers),
                    content=body
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                ldclient.get().track("latency", context, metric_value=response_time)
                
                # Return response as-is
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                ldclient.get().track("latency", context, metric_value=response_time)
                ldclient.get().track("500-error", context, data={"error": "Service call failed"})
                raise HTTPException(status_code=500, detail=f"Service call failed: {e}")
                
    except HTTPException:
        raise
    except Exception as e:
        ldclient.get().track("500-error", context, data={"error": "Proxy error"})
        raise HTTPException(status_code=500, detail=f"Proxy error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    ldclient.get().close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

