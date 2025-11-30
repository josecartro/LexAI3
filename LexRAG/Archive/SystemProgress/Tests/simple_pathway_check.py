import duckdb

print("SAFE PATHWAY CHECK")
print("="*30)

conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)

# Check total genes with pathways
total_genes = conn.execute("SELECT COUNT(DISTINCT gene_symbol) FROM kegg_gene_pathway_links WHERE gene_symbol IS NOT NULL").fetchone()[0]
print(f"Genes with pathways: {total_genes}")

# Check specific genes
test_genes = ["BRCA2", "TP53", "CFTR"]
for gene in test_genes:
    count = conn.execute("SELECT COUNT(*) FROM kegg_gene_pathway_links WHERE gene_symbol = ?", [gene]).fetchone()[0]
    print(f"{gene} pathways: {count}")

conn.close()
print("Safe check complete")
