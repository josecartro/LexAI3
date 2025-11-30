"""
LexRAG Benchmark Runner
Executes the questions from test-set.md against the AI Gateway and logs results.
"""

import requests
import json
import time
import sys

GATEWAY_URL = "http://127.0.0.1:8009"
USER_ID = "benchmark_user"

# Benchmark questions from test-set.md
BENCHMARK_QUESTIONS = [
    # AXIS 1: ANATOMY
    {"id": "axis1_l1", "axis": "Anatomy", "level": 1, "query": "What organs are affected when I have a mutation in the CFTR gene?"},
    {"id": "axis1_l2", "axis": "Anatomy", "level": 2, "query": "Map all anatomical structures where PKD1 protein is expressed and predict which tissues would be affected by loss-of-function mutations at different developmental stages."},
    
    # AXIS 2: GENOMICS
    {"id": "axis2_l1", "axis": "Genomics", "level": 1, "query": "I have the rs7412 variant in APOE. What does this mean for my health?"},
    {"id": "axis2_l2", "axis": "Genomics", "level": 2, "query": "Given my complete genetic profile, what medications should I avoid and what dosage adjustments are needed for common drugs based on my CYP450 variants and other pharmacogenomic markers?"},
    
    # AXIS 3: TRANSCRIPTOMICS
    {"id": "axis3_l1", "axis": "Transcriptomics", "level": 1, "query": "Why do some of my genes have different expression levels than normal?"},
    
    # AXIS 4: PROTEOMICS
    {"id": "axis4_l1", "axis": "Proteomics", "level": 1, "query": "What proteins are affected by my genetic variants and how might this impact my health?"},
    
    # AXIS 5: METABOLOMICS
    {"id": "axis5_l1", "axis": "Metabolomics", "level": 1, "query": "How do my genetic variants affect my metabolism and what dietary changes should I consider?"},
    
    # AXIS 6: EPIGENOMICS
    {"id": "axis6_l1", "axis": "Epigenomics", "level": 1, "query": "How do environmental factors affect my gene expression through epigenetic changes?"},
    
    # AXIS 7: EXPOSOME
    {"id": "axis7_l1", "axis": "Exposome", "level": 1, "query": "How do my lifestyle choices interact with my genetics to affect my health outcomes?"}
]

def run_benchmark():
    print(f"Starting LexRAG Benchmark ({len(BENCHMARK_QUESTIONS)} questions)...")
    print("-" * 60)
    
    results = []
    
    # Ensure user context exists (Digital Twin will create default)
    try:
        requests.get(f"http://127.0.0.1:8008/twin/{USER_ID}/model")
    except:
        pass

    for q in BENCHMARK_QUESTIONS:
        print(f"\n[TEST] {q['axis']} Level {q['level']}: {q['id']}")
        print(f"Query: {q['query']}")
        
        start_time = time.time()
        try:
            payload = {
                "message": q['query'],
                "conversation_id": f"bench_{q['id']}_{int(time.time())}"
            }
            
            # Call Gateway
            response = requests.post(
                f"{GATEWAY_URL}/chat/{USER_ID}", 
                json=payload, 
                timeout=120
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("ai_response", {})
                response_text = ai_response.get("response", "")
                
                status = "PASS" if len(response_text) > 50 else "WARN (Short)"
                
                print(f"Result: {status} ({duration:.2f}s)")
                print(f"Response Preview: {response_text[:150]}...")
                
                results.append({
                    **q,
                    "status": status,
                    "duration": duration,
                    "response_preview": response_text[:100]
                })
            else:
                print(f"Result: FAIL (HTTP {response.status_code})")
                print(response.text)
                results.append({
                    **q,
                    "status": "FAIL",
                    "duration": duration,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"Result: ERROR ({e})")
            results.append({
                **q,
                "status": "ERROR",
                "duration": time.time() - start_time,
                "error": str(e)
            })
            
        # Small delay between requests
        time.sleep(2)

    # Summary
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    print(f"{'ID':<10} | {'Axis':<15} | {'Status':<10} | {'Time':<6}")
    print("-" * 60)
    for r in results:
        print(f"{r['id']:<10} | {r['axis']:<15} | {r['status']:<10} | {r['duration']:.1f}s")
    print("="*60)

if __name__ == "__main__":
    run_benchmark()

