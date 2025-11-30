import duckdb
import time

print("RECREATING SPLICEAI TABLE TO KEEP ~100M ROWS")
print("="*50)

conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=False)

# Set optimizations
conn.execute("SET memory_limit='12GB'")
conn.execute("SET threads=2")

print("Step 1: Finding optimal threshold for ~100M rows...")

# Test threshold 0.2 (should give much more data)
test_count = conn.execute("""
    SELECT COUNT(*) FROM spliceai_scores_production
    WHERE (ABS(acceptor_gain_score) > 0.2 OR ABS(acceptor_loss_score) > 0.2 
           OR ABS(donor_gain_score) > 0.2 OR ABS(donor_loss_score) > 0.2)
""").fetchone()[0]

print(f"Threshold 0.2 would give: {test_count:,} rows")

if 80_000_000 <= test_count <= 150_000_000:
    threshold = 0.2
    print(f"✅ Using threshold 0.2 for ~{test_count/1_000_000:.0f}M rows")
else:
    print(f"⚠️  0.2 gives {test_count/1_000_000:.0f}M rows - adjusting...")
    threshold = 0.15 if test_count < 80_000_000 else 0.25

print(f"\nStep 2: Dropping old table and creating new one...")

# Drop old table
conn.execute("DROP TABLE IF EXISTS spliceai_high_impact")

# Create new table with better threshold
create_sql = f"""
    CREATE TABLE spliceai_high_impact AS
    SELECT chrom, pos_bp, variant_id, ref, alt, gene_symbol,
           acceptor_gain_score, acceptor_loss_score,
           donor_gain_score, donor_loss_score,
           variant_type
    FROM spliceai_scores_production
    WHERE gene_symbol IS NOT NULL
    AND (ABS(acceptor_gain_score) > {threshold} OR ABS(acceptor_loss_score) > {threshold}
         OR ABS(donor_gain_score) > {threshold} OR ABS(donor_loss_score) > {threshold})
"""

print(f"Creating table with threshold >{threshold}...")
start_time = time.time()

conn.execute(create_sql)

creation_time = time.time() - start_time
new_count = conn.execute("SELECT COUNT(*) FROM spliceai_high_impact").fetchone()[0]

print(f"✅ NEW TABLE CREATED")
print(f"   Rows: {new_count:,}")
print(f"   Time: {creation_time:.1f}s")
print(f"   Percentage of original: {(new_count/3_433_300_000)*100:.1f}%")

# Test BRCA2 coverage
brca2_new = conn.execute("SELECT COUNT(*) FROM spliceai_high_impact WHERE gene_symbol = 'BRCA2'").fetchone()[0]
brca2_original = conn.execute("SELECT COUNT(*) FROM spliceai_scores_production WHERE gene_symbol = 'BRCA2'").fetchone()[0]

print(f"\nBRCA2 Coverage Check:")
print(f"   Original: {brca2_original:,}")
print(f"   Kept: {brca2_new:,}")
print(f"   Coverage: {(brca2_new/brca2_original)*100:.1f}%")

# Create indexes on new table
print(f"\nStep 3: Creating indexes...")
conn.execute("CREATE INDEX idx_splice_100m_gene ON spliceai_high_impact(gene_symbol)")
conn.execute("CREATE INDEX idx_splice_100m_variant ON spliceai_high_impact(variant_id)")

print("✅ Indexes created")

# Test performance
test_start = time.time()
brca2_lookup = conn.execute("SELECT COUNT(*) FROM spliceai_high_impact WHERE gene_symbol = 'BRCA2'").fetchone()[0]
test_time = time.time() - test_start

print(f"🧪 Performance: BRCA2 lookup in {test_time:.3f}s ({brca2_lookup:,} variants)")

conn.close()
print(f"\n✅ OPTIMIZATION COMPLETE: ~{new_count/1_000_000:.0f}M usable rows")
