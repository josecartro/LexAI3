import duckdb
import time

print("CREATING PRACTICAL SPLICEAI TABLE - MULTIPLE CRITERIA")
print("="*60)

conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=False)

# Set optimizations
conn.execute("SET memory_limit='12GB'")
conn.execute("SET threads=2")

print("Strategy: Keep data by practical criteria, not just scores")

# Drop old table
conn.execute("DROP TABLE IF EXISTS spliceai_practical")

# Create practical table with multiple inclusion criteria
create_sql = """
    CREATE TABLE spliceai_practical AS
    SELECT chrom, pos_bp, variant_id, ref, alt, gene_symbol,
           acceptor_gain_score, acceptor_loss_score,
           donor_gain_score, donor_loss_score,
           variant_type
    FROM spliceai_scores_production
    WHERE gene_symbol IS NOT NULL
    AND (
        -- High impact (definitely keep)
        (ABS(acceptor_gain_score) > 0.2 OR ABS(acceptor_loss_score) > 0.2 
         OR ABS(donor_gain_score) > 0.2 OR ABS(donor_loss_score) > 0.2)
        
        -- OR important genes (even with lower scores)
        OR gene_symbol IN (
            'BRCA1', 'BRCA2', 'TP53', 'CFTR', 'APOE', 'EGFR', 'KRAS', 'APC',
            'MLH1', 'MSH2', 'ATM', 'CHEK2', 'PALB2', 'PTEN', 'VHL', 'RB1',
            'FOXP2', 'PKD1', 'PKD2', 'NF1', 'NF2', 'TSC1', 'TSC2'
        )
        
        -- OR common variants (population relevance)
        OR variant_id IN (
            SELECT rsid FROM gnomad_population_frequencies 
            WHERE allele_frequency > 0.01
        )
    )
"""

print("Creating practical table with multiple criteria...")
print("- Scores >0.2 (broader clinical relevance)")
print("- All variants in important disease genes") 
print("- Common population variants")

start_time = time.time()
conn.execute(create_sql)
creation_time = time.time() - start_time

new_count = conn.execute("SELECT COUNT(*) FROM spliceai_practical").fetchone()[0]

print(f"\n✅ PRACTICAL TABLE CREATED")
print(f"   Rows: {new_count:,}")
print(f"   Time: {creation_time:.1f}s")
print(f"   Target: {new_count/1_000_000:.0f}M rows (closer to 100M goal)")

# Check BRCA2 coverage improvement
brca2_practical = conn.execute("SELECT COUNT(*) FROM spliceai_practical WHERE gene_symbol = 'BRCA2'").fetchone()[0]
brca2_original = conn.execute("SELECT COUNT(*) FROM spliceai_scores_production WHERE gene_symbol = 'BRCA2'").fetchone()[0]

print(f"\nBRCA2 Coverage Improvement:")
print(f"   Original: {brca2_original:,}")
print(f"   Practical: {brca2_practical:,}")
print(f"   Coverage: {(brca2_practical/brca2_original)*100:.1f}% (vs 0.3% before)")

# Create indexes
print(f"\nCreating indexes on practical table...")
conn.execute("CREATE INDEX idx_splice_practical_gene ON spliceai_practical(gene_symbol)")
conn.execute("CREATE INDEX idx_splice_practical_variant ON spliceai_practical(variant_id)")

# Test performance
test_start = time.time()
brca2_test = conn.execute("SELECT COUNT(*) FROM spliceai_practical WHERE gene_symbol = 'BRCA2'").fetchone()[0]
test_time = time.time() - test_start

print(f"🧪 Performance: BRCA2 lookup in {test_time:.3f}s ({brca2_test:,} variants)")

conn.close()

print(f"\n🎯 RESULT: {new_count/1_000_000:.0f}M row practical table with much better gene coverage")
