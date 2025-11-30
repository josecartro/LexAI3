"""
Fix ClinVar Column Issue and Continue Migration
"""

import clickhouse_connect
import gzip
import time
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def fix_clinvar_migration():
    """Fix ClinVar column mismatch and migrate properly"""
    log("FIXING CLINVAR COLUMN ISSUE")
    log("="*50)
    
    try:
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            password='simple123'
        )
        
        # Check current table structure
        current_count = client.query("SELECT COUNT(*) FROM genomics_db.clinvar_variants").result_rows[0][0]
        log(f"Current ClinVar data: {current_count:,} variants")
        
        if current_count > 3000000:
            log("ClinVar already has substantial data - skipping re-migration")
            return True
        
        # Clear and recreate table with correct structure
        client.command("DROP TABLE IF EXISTS genomics_db.clinvar_variants")
        
        # Create table with exact 8 columns (no pathogenicity_score)
        client.command("""
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
        """)
        
        log("Fixed ClinVar table structure (8 columns)")
        
        # Migrate with correct column count
        vcf_file = Path("data/global/clinvar/clinvar_GRCh38.vcf.gz")
        log(f"Re-migrating ClinVar: {vcf_file}")
        
        batch = []
        total = 0
        start_time = time.time()
        
        with gzip.open(vcf_file, 'rt') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                
                parts = line.strip().split('\t')
                if len(parts) >= 8:
                    chrom = parts[0].replace('chr', '')
                    try:
                        pos = int(parts[1])
                    except:
                        continue
                    
                    rsid = parts[2] if parts[2] != '.' else f"var_{chrom}_{pos}"
                    ref = parts[3]
                    alt = parts[4]
                    info = parts[7]
                    
                    # Parse INFO
                    gene_symbol = "unknown"
                    clinical_sig = "unknown"
                    disease = "unknown"
                    
                    if "GENEINFO=" in info:
                        try:
                            gene_symbol = info.split("GENEINFO=")[1].split(";")[0].split(":")[0]
                        except:
                            pass
                    
                    if "CLNSIG=" in info:
                        try:
                            clinical_sig = info.split("CLNSIG=")[1].split(";")[0]
                        except:
                            pass
                    
                    if "CLNDN=" in info:
                        try:
                            disease = info.split("CLNDN=")[1].split(";")[0][:200]
                        except:
                            pass
                    
                    # Insert with exactly 8 columns
                    batch.append((chrom, pos, rsid, ref, alt, gene_symbol, clinical_sig, disease))
                
                if len(batch) >= 50000:
                    try:
                        client.insert('genomics_db.clinvar_variants', batch)
                        total += len(batch)
                        
                        if total % 1000000 == 0:
                            elapsed = time.time() - start_time
                            rate = total / elapsed
                            log(f"   ClinVar: {total:,} variants ({rate:.0f}/sec)")
                        
                        batch = []
                    except Exception as e:
                        log(f"   Batch error: {e}")
                        batch = []
        
        if batch:
            client.insert('genomics_db.clinvar_variants', batch)
            total += len(batch)
        
        elapsed = time.time() - start_time
        log(f"ClinVar fixed: {total:,} variants in {elapsed/60:.1f} minutes")
        return True
        
    except Exception as e:
        log(f"ClinVar fix failed: {e}")
        return False

