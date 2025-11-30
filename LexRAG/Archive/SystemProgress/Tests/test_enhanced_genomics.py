"""
Test Enhanced LexAPI_Genomics
Test both protein and pathway connection integrations
"""

import requests
import time

def test_enhanced_genomics():
    """Test the enhanced genomics API safely"""
    print("="*70)
    print("TESTING ENHANCED LEXAPI_GENOMICS")
    print("="*70)
    print("Testing: Protein connections + Pathway connections")
    
    base_url = "http://localhost:8001"
    
    # Wait for API
    print("\nWaiting 15 seconds for enhanced API...")
    time.sleep(15)
    
    # Test 1: Enhanced gene analysis with both connections
    print("\n1. TESTING ENHANCED GENE ANALYSIS:")
    test_genes = ["BRCA2", "TP53", "CDS"]  # CDS has pathway connections
    
    for gene in test_genes:
        print(f"\n   Testing enhanced {gene} analysis:")
        try:
            r = requests.get(f"{base_url}/analyze/gene/{gene}", timeout=15)
            if r.status_code == 200:
                data = r.json()
                print(f"     [SUCCESS] {gene} enhanced analysis working")
                
                databases = data.get('databases_queried', [])
                print(f"     Databases: {len(databases)} - {databases}")
                
                # Check protein connections
                proteins = data.get('protein_connections', {})
                if proteins and 'error' not in proteins:
                    total_proteins = proteins.get('total_proteins', 0)
                    print(f"     Proteins: {total_proteins} connections")
                else:
                    print(f"     Proteins: None found")
                
                # Check pathway connections
                pathways = data.get('pathway_connections', {})
                if pathways and 'error' not in pathways:
                    total_pathways = pathways.get('total_pathways', 0)
                    print(f"     Pathways: {total_pathways} connections")
                    if total_pathways > 0:
                        sample_pathway = pathways.get('pathway_connections', [{}])[0].get('pathway_name', 'unknown')
                        print(f"     Sample pathway: {sample_pathway[:50]}...")
                else:
                    print(f"     Pathways: None found")
                    
            else:
                print(f"     [ERROR] {gene} analysis: HTTP {r.status_code}")
                
        except Exception as e:
            print(f"     [ERROR] {gene} analysis: {e}")
    
    # Test 2: New protein endpoint
    print("\n2. TESTING PROTEIN ENDPOINT:")
    try:
        r = requests.get(f"{base_url}/analyze/gene/BRCA2/proteins", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print("   [SUCCESS] Protein endpoint working")
            
            protein_analysis = data.get('protein_analysis', {})
            if 'total_proteins' in protein_analysis:
                print(f"   BRCA2 proteins: {protein_analysis['total_proteins']}")
            
            enhancement = data.get('enhancement', '')
            print(f"   Enhancement: {enhancement}")
            
        else:
            print(f"   [ERROR] Protein endpoint: HTTP {r.status_code}")
            
    except Exception as e:
        print(f"   [ERROR] Protein endpoint: {e}")
    
    # Test 3: New pathway endpoint
    print("\n3. TESTING PATHWAY ENDPOINT:")
    try:
        r = requests.get(f"{base_url}/analyze/gene/CDS/pathways", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print("   [SUCCESS] Pathway endpoint working")
            
            pathway_analysis = data.get('pathway_analysis', {})
            if 'total_pathways' in pathway_analysis:
                print(f"   CDS pathways: {pathway_analysis['total_pathways']}")
            
            enhancement = data.get('enhancement', '')
            print(f"   Enhancement: {enhancement}")
            
        else:
            print(f"   [ERROR] Pathway endpoint: HTTP {r.status_code}")
            
    except Exception as e:
        print(f"   [ERROR] Pathway endpoint: {e}")
    
    print("\n" + "="*70)
    print("ENHANCED GENOMICS TEST COMPLETE")
    print("Integration status: Protein connections + Limited pathway connections")
    print("="*70)

if __name__ == "__main__":
    test_enhanced_genomics()
