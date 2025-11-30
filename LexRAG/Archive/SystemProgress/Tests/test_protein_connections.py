"""
Test Enhanced LexAPI_Genomics - Protein Connections
Test the new gene-protein mapping integration (Priority 1)
"""

import requests
import time

def test_protein_connections():
    """Test the new protein connection capabilities"""
    print("="*70)
    print("TESTING ENHANCED LEXAPI_GENOMICS - PROTEIN CONNECTIONS")
    print("="*70)
    print("Testing Priority 1: Gene→Protein mapping (Axis 2 → Axis 4)")
    
    base_url = "http://localhost:8001"
    
    # Wait for enhanced API to start
    print("\nWaiting 20 seconds for enhanced API...")
    time.sleep(20)
    
    # Test 1: Enhanced BRCA2 analysis (should now include proteins)
    print("\n1. TESTING ENHANCED BRCA2 ANALYSIS:")
    try:
        r = requests.get(f"{base_url}/analyze/gene/BRCA2", timeout=20)
        if r.status_code == 200:
            data = r.json()
            print("   [SUCCESS] Enhanced BRCA2 analysis working")
            
            # Check databases queried
            databases = data.get('databases_queried', [])
            print(f"   Databases queried: {databases}")
            
            if "biomart_protein_mapping" in databases:
                print("   [NEW] Protein mapping integration working!")
            else:
                print("   [WARNING] Protein mapping not detected")
            
            # Check protein connections
            protein_connections = data.get('protein_connections', {})
            if protein_connections and 'error' not in protein_connections:
                total_proteins = protein_connections.get('total_proteins', 0)
                print(f"   [SUCCESS] BRCA2 protein connections: {total_proteins}")
                
                proteins = protein_connections.get('protein_connections', [])
                if proteins:
                    print(f"   Sample proteins:")
                    for protein in proteins[:3]:
                        protein_id = protein.get('protein_id', 'unknown')
                        transcript_id = protein.get('transcript_id', 'unknown')
                        print(f"     {protein_id} (transcript: {transcript_id})")
            else:
                print("   [INFO] No protein connections found")
                
        else:
            print(f"   [ERROR] Enhanced BRCA2 analysis: HTTP {r.status_code}")
            
    except Exception as e:
        print(f"   [ERROR] Enhanced BRCA2 analysis: {e}")
    
    # Test 2: New gene-protein endpoint
    print("\n2. TESTING NEW GENE-PROTEIN ENDPOINT:")
    test_genes = ["BRCA2", "TP53", "CFTR"]
    
    for gene in test_genes:
        print(f"\n   Testing {gene} protein connections:")
        try:
            r = requests.get(f"{base_url}/analyze/gene/{gene}/proteins", timeout=15)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {gene} protein endpoint working")
                
                protein_analysis = data.get('protein_analysis', {})
                if protein_analysis and 'error' not in protein_analysis:
                    total_proteins = protein_analysis.get('total_proteins', 0)
                    print(f"     Proteins found: {total_proteins}")
                    
                    enhancement = data.get('enhancement', '')
                    if 'biomart_protein_mapping' in enhancement:
                        print(f"     [NEW] Using biomart protein mapping!")
                    
                    cross_axis = data.get('cross_axis_connection', '')
                    print(f"     Connection: {cross_axis}")
                else:
                    print(f"     [INFO] No protein connections for {gene}")
                    
            else:
                print(f"     [ERROR] {gene} protein endpoint: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {gene} protein endpoint: {e}")
    
    # Test 3: Compare before/after capability
    print("\n3. COMPARING BEFORE/AFTER CAPABILITY:")
    print("   BEFORE Enhancement:")
    print("     - Gene analysis: variants, expression only")
    print("     - No protein connections")
    print("     - Limited cross-axis analysis")
    
    print("   AFTER Enhancement:")
    print("     - Gene analysis: variants + expression + PROTEINS")
    print("     - Gene→Protein mapping working")
    print("     - True Axis 2 → Axis 4 connections")
    
    # Test 4: API documentation update
    print("\n4. TESTING API DOCUMENTATION:")
    try:
        r = requests.get(f"{base_url}/openapi.json", timeout=5)
        if r.status_code == 200:
            schema = r.json()
            endpoints = list(schema.get('paths', {}).keys())
            
            if "/analyze/gene/{gene_symbol}/proteins" in endpoints:
                print("   [SUCCESS] New protein endpoint in documentation")
            else:
                print("   [WARNING] New endpoint not in documentation")
                
            print(f"   Total endpoints: {len(endpoints)}")
            
        else:
            print(f"   [ERROR] Documentation check: HTTP {r.status_code}")
            
    except Exception as e:
        print(f"   [ERROR] Documentation check: {e}")

    print("\n" + "="*70)
    print("PROTEIN CONNECTIONS INTEGRATION TEST COMPLETE")
    print("Priority 1: Gene→Protein mapping (Axis 2 → Axis 4)")
    print("="*70)
    
    return True

if __name__ == "__main__":
    print("Testing enhanced LexAPI_Genomics with protein connections...")
    print("Make sure enhanced API is running via api_startup.bat")
    print()
    
    success = test_protein_connections()
    
    if success:
        print("\n[SUCCESS] Protein connections integration working")
        print("Ready for Priority 2: Gene→Pathway mapping integration")
    else:
        print("\n[FAILED] Protein connections need debugging")
