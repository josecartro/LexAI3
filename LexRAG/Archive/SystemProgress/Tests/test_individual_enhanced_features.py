"""
Test Individual Enhanced Features
Test each enhanced feature separately to find performance bottlenecks
"""

import requests
import time
import psutil
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def monitor_system():
    """Monitor system resources"""
    memory = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent(interval=1)
    return memory, cpu

def test_feature(feature_name, url, timeout=15):
    """Test individual feature with resource monitoring"""
    log(f"\n🧪 TESTING: {feature_name}")
    log(f"   URL: {url}")
    
    # Pre-test system state
    pre_memory, pre_cpu = monitor_system()
    log(f"   Pre-test: Memory {pre_memory:.1f}%, CPU {pre_cpu:.1f}%")
    
    try:
        start_time = time.time()
        
        # Make request with monitoring
        r = requests.get(url, timeout=timeout)
        
        response_time = time.time() - start_time
        
        # Post-test system state
        post_memory, post_cpu = monitor_system()
        log(f"   Post-test: Memory {post_memory:.1f}%, CPU {post_cpu:.1f}%")
        
        if r.status_code == 200:
            data = r.json()
            
            log(f"   ✅ SUCCESS: {feature_name}")
            log(f"   ⏱️  Response time: {response_time:.2f}s")
            log(f"   📊 Memory impact: {post_memory - pre_memory:+.1f}%")
            log(f"   📊 CPU impact: {post_cpu - pre_cpu:+.1f}%")
            
            # Check response size
            response_size = len(str(data))
            log(f"   📦 Response size: {response_size:,} characters")
            
            # Check databases used
            databases = data.get('databases_queried', [])
            if databases:
                log(f"   🗄️  Databases: {databases}")
            
            return {
                'feature': feature_name,
                'success': True,
                'response_time': response_time,
                'memory_impact': post_memory - pre_memory,
                'cpu_impact': post_cpu - pre_cpu,
                'response_size': response_size,
                'databases': databases
            }
        else:
            log(f"   ❌ FAILED: HTTP {r.status_code}")
            return {
                'feature': feature_name,
                'success': False,
                'error': f'HTTP {r.status_code}',
                'response_time': response_time
            }
            
    except Exception as e:
        response_time = time.time() - start_time
        post_memory, post_cpu = monitor_system()
        
        log(f"   ❌ ERROR: {str(e)[:50]}")
        log(f"   ⏱️  Time before error: {response_time:.2f}s")
        log(f"   📊 Memory at error: {post_memory:.1f}%")
        
        return {
            'feature': feature_name,
            'success': False,
            'error': str(e)[:50],
            'response_time': response_time,
            'memory_at_error': post_memory
        }

def main():
    log("="*80)
    log("TESTING INDIVIDUAL ENHANCED FEATURES")
    log("="*80)
    log("Goal: Find which enhanced feature is causing performance issues")
    
    # Test each enhanced feature individually
    features_to_test = [
        ("Basic Gene Analysis", "http://localhost:8001/analyze/gene/TP53"),
        ("Protein Connections", "http://localhost:8001/analyze/gene/BRCA2/proteins"),
        ("Expression Effects", "http://localhost:8001/analyze/variant/rs7412/expression"),
        ("Splicing Effects", "http://localhost:8001/analyze/variant/rs7412/splicing"),
        ("SpliceAI Predictions", "http://localhost:8001/analyze/variant/rs7412/spliceai"),
        ("Protein Structure", "http://localhost:8001/analyze/variant/rs7412/protein_structure"),
        ("Drug Metabolism (Metabolics)", "http://localhost:8005/analyze/drug_metabolism/codeine"),
        ("Organ Analysis (Anatomics)", "http://localhost:8002/analyze/organ/brain")
    ]
    
    results = []
    
    for feature_name, url in features_to_test:
        result = test_feature(feature_name, url)
        results.append(result)
        
        # Recovery pause between tests
        log(f"   💤 Recovery pause...")
        time.sleep(5)
    
    # Analysis summary
    log(f"\n{'='*80}")
    log("PERFORMANCE ANALYSIS SUMMARY")
    log('='*80)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    log(f"✅ Successful features: {len(successful)}")
    log(f"❌ Failed features: {len(failed)}")
    
    if successful:
        log(f"\n✅ WORKING FEATURES:")
        for result in successful:
            log(f"   {result['feature']}: {result['response_time']:.2f}s")
    
    if failed:
        log(f"\n❌ PROBLEMATIC FEATURES:")
        for result in failed:
            log(f"   {result['feature']}: {result.get('error', 'unknown error')}")
    
    # Find bottlenecks
    if successful:
        slowest = max(successful, key=lambda x: x['response_time'])
        fastest = min(successful, key=lambda x: x['response_time'])
        
        log(f"\n📊 PERFORMANCE RANGE:")
        log(f"   Fastest: {fastest['feature']} ({fastest['response_time']:.2f}s)")
        log(f"   Slowest: {slowest['feature']} ({slowest['response_time']:.2f}s)")
        
        if slowest['response_time'] > 10:
            log(f"   🚨 BOTTLENECK: {slowest['feature']} is too slow")

if __name__ == "__main__":
    main()
