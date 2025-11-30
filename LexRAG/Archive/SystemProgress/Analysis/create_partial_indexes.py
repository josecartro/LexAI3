"""
Create Partial Indexes on Massive Tables
Smart indexing by chromosome and gene subsets
"""

import duckdb
import time
import psutil
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def monitor_system():
    """Monitor system resources"""
    memory = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent(interval=1)
    log(f"📊 System: Memory {memory:.1f}%, CPU {cpu:.1f}%")
    return memory < 75

def create_chromosome_indexes():
    """Create partial indexes by chromosome for SpliceAI"""
    log("🧬 CREATING CHROMOSOME-BASED INDEXES FOR SPLICEAI")
    log("="*60)
    
    try:
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=False)
        
        # Optimize DuckDB for indexing
        conn.execute("SET memory_limit='12GB'")
        conn.execute("SET threads=1")
        conn.execute("SET preserve_insertion_order=false")
        log("✅ DuckDB optimized for indexing")
        
        # Create indexes for major chromosomes (1-22, X, Y)
        chromosomes = [str(i) for i in range(1, 23)] + ['X', 'Y']
        successful_indexes = 0
        
        for i, chrom in enumerate(chromosomes, 1):
            if not monitor_system():
                log(f"🛑 System stressed - stopping for safety")
                break
                
            log(f"\n📍 Chromosome {chrom} ({i}/{len(chromosomes)}):")
            
            try:
                # Check chromosome data size first
                count = conn.execute(f"SELECT COUNT(*) FROM spliceai_scores_production WHERE chrom='{chrom}'").fetchone()[0]
                log(f"   Rows in chr{chrom}: {count:,}")
                
                if count > 500_000_000:  # >500M rows might be too big
                    log(f"   ⚠️  Large chromosome - skipping for safety")
                    continue
                
                # Create partial index
                index_name = f"idx_spliceai_chr{chrom}_variant"
                create_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON spliceai_scores_production(variant_id) WHERE chrom='{chrom}'"
                
                log(f"   🔨 Creating: {index_name}")
                start_time = time.time()
                
                conn.execute(create_sql)
                
                index_time = time.time() - start_time
                log(f"   ✅ Created in {index_time:.1f} seconds")
                successful_indexes += 1
                
                # Recovery pause
                time.sleep(2)
                
            except Exception as e:
                log(f"   ❌ Chr{chrom} index failed: {e}")
                if "memory" in str(e).lower():
                    log(f"   🛑 Memory issue - stopping chromosome indexing")
                    break
        
        conn.close()
        
        log(f"\n✅ CHROMOSOME INDEXING SUMMARY:")
        log(f"   Successful indexes: {successful_indexes}/{len(chromosomes)}")
        log(f"   Coverage: {successful_indexes/len(chromosomes)*100:.1f}% of chromosomes")
        
        return successful_indexes > 0
        
    except Exception as e:
        log(f"❌ Chromosome indexing error: {e}")
        return False

def create_gene_based_indexes():
    """Create partial indexes by gene for frequently queried genes"""
    log(f"\n🧬 CREATING GENE-BASED INDEXES")
    log("="*60)
    
    try:
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=False)
        
        # Index frequently queried genes
        important_genes = ['BRCA1', 'BRCA2', 'TP53', 'CFTR', 'APOE', 'EGFR', 'KRAS']
        successful_gene_indexes = 0
        
        for gene in important_genes:
            if not monitor_system():
                break
                
            log(f"\n🧬 Gene: {gene}")
            
            try:
                # Check gene data size
                count = conn.execute(f"SELECT COUNT(*) FROM spliceai_scores_production WHERE gene_symbol='{gene}'").fetchone()[0]
                log(f"   Rows for {gene}: {count:,}")
                
                if count > 0 and count < 10_000_000:  # Reasonable size
                    index_name = f"idx_spliceai_{gene.lower()}"
                    create_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON spliceai_scores_production(variant_id) WHERE gene_symbol='{gene}'"
                    
                    log(f"   🔨 Creating: {index_name}")
                    start_time = time.time()
                    
                    conn.execute(create_sql)
                    
                    index_time = time.time() - start_time
                    log(f"   ✅ Created in {index_time:.1f} seconds")
                    successful_gene_indexes += 1
                else:
                    log(f"   ⚠️  No data or too large - skipping")
                
                time.sleep(1)  # Small pause
                
            except Exception as e:
                log(f"   ❌ {gene} index failed: {e}")
        
        conn.close()
        
        log(f"\n✅ GENE INDEXING SUMMARY:")
        log(f"   Successful gene indexes: {successful_gene_indexes}/{len(important_genes)}")
        
        return successful_gene_indexes > 0
        
    except Exception as e:
        log(f"❌ Gene indexing error: {e}")
        return False

def main():
    log("="*80)
    log("PARTIAL INDEXING SOLUTION")
    log("="*80)
    log("Goal: Create smart partial indexes for massive data access")
    
    # Initial system check
    if not monitor_system():
        log("🛑 System not ready")
        return
    
    # Try chromosome-based indexing
    chrom_success = create_chromosome_indexes()
    
    # Try gene-based indexing for important genes
    gene_success = create_gene_indexes()
    
    log(f"\n{'='*80}")
    log("PARTIAL INDEXING COMPLETE")
    log('='*80)
    
    if chrom_success or gene_success:
        log("✅ PARTIAL INDEXING SUCCESS")
        log("Massive data now accessible with smart queries")
        log("🎯 Ready to restart APIs with optimized massive data access")
    else:
        log("❌ PARTIAL INDEXING FAILED")
        log("Need alternative approach for massive data")
    
    # Final system check
    monitor_system()

if __name__ == "__main__":
    main()
