"""
SpliceAI Data Partitioning Strategy
Split 3.43B row monster table into manageable pieces
"""

import duckdb
import time
import psutil
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def analyze_partitioning_options():
    """Analyze how to best partition the massive SpliceAI table"""
    log("="*80)
    log("SPLICEAI PARTITIONING ANALYSIS")
    log("="*80)
    
    try:
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
        
        # Check partitioning options
        log("📊 ANALYZING PARTITIONING OPTIONS:")
        
        # Option 1: By chromosome
        log("\n1. PARTITION BY CHROMOSOME:")
        chromosomes = conn.execute("SELECT DISTINCT chrom, COUNT(*) as row_count FROM spliceai_scores_production GROUP BY chrom ORDER BY row_count DESC LIMIT 10").fetchall()
        
        total_rows = sum(row[1] for row in chromosomes)
        log(f"   Total rows across chromosomes: {total_rows:,}")
        
        for chrom, count in chromosomes:
            percentage = (count / total_rows) * 100
            log(f"   chr{chrom}: {count:,} rows ({percentage:.1f}%)")
            
            # Assess if this size is manageable
            if count < 500_000_000:  # <500M rows
                log(f"      ✅ Manageable size for indexing")
            else:
                log(f"      ⚠️  Still large - might need further splitting")
        
        # Option 2: By gene symbol
        log("\n2. PARTITION BY GENE GROUPS:")
        gene_stats = conn.execute("""
            SELECT 
                CASE 
                    WHEN gene_symbol LIKE 'A%' THEN 'A-genes'
                    WHEN gene_symbol LIKE 'B%' THEN 'B-genes'
                    WHEN gene_symbol LIKE 'C%' THEN 'C-genes'
                    ELSE 'Other-genes'
                END as gene_group,
                COUNT(*) as row_count
            FROM spliceai_scores_production 
            WHERE gene_symbol IS NOT NULL
            GROUP BY gene_group
            ORDER BY row_count DESC
        """).fetchall()
        
        for gene_group, count in gene_stats:
            log(f"   {gene_group}: {count:,} rows")
            
            if count < 1_000_000_000:  # <1B rows
                log(f"      ✅ Good partition size")
            else:
                log(f"      ⚠️  Still too large")
        
        # Option 3: By score significance
        log("\n3. PARTITION BY SCORE SIGNIFICANCE:")
        score_ranges = conn.execute("""
            SELECT 
                CASE 
                    WHEN (ABS(acceptor_gain_score) > 0.5 OR ABS(acceptor_loss_score) > 0.5 
                          OR ABS(donor_gain_score) > 0.5 OR ABS(donor_loss_score) > 0.5) THEN 'high_impact'
                    WHEN (ABS(acceptor_gain_score) > 0.2 OR ABS(acceptor_loss_score) > 0.2 
                          OR ABS(donor_gain_score) > 0.2 OR ABS(donor_loss_score) > 0.2) THEN 'medium_impact'
                    ELSE 'low_impact'
                END as impact_level,
                COUNT(*) as row_count
            FROM spliceai_scores_production
            GROUP BY impact_level
            ORDER BY row_count DESC
        """).fetchall()
        
        for impact_level, count in score_ranges:
            log(f"   {impact_level}: {count:,} rows")
            
            if impact_level == 'high_impact' and count < 100_000_000:
                log(f"      ✅ High impact data is manageable size!")
        
        conn.close()
        
    except Exception as e:
        log(f"❌ Analysis error: {e}")

def create_partitioned_tables():
    """Create smaller, manageable partitioned tables"""
    log(f"\n🔨 CREATING PARTITIONED TABLES")
    log("="*60)
    
    try:
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=False)
        
        # Apply memory optimizations
        conn.execute("SET memory_limit='10GB'")
        conn.execute("SET threads=1")
        conn.execute("SET preserve_insertion_order=false")
        
        # Strategy: Create high-impact splice table (most useful subset)
        log("\n📋 Creating high-impact SpliceAI table...")
        
        create_high_impact_sql = """
            CREATE TABLE IF NOT EXISTS spliceai_high_impact AS
            SELECT chrom, pos_bp, variant_id, ref, alt, gene_symbol,
                   acceptor_gain_score, acceptor_loss_score, 
                   donor_gain_score, donor_loss_score
            FROM spliceai_scores_production
            WHERE (ABS(acceptor_gain_score) > 0.5 OR ABS(acceptor_loss_score) > 0.5 
                   OR ABS(donor_gain_score) > 0.5 OR ABS(donor_loss_score) > 0.5)
            AND gene_symbol IS NOT NULL
        """
        
        log(f"🔨 SQL: Creating high-impact table...")
        log(f"   Only variants with splice scores >0.5 (clinically significant)")
        
        start_time = time.time()
        conn.execute(create_high_impact_sql)
        creation_time = time.time() - start_time
        
        # Check size of new table
        high_impact_count = conn.execute("SELECT COUNT(*) FROM spliceai_high_impact").fetchone()[0]
        
        log(f"✅ HIGH-IMPACT TABLE CREATED")
        log(f"   Original: 3.43B rows")
        log(f"   High-impact: {high_impact_count:,} rows")
        log(f"   Reduction: {((3_433_300_000 - high_impact_count) / 3_433_300_000) * 100:.1f}%")
        log(f"   Creation time: {creation_time:.1f}s")
        
        # Now index the manageable table
        if high_impact_count < 100_000_000:  # <100M rows should be indexable
            log(f"\n🔨 Creating indexes on manageable high-impact table...")
            
            # Gene symbol index
            conn.execute("CREATE INDEX IF NOT EXISTS idx_splice_high_gene ON spliceai_high_impact(gene_symbol)")
            log(f"   ✅ Gene symbol index created")
            
            # Variant ID index
            conn.execute("CREATE INDEX IF NOT EXISTS idx_splice_high_variant ON spliceai_high_impact(variant_id)")
            log(f"   ✅ Variant ID index created")
            
            # Test performance
            test_start = time.time()
            brca2_count = conn.execute("SELECT COUNT(*) FROM spliceai_high_impact WHERE gene_symbol = 'BRCA2'").fetchone()[0]
            test_time = time.time() - test_start
            
            log(f"🧪 Index test: BRCA2 lookup in {test_time:.3f}s ({brca2_count:,} high-impact variants)")
            
            conn.close()
            return True
        else:
            log(f"⚠️  High-impact table still too large: {high_impact_count:,} rows")
            conn.close()
            return False
        
    except Exception as e:
        log(f"❌ Partitioning error: {e}")
        return False

def main():
    log("="*80)
    log("SPLICEAI PARTITIONING SOLUTION")
    log("="*80)
    log("Goal: Split 3.43B row monster into manageable pieces")
    
    # Analyze partitioning options
    analyze_partitioning_options()
    
    # Create partitioned tables
    success = create_partitioned_tables()
    
    log(f"\n{'='*80}")
    log("PARTITIONING COMPLETE")
    log('='*80)
    
    if success:
        log("✅ PARTITIONING SUCCESS: Manageable SpliceAI tables created")
        log("🎯 High-impact splice data now accessible with indexes")
    else:
        log("❌ Partitioning needs alternative approach")

if __name__ == "__main__":
    main()
