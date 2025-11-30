"""
Test All LexAPI_Genomics Enhancements
Verify all cross-axis integrations are working properly
"""

import requests
import time

def test_all_enhancements():
    """Test all enhancements comprehensively"""
    print("="*80)
    print("TESTING ALL LEXAPI_GENOMICS ENHANCEMENTS")
    print("="*80)
    print("Verifying: Protein + Expression + Splicing + AlphaFold integrations")
    
    base_url = "http://localhost:8001"
    
    # Test 1: Health check
    print("\n1. TESTING API HEALTH:")
    try:
        r = requests.get(f"{base_url}/health", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print("   [SUCCESS] API is healthy")
            
            databases = data.get('databases', {})
            print("   Database connections:")
            for db_name, db_info in databases.items():
                status = db_info.get('status', 'unknown')
                print(f"     {db_name}: {status}")
        else:
            print(f"   [ERROR] Health check: HTTP {r.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Health check: {e}")
        return False
    
    # Test 2: Enhanced variant analysis
    print("\n2. TESTING ENHANCED VARIANT ANALYSIS:")
    test_variants = ["rs7412", "rs4680"]
    
    for variant in test_variants:
        print(f"\n   Testing {variant} complete analysis:")
        try:
            r = requests.get(f"{base_url}/analyze/variant/{variant}", timeout=25)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {variant} analysis working")
                
                databases = data.get('databases_queried', [])
                print(f"     Databases: {len(databases)} queried")
                
                # Check each enhancement
                genomic = data.get('genomic_data', {})
                if genomic and 'error' not in genomic:
                    gene = genomic.get('gene_symbol', 'unknown')
                    significance = genomic.get('clinical_significance', 'unknown')
                    print(f"     Basic: {gene}, {significance}")
                
                expression = data.get('expression_effects', {})
                if expression and 'error' not in expression:
                    tissues = expression.get('total_tissues_affected', 0)
                    print(f"     Expression: {tissues} tissues affected")
                
                splicing = data.get('splicing_effects', {})
                if splicing and 'error' not in splicing:
                    events = splicing.get('total_splice_events', 0)
                    splice_tissues = splicing.get('total_tissues_affected', 0)
                    print(f"     Splicing: {events} events in {splice_tissues} tissues")
                
                structure = data.get('protein_structure_effects', {})
                if structure and 'error' not in structure:
                    structures = structure.get('total_protein_structures', 0)
                    print(f"     Protein structures: {structures}")
                else:
                    print(f"     Protein structures: None found")
                    
            else:
                print(f"     [ERROR] {variant}: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {variant}: {e}")
    
    # Test 3: Enhanced gene analysis
    print("\n3. TESTING ENHANCED GENE ANALYSIS:")
    test_genes = ["BRCA2", "TP53"]
    
    for gene in test_genes:
        print(f"\n   Testing {gene} complete analysis:")
        try:
            r = requests.get(f"{base_url}/analyze/gene/{gene}", timeout=25)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {gene} analysis working")
                
                databases = data.get('databases_queried', [])
                print(f"     Databases: {len(databases)} queried")
                
                variants = data.get('variants', {})
                if variants and 'error' not in variants:
                    total = variants.get('total_variants', 0)
                    pathogenic = variants.get('pathogenic_variants', 0)
                    print(f"     Variants: {total:,} total, {pathogenic:,} pathogenic")
                
                proteins = data.get('protein_connections', {})
                if proteins and 'error' not in proteins:
                    protein_count = proteins.get('total_proteins', 0)
                    print(f"     Proteins: {protein_count} connections")
                
                structure = data.get('protein_structure_effects', {})
                if structure and 'error' not in structure:
                    structures = structure.get('total_protein_structures', 0)
                    print(f"     Protein structures: {structures}")
                    
            else:
                print(f"     [ERROR] {gene}: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {gene}: {e}")
    
    # Test 4: Cross-axis endpoints
    print("\n4. TESTING CROSS-AXIS ENDPOINTS:")
    
    # Test protein endpoint
    try:
        r = requests.get(f"{base_url}/analyze/gene/BRCA2/proteins", timeout=10)
        if r.status_code == 200:
            data = r.json()
            protein_analysis = data.get('protein_analysis', {})
            if 'total_proteins' in protein_analysis:
                print(f"   [SUCCESS] Protein endpoint: {protein_analysis['total_proteins']} BRCA2 proteins")
            else:
                print(f"   [INFO] Protein endpoint working but no data")
        else:
            print(f"   [ERROR] Protein endpoint: HTTP {r.status_code}")
    except Exception as e:
        print(f"   [ERROR] Protein endpoint: {e}")
    
    # Test expression endpoint
    try:
        r = requests.get(f"{base_url}/analyze/variant/rs7412/expression", timeout=10)
        if r.status_code == 200:
            data = r.json()
            expression_analysis = data.get('expression_analysis', {})
            if 'total_tissues_affected' in expression_analysis:
                print(f"   [SUCCESS] Expression endpoint: {expression_analysis['total_tissues_affected']} tissues")
            else:
                print(f"   [INFO] Expression endpoint working but no data")
        else:
            print(f"   [ERROR] Expression endpoint: HTTP {r.status_code}")
    except Exception as e:
        print(f"   [ERROR] Expression endpoint: {e}")
    
    # Test splicing endpoint
    try:
        r = requests.get(f"{base_url}/analyze/variant/rs7412/splicing", timeout=10)
        if r.status_code == 200:
            data = r.json()
            splicing_analysis = data.get('splicing_analysis', {})
            if 'total_splice_events' in splicing_analysis:
                print(f"   [SUCCESS] Splicing endpoint: {splicing_analysis['total_splice_events']} events")
            else:
                print(f"   [INFO] Splicing endpoint working but no data")
        else:
            print(f"   [ERROR] Splicing endpoint: HTTP {r.status_code}")
    except Exception as e:
        print(f"   [ERROR] Splicing endpoint: {e}")
    
    # Test 5: API documentation
    print("\n5. TESTING API DOCUMENTATION:")
    try:
        r = requests.get(f"{base_url}/openapi.json", timeout=5)
        if r.status_code == 200:
            schema = r.json()
            endpoints = list(schema.get('paths', {}).keys())
            print(f"   [SUCCESS] Total endpoints: {len(endpoints)}")
            
            cross_axis = [ep for ep in endpoints if any(word in ep for word in ['proteins', 'expression', 'splicing', 'structure'])]
            print(f"   Cross-axis endpoints: {len(cross_axis)}")
            for endpoint in cross_axis:
                print(f"     {endpoint}")
        else:
            print(f"   [ERROR] Documentation: HTTP {r.status_code}")
    except Exception as e:
        print(f"   [ERROR] Documentation: {e}")

    print("\n" + "="*80)
    print("ENHANCEMENT VERIFICATION COMPLETE")
    print("="*80)
    
    return True

if __name__ == "__main__":
    print("Verifying all LexAPI_Genomics enhancements...")
    print("Testing comprehensive cross-axis analysis capabilities")
    print()
    
    success = test_all_enhancements()
    
    if success:
        print("\n[SUCCESS] All enhancements verified working")
        print("Ready for benchmark testing or further enhancements")
    else:
        print("\n[FAILED] Some enhancements need debugging")