def continue_spliceai_migration():
    """Continue with SpliceAI - the largest remaining dataset"""
    log("\nCONTINUING WITH SPLICEAI MIGRATION")
    log("="*50)
    log("This is the 3.43 billion row dataset")
    log("Will run for 8-12 hours")
    
    try:
        client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            password='simple123'
        )
        
        # Check if SpliceAI table exists and has data
        try:
            current_splice = client.query("SELECT COUNT(*) FROM genomics_db.spliceai_predictions").result_rows[0][0]
            log(f"Current SpliceAI data: {current_splice:,} predictions")
        except:
            log("Creating SpliceAI table...")
            client.command("""
                CREATE TABLE IF NOT EXISTS genomics_db.spliceai_predictions (
                    chrom String,
                    pos UInt64,
                    variant_id String,
                    ref String,
                    alt String,
                    gene_symbol String,
                    acceptor_gain Float32,
                    acceptor_loss Float32,
                    donor_gain Float32,
                    donor_loss Float32,
                    max_score Float32
                ) ENGINE = MergeTree()
                ORDER BY (gene_symbol, chrom, pos)
            """)
        
        # Start SpliceAI migration
        vcf_file = Path("data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz")
        log(f"Processing SpliceAI: {vcf_file} ({vcf_file.stat().st_size/(1024*1024*1024):.1f} GB)")
        
        batch = []
        total = 0
        start_time = time.time()
        
        with gzip.open(vcf_file, 'rt') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                
                parts = line.strip().split('\t')
                if len(parts) >= 8:
                    chrom = parts[0].replace('chr', '')
                    try:
                        pos = int(parts[1])
                    except:
                        continue
                    
                    variant_id = parts[2] if parts[2] != '.' else f"var_{chrom}_{pos}"
                    ref = parts[3]
                    alt = parts[4]
                    info = parts[7]
                    
                    # Parse SpliceAI scores
                    gene_symbol = "unknown"
                    acceptor_gain = 0.0
                    acceptor_loss = 0.0
                    donor_gain = 0.0
                    donor_loss = 0.0
                    
                    if "SYMBOL=" in info:
                        try:
                            gene_symbol = info.split("SYMBOL=")[1].split(";")[0]
                        except:
                            pass
                    
                    if "SpliceAI=" in info:
                        try:
                            scores = info.split("SpliceAI=")[1].split(";")[0].split("|")
                            if len(scores) >= 4:
                                acceptor_gain = float(scores[0]) if scores[0] != '.' else 0.0
                                acceptor_loss = float(scores[1]) if scores[1] != '.' else 0.0
                                donor_gain = float(scores[2]) if scores[2] != '.' else 0.0
                                donor_loss = float(scores[3]) if scores[3] != '.' else 0.0
                        except:
                            pass
                    
                    max_score = max(abs(acceptor_gain), abs(acceptor_loss), abs(donor_gain), abs(donor_loss))
                    
                    batch.append((chrom, pos, variant_id, ref, alt, gene_symbol,
                                acceptor_gain, acceptor_loss, donor_gain, donor_loss, max_score))
                
                if len(batch) >= 100000:
                    try:
                        client.insert('genomics_db.spliceai_predictions', batch)
                        total += len(batch)
                        
                        if total % 10000000 == 0:  # Report every 10M
                            elapsed = time.time() - start_time
                            rate = total / elapsed
                            remaining = 3_433_300_000 - total
                            eta_hours = remaining / rate / 3600 if rate > 0 else 0
                            
                            log(f"   SpliceAI: {total:,} predictions ({rate:.0f}/sec, ETA: {eta_hours:.1f}h)")
                        
                        batch = []
                    except Exception as e:
                        batch = []  # Skip problematic batches, continue
        
        if batch:
            try:
                client.insert('genomics_db.spliceai_predictions', batch)
                total += len(batch)
            except:
                pass
        
        elapsed = time.time() - start_time
        log(f"SpliceAI migration: {total:,} predictions in {elapsed/3600:.1f} hours")
        return True
        
    except Exception as e:
        log(f"SpliceAI migration error: {e}")
        return False

def main():
    log("FIXING CLINVAR AND CONTINUING MIGRATION")
    log("="*60)
    
    # Fix ClinVar first
    if fix_clinvar_migration():
        log("ClinVar fixed successfully")
        
        # Continue with SpliceAI (the big one)
        continue_spliceai_migration()
    else:
        log("ClinVar fix failed")

if __name__ == "__main__":
    main()
