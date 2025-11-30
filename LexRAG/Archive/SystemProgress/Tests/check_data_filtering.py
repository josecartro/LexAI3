import duckdb

print("CHECKING WHAT DATA WE KEPT VS FILTERED OUT")
print("="*50)

conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)

print("\n1. SPLICE SCORE DISTRIBUTION:")
score_ranges = conn.execute("""
    SELECT 
        CASE 
            WHEN (ABS(acceptor_gain_score) > 0.8 OR ABS(donor_gain_score) > 0.8) THEN 'very_high'
            WHEN (ABS(acceptor_gain_score) > 0.5 OR ABS(donor_gain_score) > 0.5) THEN 'high'
            WHEN (ABS(acceptor_gain_score) > 0.2 OR ABS(donor_gain_score) > 0.2) THEN 'medium'
            WHEN (ABS(acceptor_gain_score) > 0.1 OR ABS(donor_gain_score) > 0.1) THEN 'low'
            ELSE 'very_low'
        END as score_range,
        COUNT(*) as count
    FROM spliceai_scores_production
    GROUP BY score_range
    ORDER BY count DESC
    LIMIT 10
""").fetchall()

total_original = sum(row[1] for row in score_ranges)
print(f"Total original: {total_original:,}")

for score_range, count in score_ranges:
    percentage = (count / total_original) * 100
    print(f"  {score_range}: {count:,} ({percentage:.1f}%)")

print("\n2. WHAT WE KEPT:")
high_impact_count = conn.execute("SELECT COUNT(*) FROM spliceai_high_impact").fetchone()[0]
print(f"High-impact (>0.5): {high_impact_count:,} rows")

print("\n3. BRCA2 COMPARISON:")
brca2_original = conn.execute("SELECT COUNT(*) FROM spliceai_scores_production WHERE gene_symbol = 'BRCA2'").fetchone()[0]
brca2_filtered = conn.execute("SELECT COUNT(*) FROM spliceai_high_impact WHERE gene_symbol = 'BRCA2'").fetchone()[0]

print(f"BRCA2 original: {brca2_original:,}")
print(f"BRCA2 filtered: {brca2_filtered:,}")
print(f"BRCA2 kept: {(brca2_filtered/brca2_original)*100:.1f}%")

conn.close()

print("\n4. ASSESSMENT:")
if high_impact_count < total_original * 0.05:  # Less than 5%
    print("❌ We filtered out >95% of data - might be too aggressive")
    print("💡 Consider lowering threshold to 0.2 or 0.3")
else:
    print("✅ Reasonable filtering - kept clinically relevant data")
