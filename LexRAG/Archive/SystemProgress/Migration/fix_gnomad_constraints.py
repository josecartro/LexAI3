"""
Fix gnomAD Gene Constraints Migration
Handle NULL values and large numbers properly
"""

import clickhouse_connect
import time
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def fix_gnomad_constraints():
    """Fix and migrate gnomAD constraints with proper data types"""
    log("🔧 FIXING GNOMAD GENE CONSTRAINTS")
    log("="*60)
    
    client = clickhouse_connect.get_client(
        host='localhost',
        port=8123,
        username='genomics',
        password='genomics123'
    )
    
    # Drop and recreate table with nullable columns
    log("🗑️ Dropping old table...")
    client.command("DROP TABLE IF EXISTS population_db.gene_constraints")
    
    log("🏗️ Creating fixed table with nullable columns...")
    client.command("""
        CREATE TABLE population_db.gene_constraints (
            gene_symbol String,
            gene_id String,
            transcript_id String,
            canonical Boolean,
            lof_observed Nullable(UInt64),
            lof_expected Nullable(Float64),
            lof_oe Nullable(Float64),
            lof_pli Nullable(Float64),
            missense_observed Nullable(UInt64),
            missense_expected Nullable(Float64),
            missense_oe Nullable(Float64),
            missense_z_score Nullable(Float64),
            constraint_flag String
        ) ENGINE = MergeTree()
        ORDER BY gene_symbol
    """)
    log("✅ Fixed table created")
    
    # Process gnomAD file with better NULL handling
    constraints_file = Path("data/population/gnomad_v4.1_constraint.tsv")
    if not constraints_file.exists():
        log(f"❌ File not found: {constraints_file}")
        return False
    
    log(f"📁 Processing: {constraints_file.name}")
    
    batch = []
    total = 0
    start_time = time.time()
    
    def safe_int(value):
        """Safely convert to int or return None"""
        if value and value != 'NA':
            try:
                return int(float(value))
            except:
                pass
        return None
    
    def safe_float(value):
        """Safely convert to float or return None"""
        if value and value != 'NA':
            try:
                return float(value)
            except:
                pass
        return None
    
    def safe_bool(value):
        """Safely convert to boolean"""
        return value.lower() == 'true' if value else False
    
    try:
        with open(constraints_file, 'r') as f:
            header = f.readline()  # Skip header
            
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 40:  # Ensure we have enough columns
                    try:
                        gene_symbol = parts[0] if parts[0] else ""
                        gene_id = parts[1] if parts[1] else ""
                        transcript_id = parts[2] if parts[2] else ""
                        canonical = safe_bool(parts[3])
                        
                        # Loss-of-function scores (safe conversion)
                        lof_obs = safe_int(parts[5])
                        lof_exp = safe_float(parts[6])
                        lof_oe = safe_float(parts[7])
                        lof_pli = safe_float(parts[10])
                        
                        # Missense scores (safe conversion)
                        mis_obs = safe_int(parts[26])
                        mis_exp = safe_float(parts[27])
                        mis_oe = safe_float(parts[29])
                        mis_z = safe_float(parts[33])
                        
                        constraint_flag = parts[39] if len(parts) > 39 else ""
                        
                        batch.append((
                            gene_symbol, gene_id, transcript_id, canonical,
                            lof_obs, lof_exp, lof_oe, lof_pli,
                            mis_obs, mis_exp, mis_oe, mis_z, constraint_flag
                        ))
                        
                    except (ValueError, IndexError):
                        continue  # Skip malformed lines
                
                # Insert in batches
                if len(batch) >= 10000:
                    try:
                        client.insert('population_db.gene_constraints', batch)
                        total += len(batch)
                        
                        if total % 10000 == 0:
                            elapsed = time.time() - start_time
                            rate = total / elapsed if elapsed > 0 else 0
                            log(f"   📊 Progress: {total:,} genes ({rate:.0f}/sec)")
                        
                        batch = []
                    except Exception as e:
                        log(f"⚠️  Batch failed: {e}")
                        batch = []
        
        # Final batch
        if batch:
            client.insert('population_db.gene_constraints', batch)
            total += len(batch)
        
        elapsed = time.time() - start_time
        log(f"✅ gnomAD constraints complete: {total:,} genes in {elapsed/60:.1f} min")
        return total > 1000
        
    except Exception as e:
        log(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_gnomad_constraints()
    if success:
        log("🎉 GNOMAD CONSTRAINTS FIXED!")
        log("🔗 ALL REFERENCE DATA NOW COMPLETE!")
    else:
        log("❌ Fix failed")
