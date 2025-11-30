import requests

print("Testing enhanced gene analysis...")

try:
    r = requests.get("http://localhost:8001/analyze/gene/BRCA2", timeout=20)
    if r.status_code == 200:
        data = r.json()
        print("✅ Enhanced BRCA2 analysis working")
        
        databases = data.get('databases_queried', [])
        print(f"Databases: {len(databases)} - {databases}")
        
        # Check enhanced features
        proteins = data.get('protein_connections', {})
        if proteins and 'error' not in proteins:
            protein_count = proteins.get('total_proteins', 0)
            print(f"✅ Proteins: {protein_count} connections")
        
        splice_preds = data.get('spliceai_predictions', {})
        if splice_preds and 'error' not in splice_preds:
            splice_count = splice_preds.get('total_splice_variants', 0)
            print(f"✅ SpliceAI: {splice_count} splice variants from optimized table")
        else:
            print(f"❌ SpliceAI: Not included")
        
        gtex_expr = data.get('gtex_expression_summary', {})
        if gtex_expr and 'error' not in gtex_expr:
            expr_variants = gtex_expr.get('variants_with_expression_effects', 0)
            tissues = gtex_expr.get('tissues_affected', 0)
            print(f"✅ GTEx: {expr_variants} variants, {tissues} tissues")
        else:
            print(f"❌ GTEx: Not included")
            
        # Count total enhanced features
        enhanced_features = len([k for k in data.keys() if k not in ["gene_symbol", "timestamp"]])
        print(f"🎯 Enhanced analysis includes: {enhanced_features} data types")
        
        print("\n🎯 READY FOR ENHANCED BENCHMARK TEST")
        
    else:
        print(f"❌ API error: HTTP {r.status_code}")
except Exception as e:
    print(f"❌ API test failed: {e}")

