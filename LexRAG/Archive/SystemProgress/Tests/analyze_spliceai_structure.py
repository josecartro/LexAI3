import duckdb
import time

print("ANALYZING 3.43B SPLICEAI TABLE STRUCTURE")
print("="*60)
print("Goal: Understand how to normalize into separate tables")

conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)

print("\n1. TABLE SCHEMA ANALYSIS:")
columns = conn.execute("DESCRIBE spliceai_scores_production").fetchall()
print(f"Total columns: {len(columns)}")
for col_name, col_type, nullable, key, default, extra in columns:
    print(f"   {col_name}: {col_type}")

print("\n2. DATA UNIQUENESS ANALYSIS:")

# Check unique genes
gene_count = conn.execute("SELECT COUNT(DISTINCT gene_symbol) FROM spliceai_scores_production WHERE gene_symbol IS NOT NULL").fetchone()[0]
print(f"Unique genes: {gene_count:,}")

# Check unique variants
variant_count = conn.execute("SELECT COUNT(DISTINCT variant_id) FROM spliceai_scores_production WHERE variant_id IS NOT NULL").fetchone()[0]
print(f"Unique variants: {variant_count:,}")

# Check unique chromosomes
chrom_count = conn.execute("SELECT COUNT(DISTINCT chrom) FROM spliceai_scores_production").fetchone()[0]
print(f"Unique chromosomes: {chrom_count}")

print("\n3. REPETITION ANALYSIS:")

# Check how many rows per gene (average)
avg_rows_per_gene = conn.execute("""
    SELECT AVG(gene_row_count) FROM (
        SELECT gene_symbol, COUNT(*) as gene_row_count 
        FROM spliceai_scores_production 
        WHERE gene_symbol IS NOT NULL 
        GROUP BY gene_symbol
    )
""").fetchone()[0]
print(f"Average rows per gene: {avg_rows_per_gene:,.0f}")

# Check sample gene distribution
print("\nSample gene row counts:")
gene_samples = conn.execute("""
    SELECT gene_symbol, COUNT(*) as row_count
    FROM spliceai_scores_production
    WHERE gene_symbol IN ('BRCA1', 'BRCA2', 'TP53', 'CFTR', 'APOE')
    GROUP BY gene_symbol
    ORDER BY row_count DESC
""").fetchall()

for gene, count in gene_samples:
    print(f"   {gene}: {count:,} rows")

print("\n4. SCORE DISTRIBUTION ANALYSIS:")
score_stats = conn.execute("""
    SELECT 
        COUNT(*) as total_rows,
        COUNT(CASE WHEN ABS(acceptor_gain_score) > 0.5 OR ABS(donor_gain_score) > 0.5 THEN 1 END) as high_scores,
        COUNT(CASE WHEN ABS(acceptor_gain_score) > 0.2 OR ABS(donor_gain_score) > 0.2 THEN 1 END) as medium_scores,
        COUNT(CASE WHEN ABS(acceptor_gain_score) > 0.1 OR ABS(donor_gain_score) > 0.1 THEN 1 END) as low_scores
    FROM spliceai_scores_production
""").fetchone()

total, high, medium, low = score_stats
print(f"Score distribution:")
print(f"   High impact (>0.5): {high:,} ({(high/total)*100:.2f}%)")
print(f"   Medium impact (>0.2): {medium:,} ({(medium/total)*100:.2f}%)")
print(f"   Low impact (>0.1): {low:,} ({(low/total)*100:.2f}%)")
print(f"   Very low (≤0.1): {total-low:,} ({((total-low)/total)*100:.1f}%)")

print("\n5. PROPOSED NORMALIZATION STRUCTURE:")
print("""
NORMALIZED APPROACH:

Table 1: splice_genes (one row per gene)
- gene_symbol, gene_id, chromosome, gene_start, gene_end
- {gene_count:,} rows (very fast lookups)

Table 2: splice_variants_important (clinical relevance)
- variant_id, gene_symbol, position, scores >0.2
- ~{medium:,} rows (manageable, clinically relevant)

Table 3: splice_variants_research (research data)  
- variant_id, gene_symbol, position, scores 0.1-0.2
- ~{(low-medium):,} rows (additional research data)

Table 4: splice_scores (just the scores)
- variant_id, acceptor_gain, acceptor_loss, donor_gain, donor_loss
- Links to variants tables via variant_id

BENEFITS:
- Gene lookup: Table 1 (instant)
- Clinical analysis: Table 1 + 2 (fast)
- Research analysis: Table 1 + 2 + 3 (comprehensive)
- Each table indexable and manageable
""".format(
    gene_count=gene_count,
    medium=medium, 
    low=low
))

conn.close()
print("\n🎯 RECOMMENDATION: Implement normalized structure for practical use")
