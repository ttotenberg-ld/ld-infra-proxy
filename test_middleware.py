#!/usr/bin/env python3
"""
Test script for the LD Infra Proxy middleware.
"""

import requests
import json
import time

# Middleware endpoint
MIDDLEWARE_URL = "http://localhost:8000"

def test_middleware():
    """Test the middleware with sample requests."""
    
    # Test payload
    payload = {
        "feature_flag_key": "service-endpoint",
        "default_endpoint": "http://localhost:8001/api/process"
    }
    
    print("Testing LD Infra Proxy Middleware")
    print(f"Middleware URL: {MIDDLEWARE_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    # Make multiple test requests
    while True:
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{MIDDLEWARE_URL}/test",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"  Status: {response.status_code}")
            print(f"  Total time: {total_time:.3f}s")
            print(f"  Response: {response.text}")
            print()
            
        except Exception as e:
            print(f"Request {i+1} failed: {e}")
            print()
        
        # Small delay between requests
        time.sleep(0.2)

if __name__ == "__main__":
    test_middleware() 