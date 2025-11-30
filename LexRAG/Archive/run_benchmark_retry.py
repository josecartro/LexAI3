"""
LexRAG Benchmark Runner - Retry Logic
Executes the questions from test-set.md against the AI Gateway with connection retry logic.
"""

import requests
import json
import time
import sys

GATEWAY_URL = "http://127.0.0.1:8009"
USER_ID = "benchmark_user"

BENCHMARK_QUESTIONS = [
    {"id": "axis1_l1", "axis": "Anatomy", "level": 1, "query": "What organs are affected when I have a mutation in the CFTR gene?"},
    # ... (Add back other questions)
]

def wait_for_gateway():
    print("Waiting for Gateway to be ready...")
    for i in range(10):
        try:
            requests.get(f"{GATEWAY_URL}/health", timeout=2)
            print("Gateway is UP!")
            return True
        except:
            time.sleep(2)
            print(".", end="", flush=True)
    print("\nGateway failed to start.")
    return False

def run_benchmark():
    if not wait_for_gateway():
        return

    print(f"\nStarting LexRAG Benchmark...")
    
    # Test just one question to verify connectivity first
    q = BENCHMARK_QUESTIONS[0]
    print(f"\n[TEST] {q['axis']} Level {q['level']}: {q['id']}")
    
    try:
        payload = {
            "message": q['query'],
            "conversation_id": f"bench_{q['id']}_{int(time.time())}"
        }
        
        response = requests.post(
            f"{GATEWAY_URL}/chat/{USER_ID}", 
            json=payload, 
            timeout=120
        )
        
        print(f"Status: {response.status_code}")
        print(response.text[:200])
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    run_benchmark()

