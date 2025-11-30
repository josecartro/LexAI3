import duckdb

conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)

print("Checking AlphaFold data...")

# Check BRCA2
brca2_count = conn.execute("SELECT COUNT(*) FROM alphafold_clinical_variant_impact WHERE gene_symbol = 'BRCA2'").fetchone()[0]
print(f"BRCA2 entries: {brca2_count}")

# Check SOX10  
sox10_count = conn.execute("SELECT COUNT(*) FROM alphafold_clinical_variant_impact WHERE gene_symbol = 'SOX10'").fetchone()[0]
print(f"SOX10 entries: {sox10_count}")

if brca2_count > 0:
    sample = conn.execute("SELECT uniprot_id, protein_name FROM alphafold_clinical_variant_impact WHERE gene_symbol = 'BRCA2' LIMIT 1").fetchone()
    print(f"BRCA2 sample: {sample}")

conn.close()
