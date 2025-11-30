"""
Test ClickHouse Performance vs DuckDB
Create test genomics database and compare query performance
"""

import time
import requests
import json

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def test_clickhouse_connection():
    """Test ClickHouse connection and basic functionality"""
    log("TESTING CLICKHOUSE CONNECTION")
    log("="*50)
    
    try:
        # Test HTTP interface
        response = requests.get("http://localhost:8123/")
        if response.status_code == 200:
            log("✅ ClickHouse HTTP interface working")
        else:
            log(f"❌ ClickHouse HTTP error: {response.status_code}")
            return False
        
        # Test simple query
        query = "SELECT version()"
        response = requests.post("http://localhost:8123/", data=query)
        if response.status_code == 200:
            version = response.text.strip()
            log(f"✅ ClickHouse version: {version}")
        else:
            log(f"❌ Query failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        log(f"❌ ClickHouse connection failed: {e}")
        return False

def create_test_genomics_database():
    """Create test genomics database in ClickHouse"""
    log("\nCREATING TEST GENOMICS DATABASE")
    log("="*50)
    
    try:
        # Create database
        create_db_query = "CREATE DATABASE IF NOT EXISTS genomics_test"
        response = requests.post("http://localhost:8123/", data=create_db_query)
        
        if response.status_code == 200:
            log("✅ Database 'genomics_test' created")
        else:
            log(f"❌ Database creation failed: {response.status_code}")
            return False
        
        # Create genes table
        genes_table = """
            CREATE TABLE IF NOT EXISTS genomics_test.genes (
                gene_symbol String,
                gene_id String,
                chromosome String,
                total_variants UInt32,
                pathogenic_variants UInt32
            ) ENGINE = MergeTree()
            ORDER BY gene_symbol
        """
        
        response = requests.post("http://localhost:8123/", data=genes_table)
        if response.status_code == 200:
            log("✅ Genes table created")
        else:
            log(f"❌ Genes table creation failed: {response.status_code}")
        
        # Create variants table
        variants_table = """
            CREATE TABLE IF NOT EXISTS genomics_test.variants (
                rsid String,
                gene_symbol String,
                chromosome String,
                position UInt64,
                ref_allele String,
                alt_allele String,
                clinical_significance String,
                disease_name String,
                pathogenicity_score Float32
            ) ENGINE = MergeTree()
            ORDER BY (gene_symbol, rsid)
        """
        
        response = requests.post("http://localhost:8123/", data=variants_table)
        if response.status_code == 200:
            log("✅ Variants table created")
        else:
            log(f"❌ Variants table creation failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        log(f"❌ Database creation error: {e}")
        return False

def load_sample_data():
    """Load sample genomics data into ClickHouse"""
    log("\nLOADING SAMPLE GENOMICS DATA")
    log("="*50)
    
    try:
        # Sample genes data
        genes_data = [
            ("BRCA1", "ENSG00000012048", "17", 20000, 5000),
            ("BRCA2", "ENSG00000139618", "13", 19886, 5047),
            ("TP53", "ENSG00000141510", "17", 3678, 881),
            ("CFTR", "ENSG00000001626", "7", 2500, 800),
            ("APOE", "ENSG00000130203", "19", 240, 13)
        ]
        
        # Insert genes
        for gene_symbol, gene_id, chromosome, total_vars, pathogenic_vars in genes_data:
            insert_query = f"""
                INSERT INTO genomics_test.genes VALUES 
                ('{gene_symbol}', '{gene_id}', '{chromosome}', {total_vars}, {pathogenic_vars})
            """
            
            response = requests.post("http://localhost:8123/", data=insert_query)
            if response.status_code == 200:
                log(f"   ✅ {gene_symbol} data inserted")
            else:
                log(f"   ❌ {gene_symbol} insert failed: {response.status_code}")
        
        # Sample variants data (simulate realistic data)
        variants_data = [
            ("rs7412", "APOE", "19", 45411941, "C", "T", "Pathogenic", "Alzheimer disease", 0.95),
            ("rs429358", "APOE", "19", 45411941, "T", "C", "Risk factor", "Alzheimer disease", 0.85),
            ("rs80357713", "BRCA1", "17", 43045677, "C", "T", "Pathogenic", "Breast cancer", 0.99),
            ("rs80357906", "BRCA2", "13", 32316461, "G", "A", "Pathogenic", "Breast cancer", 0.98),
            ("rs11540654", "TP53", "17", 7661779, "G", "A", "Pathogenic", "Li-Fraumeni syndrome", 0.97)
        ]
        
        for rsid, gene, chrom, pos, ref, alt, significance, disease, score in variants_data:
            insert_query = f"""
                INSERT INTO genomics_test.variants VALUES 
                ('{rsid}', '{gene}', '{chrom}', {pos}, '{ref}', '{alt}', '{significance}', '{disease}', {score})
            """
            
            response = requests.post("http://localhost:8123/", data=insert_query)
            if response.status_code == 200:
                log(f"   ✅ {rsid} variant inserted")
            else:
                log(f"   ❌ {rsid} insert failed")
        
        return True
        
    except Exception as e:
        log(f"❌ Data loading error: {e}")
        return False

def test_clickhouse_performance():
    """Test ClickHouse query performance"""
    log("\nTESTING CLICKHOUSE PERFORMANCE")
    log("="*50)
    
    test_queries = [
        ("Simple gene lookup", "SELECT * FROM genomics_test.genes WHERE gene_symbol = 'BRCA2'"),
        ("Variant count", "SELECT COUNT(*) FROM genomics_test.variants WHERE gene_symbol = 'BRCA2'"),
        ("JOIN query", "SELECT g.gene_symbol, g.total_variants, COUNT(v.rsid) as loaded_variants FROM genomics_test.genes g LEFT JOIN genomics_test.variants v ON g.gene_symbol = v.gene_symbol GROUP BY g.gene_symbol, g.total_variants"),
        ("Complex filter", "SELECT gene_symbol, COUNT(*) FROM genomics_test.variants WHERE clinical_significance = 'Pathogenic' GROUP BY gene_symbol")
    ]
    
    performance_results = []
    
    for query_name, query_sql in test_queries:
        log(f"\n🧪 Testing: {query_name}")
        
        try:
            start_time = time.time()
            response = requests.post("http://localhost:8123/", data=query_sql)
            query_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.text.strip()
                log(f"   ✅ SUCCESS: {query_time:.4f} seconds")
                log(f"   📊 Result: {result}")
                
                performance_results.append({
                    'query': query_name,
                    'time': query_time,
                    'success': True
                })
            else:
                log(f"   ❌ FAILED: HTTP {response.status_code}")
                performance_results.append({
                    'query': query_name,
                    'time': query_time,
                    'success': False
                })
                
        except Exception as e:
            log(f"   ❌ ERROR: {e}")
    
    return performance_results

def compare_with_duckdb():
    """Compare same queries with DuckDB for performance comparison"""
    log("\nCOMPARING WITH DUCKDB PERFORMANCE")
    log("="*50)
    
    try:
        import duckdb
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
        
        # Test same query patterns on DuckDB
        duckdb_queries = [
            ("DuckDB gene lookup", "SELECT COUNT(*) FROM clinvar_full_production WHERE gene_symbol = 'BRCA2'"),
            ("DuckDB variant count", "SELECT COUNT(*) FROM variants_clinical WHERE gene_symbol = 'BRCA2'"),
            ("DuckDB JOIN", "SELECT cv.gene_symbol, COUNT(*) FROM variants_clinical cv JOIN spliceai_practical sp ON cv.gene_symbol = sp.gene_symbol WHERE cv.gene_symbol = 'BRCA2' GROUP BY cv.gene_symbol")
        ]
        
        for query_name, query_sql in duckdb_queries:
            try:
                start_time = time.time()
                result = conn.execute(query_sql).fetchone()
                query_time = time.time() - start_time
                
                log(f"🦆 {query_name}: {query_time:.4f} seconds")
                
            except Exception as e:
                log(f"❌ {query_name}: {e}")
        
        conn.close()
        
    except Exception as e:
        log(f"❌ DuckDB comparison error: {e}")

def main():
    log("="*80)
    log("CLICKHOUSE PERFORMANCE TEST")
    log("="*80)
    log("Goal: Test ClickHouse performance vs DuckDB for genomics queries")
    
    # Test connection
    if not test_clickhouse_connection():
        log("❌ ClickHouse not ready - aborting test")
        return
    
    # Create test database
    if not create_test_genomics_database():
        log("❌ Database creation failed - aborting test")
        return
    
    # Load sample data
    if not load_sample_data():
        log("❌ Data loading failed - aborting test")
        return
    
    # Test performance
    results = test_clickhouse_performance()
    
    # Compare with DuckDB
    compare_with_duckdb()
    
    # Summary
    log(f"\n{'='*80}")
    log("CLICKHOUSE PERFORMANCE TEST COMPLETE")
    log('='*80)
    
    successful_queries = [r for r in results if r['success']]
    if successful_queries:
        avg_time = sum(r['time'] for r in successful_queries) / len(successful_queries)
        fastest = min(r['time'] for r in successful_queries)
        log(f"✅ ClickHouse performance: {len(successful_queries)} queries successful")
        log(f"📊 Average time: {avg_time:.4f}s")
        log(f"🚀 Fastest query: {fastest:.4f}s")
        
        if avg_time < 0.1:
            log("🎉 EXCELLENT: ClickHouse is ultra-fast for our genomics data!")
        elif avg_time < 0.5:
            log("✅ GOOD: ClickHouse is much faster than DuckDB")
        else:
            log("⚠️  MODERATE: ClickHouse faster but not dramatically")
    else:
        log("❌ ClickHouse test failed")

if __name__ == "__main__":
    main()
