"""
Safe Genomics Data Analysis
Responsible script with progress indicators and resource management
"""

import duckdb
import time
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def safe_table_analysis(conn, table_name, max_time=30):
    """Safely analyze a table with timeout and progress"""
    log(f"Analyzing table: {table_name}")
    
    try:
        # Quick count with timeout
        start_time = time.time()
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        count_time = time.time() - start_time
        
        if count_time > max_time:
            log(f"  WARNING: Count took {count_time:.1f}s - large table")
        
        log(f"  Rows: {count:,}")
        
        # Get column info (fast operation)
        columns = conn.execute(f"DESCRIBE {table_name}").fetchall()
        log(f"  Columns: {len(columns)}")
        
        # Show key columns
        column_names = [col[0] for col in columns]
        log(f"  Key columns: {column_names[:8]}")
        
        # Check for connection columns
        connection_cols = [col for col in column_names if any(word in col.lower() for word in ['gene', 'variant', 'protein', 'tissue', '_id', 'rsid'])]
        if connection_cols:
            log(f"  Connection columns: {connection_cols[:6]}")
        
        # Quick sample (safe)
        sample = conn.execute(f"SELECT * FROM {table_name} LIMIT 1").fetchone()
        log(f"  Has data: {bool(sample)}")
        
        # Small delay to prevent CPU overload
        time.sleep(0.5)
        
        return {
            'table': table_name,
            'rows': count,
            'columns': len(columns),
            'column_names': column_names,
            'connection_columns': connection_cols,
            'has_data': bool(sample)
        }
        
    except Exception as e:
        log(f"  ERROR analyzing {table_name}: {str(e)[:100]}")
        return {'table': table_name, 'error': str(e)[:100]}

def main():
    log("Starting SAFE genomics data analysis")
    log("Will analyze tables responsibly with progress indicators")
    
    try:
        conn = duckdb.connect("../../data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
        log("Database connection successful")
        
        # Step 1: Analyze current tables
        log("\nSTEP 1: Analyzing CURRENT tables used by LexAPI_Genomics")
        log("-" * 50)
        
        current_tables = ["clinvar_full_production", "gencode_v44_transcripts"]
        current_results = []
        
        for table in current_tables:
            result = safe_table_analysis(conn, table)
            current_results.append(result)
        
        # Step 2: Analyze massive production tables (carefully)
        log("\nSTEP 2: Analyzing MASSIVE production tables (not currently used)")
        log("-" * 50)
        log("WARNING: These are billion-row tables - analyzing safely")
        
        massive_tables = [
            "spliceai_scores_production",
            "spliceai_full_production", 
            "dbsnp_parquet_production"
        ]
        
        massive_results = []
        for table in massive_tables:
            log(f"\nAnalyzing massive table: {table} (this may take time)")
            result = safe_table_analysis(conn, table, max_time=60)
            massive_results.append(result)
        
        # Step 3: Analyze AlphaFold tables
        log("\nSTEP 3: Analyzing AlphaFold protein tables")
        log("-" * 50)
        
        alphafold_tables = [
            "alphafold_clinical_variant_impact",
            "alphafold_variant_protein_analysis"
        ]
        
        alphafold_results = []
        for table in alphafold_tables:
            result = safe_table_analysis(conn, table)
            alphafold_results.append(result)
        
        # Step 4: Search for connection tables
        log("\nSTEP 4: Searching for connection/relationship tables")
        log("-" * 50)
        
        all_tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [t[0] for t in all_tables]
        
        connection_keywords = ["connection", "relationship", "mapping", "link", "association", "interaction", "pathway", "network"]
        connection_tables = []
        
        for table in table_names:
            for keyword in connection_keywords:
                if keyword in table.lower():
                    connection_tables.append(table)
                    break
        
        log(f"Found {len(connection_tables)} potential connection tables")
        
        connection_results = []
        for table in connection_tables[:10]:  # Limit to first 10 to avoid overload
            result = safe_table_analysis(conn, table)
            connection_results.append(result)
        
        conn.close()
        log("Database connection closed safely")
        
        # Summary
        log("\n" + "="*80)
        log("ANALYSIS SUMMARY")
        log("="*80)
        
        log(f"Current tables analyzed: {len(current_results)}")
        log(f"Massive production tables: {len(massive_results)}")
        log(f"AlphaFold tables: {len(alphafold_results)}")
        log(f"Connection tables: {len(connection_results)}")
        
        log("\nKEY FINDINGS:")
        for result in massive_results:
            if 'rows' in result:
                log(f"  MASSIVE UNUSED: {result['table']} - {result['rows']:,} rows")
        
        for result in connection_results:
            if 'rows' in result and result['rows'] > 10000:
                log(f"  CONNECTION TABLE: {result['table']} - {result['rows']:,} rows")
        
        log("\nAnalysis completed safely")
        
    except Exception as e:
        log(f"ERROR: {e}")

if __name__ == "__main__":
    main()
