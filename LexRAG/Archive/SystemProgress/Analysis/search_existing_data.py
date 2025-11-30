"""
Search Existing Databases for SpliceAI, gnomAD, AlphaFold
Check if we already have processed data in DuckDB and Qdrant
"""

import duckdb
from pathlib import Path
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def search_duckdb_databases():
    """Search all DuckDB databases for SpliceAI, gnomAD, AlphaFold data"""
    log("SEARCHING DUCKDB DATABASES")
    log("="*60)
    
    # All available DuckDB files
    db_files = [
        "data/databases/genomic_knowledge/genomic_knowledge.duckdb",
        "data/databases/genomic_knowledge/multi_omics.duckdb", 
        "data/databases/genomic_knowledge/digital_twin.duckdb",
        "data/databases/genomic_knowledge/user_profiles_enhanced.duckdb",
        "data/databases/genomic_knowledge/etl_metadata.duckdb",
        "data/databases/population_risk/population_risk.duckdb"
    ]
    
    search_terms = ["spliceai", "gnomad", "alphafold", "splice", "population", "structure"]
    
    for db_file in db_files:
        db_path = Path(db_file)
        if not db_path.exists():
            log(f"❌ Database not found: {db_file}")
            continue
            
        log(f"\n📂 Searching: {db_path.name}")
        
        try:
            conn = duckdb.connect(str(db_path), read_only=True)
            
            # Get all tables
            tables = conn.execute("SHOW TABLES").fetchall()
            table_names = [t[0] for t in tables]
            
            # Search for relevant tables
            found_tables = []
            for table in table_names:
                for term in search_terms:
                    if term.lower() in table.lower():
                        found_tables.append(table)
                        break
            
            if found_tables:
                log(f"   ✅ Found {len(found_tables)} relevant tables:")
                for table in found_tables:
                    try:
                        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                        log(f"     {table}: {count:,} rows")
                        
                        # Show sample columns for context
                        columns = conn.execute(f"DESCRIBE {table}").fetchall()
                        key_columns = [col[0] for col in columns[:5]]
                        log(f"       Columns: {key_columns}")
                        
                    except Exception as e:
                        log(f"     {table}: ERROR - {str(e)[:50]}")
            else:
                log(f"   ❌ No relevant tables found")
                
            conn.close()
            
        except Exception as e:
            log(f"   ❌ Error accessing {db_file}: {e}")

def search_qdrant_collections():
    """Search Qdrant for relevant collections"""
    log(f"\n📂 SEARCHING QDRANT COLLECTIONS")
    log("="*60)
    
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url="http://localhost:6333")
        
        collections = client.get_collections()
        log(f"Total collections: {len(collections.collections)}")
        
        search_terms = ["spliceai", "gnomad", "alphafold", "splice", "population", "structure", "protein"]
        
        found_collections = []
        for collection in collections.collections:
            collection_name = collection.name.lower()
            for term in search_terms:
                if term in collection_name:
                    found_collections.append(collection.name)
                    break
        
        if found_collections:
            log(f"✅ Found {len(found_collections)} relevant collections:")
            for collection_name in found_collections:
                try:
                    info = client.get_collection(collection_name)
                    log(f"   {collection_name}: {info.points_count} points")
                except:
                    log(f"   {collection_name}: Info not available")
        else:
            log(f"❌ No relevant collections found")
            
        # List all collections for reference
        log(f"\nAll collections:")
        for collection in collections.collections:
            log(f"   {collection.name}")
            
    except Exception as e:
        log(f"❌ Error accessing Qdrant: {e}")

def check_production_tables_specifically():
    """Check specifically for production tables with massive data"""
    log(f"\n📂 CHECKING PRODUCTION TABLES SPECIFICALLY")
    log("="*60)
    
    try:
        conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
        
        # Check for specific massive tables we know exist
        massive_tables = [
            "spliceai_scores_production",
            "spliceai_full_production", 
            "alphafold_clinical_variant_impact",
            "alphafold_variant_protein_analysis",
            "dbsnp_parquet_production"
        ]
        
        log(f"Checking massive production tables:")
        for table in massive_tables:
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                columns = conn.execute(f"DESCRIBE {table}").fetchall()
                
                log(f"   ✅ {table}: {count:,} rows, {len(columns)} columns")
                
                # Sample data to verify it's real
                sample = conn.execute(f"SELECT * FROM {table} LIMIT 1").fetchone()
                log(f"       Has data: {bool(sample)}")
                
            except Exception as e:
                log(f"   ❌ {table}: {e}")
        
        conn.close()
        
    except Exception as e:
        log(f"❌ Error checking production tables: {e}")

def main():
    log("="*80)
    log("SEARCHING FOR EXISTING SPLICEAI, GNOMAD, ALPHAFOLD DATA")
    log("="*80)
    log("Goal: Find processed data we might already have")
    
    # Search DuckDB databases
    search_duckdb_databases()
    
    # Search Qdrant collections
    search_qdrant_collections()
    
    # Check production tables specifically
    check_production_tables_specifically()
    
    log(f"\n{'='*80}")
    log("SEARCH COMPLETE")
    log("Found existing processed data that we might not be using")
    log("="*80)

if __name__ == "__main__":
    main()
