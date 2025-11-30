"""
LexRAG Benchmark Test Suite
Runs the AI Model against the Axis 1-7 questions defined in test-set.md.
"""

import requests
import json
import time
import re

GATEWAY_URL = "http://127.0.0.1:8009"
USER_ID = "benchmark_user_001"

# Benchmark Questions from test-set.md (Level 1 examples)
BENCHMARK_QUESTIONS = [
    {
        "axis": "Axis 1: Anatomy",
        "query": "What organs are affected when I have a mutation in the CFTR gene?",
        "level": 1
    },
    {
        "axis": "Axis 2: Genomics",
        "query": "I have the rs7412 variant in APOE. What does this mean for my health?",
        "level": 1
    },
    {
        "axis": "Axis 3: Transcriptomics",
        "query": "Why do some of my genes have different expression levels than normal?",
        "level": 1
    },
    {
        "axis": "Axis 4: Proteomics",
        "query": "What proteins are affected by my genetic variants and how might this impact my health?",
        "level": 1
    },
    {
        "axis": "Axis 5: Metabolomics",
        "query": "How do my genetic variants affect my metabolism and what dietary changes should I consider?",
        "level": 1
    },
    {
        "axis": "Axis 6: Epigenomics",
        "query": "How do environmental factors affect my gene expression through epigenetic changes?",
        "level": 1
    },
    {
        "axis": "Axis 7: Exposome",
        "query": "How do my lifestyle choices interact with my genetics to affect my health outcomes?",
        "level": 1
    }
]

def run_benchmark():
    print("==================================================")
    print(" STARTING LEXRAG BENCHMARK SUITE (7 AXES)")
    print("==================================================")
    
    results = []
    
    for i, item in enumerate(BENCHMARK_QUESTIONS, 1):
        print(f"\n[Test {i}/7] {item['axis']}")
        print(f"Query: {item['query']}")
        
        start_time = time.time()
        try:
            # Create new conversation for each test to ensure clean context
            # First, ensure user context exists (Digital Twin will auto-create default)
            requests.get(f"http://127.0.0.1:8008/twin/{USER_ID}/model")
            
            payload = {
                "message": item['query'],
                "conversation_id": f"bench_{i}_{int(time.time())}"
            }
            
            response = requests.post(
                f"{GATEWAY_URL}/chat/{USER_ID}", 
                json=payload, 
                timeout=120 # Give the agent time to think and use tools
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                ai_text = data.get("ai_response", {}).get("response", "")
                
                # Basic validation: Check if response is substantial
                status = "PASS" if len(ai_text) > 50 else "WARN (Short)"
                
                print(f"Status: {status} ({duration:.2f}s)")
                print("-" * 40)
                print(f"Response Snippet: {ai_text[:200]}...")
                print("-" * 40)
                
                # Check for evidence of tool use in the response or logs
                # In a real scenario, we'd parse the logs or metadata
                
                results.append({
                    "axis": item['axis'],
                    "status": status,
                    "duration": duration
                })
                
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(response.text)
                results.append({
                    "axis": item['axis'],
                    "status": "FAIL",
                    "duration": duration
                })
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "axis": item['axis'],
                "status": "ERROR",
                "duration": time.time() - start_time
            })
            
    print("\n==================================================")
    print(" BENCHMARK SUMMARY")
    print("==================================================")
    for res in results:
        print(f"{res['axis']:<25} | {res['status']:<10} | {res['duration']:.2f}s")

if __name__ == "__main__":
    run_benchmark()

