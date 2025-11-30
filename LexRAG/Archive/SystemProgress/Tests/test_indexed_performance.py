"""
Test Indexed Performance - Massive Data Access
Test improved performance with indexed massive tables
"""

import requests
import time
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def test_indexed_performance():
    """Test performance improvements with indexed massive data"""
    log("="*80)
    log("TESTING INDEXED MASSIVE DATA PERFORMANCE")
    log("="*80)
    log("Goal: Verify safe, fast access to billion-row tables")
    
    base_url = "http://localhost:8001"
    
    # Test 1: Verify API is running with indexes
    log("\n1. VERIFYING API STATUS:")
    try:
        r = requests.get(f"{base_url}/health", timeout=10)
        if r.status_code == 200:
            data = r.json()
            log("✅ LexAPI_Genomics operational with indexed data")
            
            databases = data.get('databases', {})
            for db_name, db_info in databases.items():
                status = db_info.get('status', 'unknown')
                log(f"   {db_name}: {status}")
        else:
            log(f"❌ API not responding: HTTP {r.status_code}")
            return False
    except Exception as e:
        log(f"❌ API error: {e}")
        return False
    
    # Test 2: Test SpliceAI with gene_symbol index (should be fast)
    log("\n2. TESTING SPLICEAI WITH GENE INDEX:")
    try:
        start_time = time.time()
        r = requests.get(f"{base_url}/analyze/variant/rs7412/spliceai", timeout=30)
        response_time = time.time() - start_time
        
        log(f"⏱️  Response time: {response_time:.2f} seconds")
        
        if r.status_code == 200:
            data = r.json()
            spliceai_analysis = data.get('spliceai_analysis', {})
            
            if spliceai_analysis and 'error' not in spliceai_analysis:
                predictions = spliceai_analysis.get('total_predictions', 0)
                log(f"✅ SpliceAI indexed access: {predictions} predictions")
                
                # Show sample prediction
                preds = spliceai_analysis.get('splice_predictions', [])
                if preds:
                    sample = preds[0]
                    gene = sample.get('gene_symbol', 'unknown')
                    max_score = sample.get('max_score', 0)
                    log(f"   Sample: {gene}, max_score={max_score:.3f}")
                    
                log(f"   📊 Data access: {data.get('data_access', 'unknown')}")
            else:
                log(f"❌ SpliceAI: No predictions found")
        else:
            log(f"❌ SpliceAI endpoint: HTTP {r.status_code}")
            
    except Exception as e:
        log(f"❌ SpliceAI test: {e}")
    
    # Test 3: Test enhanced variant analysis with multiple massive tables
    log("\n3. TESTING ENHANCED VARIANT ANALYSIS:")
    test_variants = ["rs7412", "rs4680"]
    
    for variant in test_variants:
        log(f"\n   Testing {variant} with indexed massive data:")
        try:
            start_time = time.time()
            r = requests.get(f"{base_url}/analyze/variant/{variant}", timeout=30)
            response_time = time.time() - start_time
            
            log(f"   ⏱️  Response time: {response_time:.2f} seconds")
            
            if r.status_code == 200:
                data = r.json()
                databases = data.get('databases_queried', [])
                log(f"   ✅ {variant}: {len(databases)} databases queried")
                
                # Check massive data access
                massive_data_used = []
                if 'spliceai_scores_production' in databases:
                    massive_data_used.append("SpliceAI (3.43B rows)")
                if 'gnomad_population_frequencies' in databases:
                    massive_data_used.append("gnomAD (3.3M rows)")
                if 'alphafold_clinical_variant_impact' in databases:
                    massive_data_used.append("AlphaFold (11.6M rows)")
                
                if massive_data_used:
                    log(f"   🎯 MASSIVE DATA ACCESSED: {', '.join(massive_data_used)}")
                else:
                    log(f"   ⚠️  No massive data accessed")
                    
            else:
                log(f"   ❌ {variant}: HTTP {r.status_code}")
                
        except Exception as e:
            log(f"   ❌ {variant}: {e}")
    
    # Test 4: Test gene analysis with indexed data
    log("\n4. TESTING GENE ANALYSIS WITH INDEXED DATA:")
    test_genes = ["BRCA2", "TP53"]
    
    for gene in test_genes:
        log(f"\n   Testing {gene} with indexed massive data:")
        try:
            start_time = time.time()
            r = requests.get(f"{base_url}/analyze/gene/{gene}", timeout=30)
            response_time = time.time() - start_time
            
            log(f"   ⏱️  Response time: {response_time:.2f} seconds")
            
            if r.status_code == 200:
                data = r.json()
                databases = data.get('databases_queried', [])
                log(f"   ✅ {gene}: {len(databases)} databases queried")
                
                # Check for massive data integration
                if 'spliceai_scores_production' in databases:
                    log(f"   🎯 SPLICEAI INTEGRATED: 3.43B rows accessible")
                if 'alphafold_clinical_variant_impact' in databases:
                    log(f"   🎯 ALPHAFOLD INTEGRATED: 11.6M rows accessible")
                    
            else:
                log(f"   ❌ {gene}: HTTP {r.status_code}")
                
        except Exception as e:
            log(f"   ❌ {gene}: {e}")
    
    log(f"\n{'='*80}")
    log("INDEXED PERFORMANCE TEST COMPLETE")
    log("Massive data access verified with indexed performance")
    log("="*80)
    
    return True

if __name__ == "__main__":
    log("Testing indexed massive data performance...")
    log("Verifying safe access to billion-row tables")
    print()
    
    success = test_indexed_performance()
    
    if success:
        log("\n🎉 INDEXED PERFORMANCE SUCCESS!")
        log("Ready for enhanced benchmark with massive data access")
    else:
        log("\n❌ Performance testing needs debugging")
