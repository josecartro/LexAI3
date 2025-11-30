"""
Recreate ClinVar Data in Persistent ClickHouse
Test that data survives container restarts
"""

import clickhouse_connect
import gzip
import time

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def recreate_clinvar_data():
    """Recreate ClinVar data in persistent storage"""
    log("RECREATING CLINVAR IN PERSISTENT CLICKHOUSE")
    log("="*60)
    
    try:
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        
        # Create genomics database
        client.command("CREATE DATABASE IF NOT EXISTS genomics_db")
        log("SUCCESS: Genomics database created")
        
        # Create ClinVar table
        client.command("DROP TABLE IF EXISTS genomics_db.clinvar_variants")
        
        create_table = """
            CREATE TABLE genomics_db.clinvar_variants (
                chrom String,
                pos UInt64,
                rsid String,
                ref String,
                alt String,
                gene_symbol String,
                clinical_significance String,
                disease_name String
            ) ENGINE = MergeTree()
            ORDER BY (gene_symbol, rsid)
        """
        
        client.command(create_table)
        log("SUCCESS: ClinVar table created")
        
        # Insert sample ClinVar data (quick test)
        log("Inserting sample ClinVar data...")
        sample_data = [
            ('17', 43045677, 'rs80357713', 'C', 'T', 'BRCA1', 'Pathogenic', 'Breast cancer'),
            ('13', 32316461, 'rs80357906', 'G', 'A', 'BRCA2', 'Pathogenic', 'Breast cancer'),
            ('17', 7661779, 'rs11540654', 'G', 'A', 'TP53', 'Pathogenic', 'Li-Fraumeni syndrome'),
            ('19', 45411941, 'rs7412', 'C', 'T', 'APOE', 'Pathogenic', 'Alzheimer disease'),
            ('7', 117509035, 'rs113993960', 'G', 'A', 'CFTR', 'Pathogenic', 'Cystic fibrosis')
        ]
        
        client.insert('genomics_db.clinvar_variants', sample_data)
        
        # Verify insertion
        count = client.query("SELECT COUNT(*) FROM genomics_db.clinvar_variants").result_rows[0][0]
        log(f"SUCCESS: {count} variants inserted")
        
        # Test queries
        brca2 = client.query("SELECT * FROM genomics_db.clinvar_variants WHERE gene_symbol = 'BRCA2'").result_rows
        log(f"BRCA2 test: {len(brca2)} variants found")
        
        log("SUCCESS: ClinVar data created in persistent storage")
        return True
        
    except Exception as e:
        log(f"ERROR: ClinVar recreation failed - {e}")
        return False

def test_persistence_after_restart():
    """Test that data persists after container restart"""
    log("\nTESTING PERSISTENCE AFTER RESTART")
    log("="*60)
    
    try:
        log("Restarting ClickHouse container...")
        import subprocess
        
        # Restart container
        subprocess.run("docker restart clickhouse-genomics", shell=True, capture_output=True)
        
        # Wait for restart
        time.sleep(15)
        
        # Reconnect
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        
        # Check if data survived
        databases = client.query("SHOW DATABASES").result_rows
        log(f"Databases after restart: {[db[0] for db in databases]}")
        
        if 'genomics_db' in [db[0] for db in databases]:
            count = client.query("SELECT COUNT(*) FROM genomics_db.clinvar_variants").result_rows[0][0]
            log(f"ClinVar data after restart: {count} variants")
            
            if count > 0:
                log("EXCELLENT: Data persisted through restart!")
                return True
            else:
                log("FAILED: Data lost after restart")
                return False
        else:
            log("FAILED: Database lost after restart")
            return False
        
    except Exception as e:
        log(f"ERROR: Persistence test failed - {e}")
        return False

def main():
    log("="*80)
    log("CLICKHOUSE PERSISTENT STORAGE TEST")
    log("="*80)
    log("Goal: Ensure data survives container restarts")
    
    # Create data
    if recreate_clinvar_data():
        # Test persistence
        if test_persistence_after_restart():
            log(f"\n{'='*80}")
            log("PERSISTENCE TEST SUCCESS")
            log('='*80)
            log("✅ ClickHouse data survives restarts")
            log("✅ Ready for production data migration")
            log("✅ No more data loss issues")
        else:
            log(f"\n{'='*80}")
            log("PERSISTENCE TEST FAILED")
            log('='*80)
            log("❌ Data still being lost - need to fix storage")

if __name__ == "__main__":
    main()

