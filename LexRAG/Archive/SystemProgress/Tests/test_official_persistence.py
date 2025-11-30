"""
Test ClickHouse Official Persistence Setup
Verify data persists using official Docker documentation approach
"""

import clickhouse_connect
import time
import subprocess

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def test_official_persistence():
    """Test persistence using official ClickHouse Docker approach"""
    log("TESTING OFFICIAL CLICKHOUSE PERSISTENCE")
    log("="*60)
    log("Following: https://clickhouse.com/docs/install/docker")
    
    try:
        # Connect to ClickHouse
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        log("SUCCESS: ClickHouse connected")
        
        # Create test database and data
        log("Creating test data...")
        client.command("CREATE DATABASE IF NOT EXISTS genomics_test")
        client.command("DROP TABLE IF EXISTS genomics_test.persistence_check")
        
        client.command("""
            CREATE TABLE genomics_test.persistence_check (
                id UInt32,
                gene_name String,
                variant_count UInt32,
                created_time DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY id
        """)
        
        # Insert test genomics data
        test_data = [
            (1, 'BRCA1', 14731),
            (2, 'BRCA2', 19886), 
            (3, 'TP53', 3678),
            (4, 'CFTR', 5603),
            (5, 'APOE', 240)
        ]
        
        client.insert('genomics_test.persistence_check', test_data)
        
        # Verify insertion
        count = client.query("SELECT COUNT(*) FROM genomics_test.persistence_check").result_rows[0][0]
        log(f"SUCCESS: {count} test records inserted")
        
        # Show data
        records = client.query("SELECT gene_name, variant_count FROM genomics_test.persistence_check ORDER BY id").result_rows
        log("Test data:")
        for gene, variants in records:
            log(f"   {gene}: {variants:,} variants")
        
        # Now test persistence by restarting container
        log("\nTESTING PERSISTENCE: Restarting container...")
        
        # Restart the container
        result = subprocess.run("docker restart clickhouse-genomics", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log("SUCCESS: Container restarted")
        else:
            log(f"ERROR: Container restart failed - {result.stderr}")
            return False
        
        # Wait for restart
        log("Waiting for ClickHouse to restart...")
        time.sleep(20)
        
        # Reconnect
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        log("SUCCESS: Reconnected after restart")
        
        # Check if data survived
        log("Checking if data survived restart...")
        
        try:
            databases = client.query("SHOW DATABASES").result_rows
            db_names = [db[0] for db in databases]
            log(f"Databases after restart: {db_names}")
            
            if 'genomics_test' in db_names:
                survived_count = client.query("SELECT COUNT(*) FROM genomics_test.persistence_check").result_rows[0][0]
                log(f"Data after restart: {survived_count} records")
                
                if survived_count == 5:
                    log("EXCELLENT: All data survived restart!")
                    
                    # Verify data integrity
                    survived_records = client.query("SELECT gene_name, variant_count FROM genomics_test.persistence_check ORDER BY id").result_rows
                    log("Survived data:")
                    for gene, variants in survived_records:
                        log(f"   {gene}: {variants:,} variants")
                    
                    log("SUCCESS: Official persistence setup working perfectly!")
                    return True
                else:
                    log(f"PARTIAL: Only {survived_count}/5 records survived")
                    return False
            else:
                log("FAILED: Database lost after restart")
                return False
                
        except Exception as e:
            log(f"ERROR checking data after restart: {e}")
            return False
        
    except Exception as e:
        log(f"ERROR: Persistence test failed - {e}")
        return False

def main():
    log("="*80)
    log("OFFICIAL CLICKHOUSE PERSISTENCE TEST")
    log("="*80)
    log("Using official Docker documentation approach")
    log("Goal: Verify data survives container restarts")
    
    success = test_official_persistence()
    
    log(f"\n{'='*80}")
    log("OFFICIAL PERSISTENCE TEST COMPLETE")
    log('='*80)
    
    if success:
        log("✅ PERSISTENCE WORKING: Data survives restarts")
        log("✅ Ready for production data migration")
        log("✅ No more data loss concerns")
        log("🎯 NEXT: Migrate ClinVar data safely")
    else:
        log("❌ PERSISTENCE STILL FAILING")
        log("❌ ClickHouse not viable for production")
        log("🔄 FALLBACK: Return to enhanced DuckDB system")

if __name__ == "__main__":
    main()

