"""
Simple gnomAD Constraints Migration
Store everything as strings to avoid data type issues
"""

import clickhouse_connect
import time
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def migrate_gnomad_simple():
    """Migrate gnomAD constraints with simple string storage"""
    log("🔧 SIMPLE GNOMAD CONSTRAINTS MIGRATION")
    log("="*60)
    
    client = clickhouse_connect.get_client(
        host='localhost',
        port=8123,
        username='genomics',
        password='genomics123'
    )
    
    # Create simple table with string columns
    log("🏗️ Creating simple constraints table...")
    client.command("DROP TABLE IF EXISTS population_db.gene_constraints")
    client.command("""
        CREATE TABLE population_db.gene_constraints (
            gene_symbol String,
            gene_id String,
            transcript_id String,
            canonical String,
            lof_observed String,
            lof_expected String,
            lof_oe String,
            lof_pli String,
            missense_observed String,
            missense_expected String,
            missense_oe String,
            missense_z_score String,
            constraint_flag String
        ) ENGINE = MergeTree()
        ORDER BY gene_symbol
    """)
    log("✅ Simple table created")
    
    constraints_file = Path("data/population/gnomad_v4.1_constraint.tsv")
    log(f"📁 Processing: {constraints_file.name}")
    
    batch = []
    total = 0
    start_time = time.time()
    
    try:
        with open(constraints_file, 'r') as f:
            header_line = f.readline().strip()
            headers = header_line.split('\t')
            
            log(f"📊 Found {len(headers)} columns")
            log(f"Key columns: {headers[:5]}")
            
            for line_num, line in enumerate(f, 1):
                parts = line.strip().split('\t')
                if len(parts) >= 13:  # Ensure minimum columns
                    try:
                        # Use exact column indices based on header
                        gene_symbol = parts[0] if len(parts) > 0 else ""
                        gene_id = parts[1] if len(parts) > 1 else ""
                        transcript_id = parts[2] if len(parts) > 2 else ""
                        canonical = parts[3] if len(parts) > 3 else ""
                        
                        # Store as strings to avoid conversion issues
                        lof_obs = parts[5] if len(parts) > 5 else "0"
                        lof_exp = parts[6] if len(parts) > 6 else "0"
                        lof_oe = parts[8] if len(parts) > 8 else "0"
                        lof_pli = parts[10] if len(parts) > 10 else "0"
                        
                        # Find missense columns (around index 26-33)
                        mis_obs = parts[26] if len(parts) > 26 else "0"
                        mis_exp = parts[27] if len(parts) > 27 else "0"
                        mis_oe = parts[29] if len(parts) > 29 else "0"
                        mis_z = parts[33] if len(parts) > 33 else "0"
                        
                        constraint_flag = parts[39] if len(parts) > 39 else ""
                        
                        batch.append((
                            gene_symbol, gene_id, transcript_id, canonical,
                            lof_obs, lof_exp, lof_oe, lof_pli,
                            mis_obs, mis_exp, mis_oe, mis_z, constraint_flag
                        ))
                        
                    except IndexError as e:
                        log(f"   Row {line_num}: Index error - {len(parts)} columns")
                        continue
                
                # Insert in small batches
                if len(batch) >= 1000:
                    try:
                        client.insert('population_db.gene_constraints', batch)
                        total += len(batch)
                        
                        if total % 5000 == 0:
                            elapsed = time.time() - start_time
                            rate = total / elapsed if elapsed > 0 else 0
                            log(f"   📊 Progress: {total:,} genes ({rate:.0f}/sec)")
                        
                        batch = []
                    except Exception as e:
                        log(f"⚠️  Batch failed at row {line_num}: {e}")
                        # Show problematic data
                        if batch:
                            log(f"   Sample data: {batch[0]}")
                        batch = []
                        break
        
        # Final batch
        if batch:
            try:
                client.insert('population_db.gene_constraints', batch)
                total += len(batch)
            except Exception as e:
                log(f"⚠️  Final batch failed: {e}")
        
        elapsed = time.time() - start_time
        log(f"✅ gnomAD constraints: {total:,} genes in {elapsed/60:.1f} min")
        return total > 1000
        
    except Exception as e:
        log(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_gnomad_simple()
    if success:
        log("🎉 GNOMAD CONSTRAINTS COMPLETE!")
    else:
        log("❌ Migration failed")
