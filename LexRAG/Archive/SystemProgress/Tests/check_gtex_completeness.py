import requests

print("CHECKING GTEX DATA COMPLETENESS")
print("="*50)

try:
    # Check total GTEx records
    r = requests.post("http://localhost:8123/?password=simple123", data="SELECT COUNT(*) FROM expression_db.tissue_expression")
    total_records = r.text.strip()
    print(f"Total GTEx records: {total_records}")
    
    # Check tissue coverage
    r = requests.post("http://localhost:8123/?password=simple123", data="SELECT COUNT(DISTINCT tissue) FROM expression_db.tissue_expression")
    tissue_count = r.text.strip()
    print(f"Tissues covered: {tissue_count}")
    
    # Check gene coverage
    r = requests.post("http://localhost:8123/?password=simple123", data="SELECT COUNT(DISTINCT gene_symbol) FROM expression_db.tissue_expression WHERE gene_symbol != 'unknown'")
    gene_count = r.text.strip()
    print(f"Genes with expression: {gene_count}")
    
    # Sample tissues
    r = requests.post("http://localhost:8123/?password=simple123", data="SELECT DISTINCT tissue FROM expression_db.tissue_expression LIMIT 10")
    tissues = r.text.strip().split('\n')
    print(f"Sample tissues: {tissues[:5]}")
    
    print("\nASSESSMENT:")
    if int(total_records) > 400000000:
        print("GOOD: Substantial GTEx data imported")
        print(f"Success rate: ~108/118 files ({108/118*100:.1f}%)")
    else:
        print("LIMITED: May be missing important files")
        
    print("\nMISSING FILES THAT FAILED:")
    failed_files = [
        "GTEx_Analysis_2021-02-11_v10_WholeGenomeSeq_953Indiv.lookup_table.txt.gz",
        "GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct.gz",
        "GTEx_Analysis_v10_RSEMv1.3.3_transcripts_expected_count.txt.gz", 
        "GTEx_Analysis_v10_RSEMv1.3.3_transcripts_tpm.txt.gz"
    ]
    
    for file in failed_files:
        print(f"- {file}")
    
    print("\nNEXT STEPS:")
    print("1. Retry failed GTEx files with larger timeouts")
    print("2. Continue with remaining datasets (smallest to largest)")
    print("3. Save SpliceAI (3.43B rows) for last")
    
except Exception as e:
    print(f"Error: {e}")

print("\nGTEx completeness check done")
