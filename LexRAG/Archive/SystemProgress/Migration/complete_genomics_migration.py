"""
Complete Genomics Data Migration to ClickHouse
Migrate ALL genomics data efficiently with optimized batching
"""

import clickhouse_connect
import gzip
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

class GenomicsMigrator:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            password='simple123'
        )
        self.batch_size = 50000  # Larger batches for efficiency
        self.report_interval = 1000000  # Report every 1M rows
        
    def setup_databases(self):
        """Create all required databases and tables"""
        log("SETTING UP GENOMICS DATABASES")
        log("="*60)
        
        # Create databases
        databases = ['genomics_db', 'expression_db', 'population_db', 'drugs_db']
        for db in databases:
            self.client.command(f"CREATE DATABASE IF NOT EXISTS {db}")
            log(f"✅ {db} database ready")
        
        # Create tables
        self.create_all_tables()
        log("✅ All tables created")
    
    def create_all_tables(self):
        """Create all genomics tables"""
        
        # ClinVar variants
        self.client.command("""
            CREATE TABLE IF NOT EXISTS genomics_db.clinvar_variants (
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
        
        # dbSNP common variants
        self.client.command("""
            CREATE TABLE IF NOT EXISTS genomics_db.dbsnp_variants (
                chrom String,
                pos UInt64,
                rsid String,
                ref String,
                alt String,
                allele_frequency Float32,
                variant_class String
            ) ENGINE = MergeTree()
            ORDER BY (rsid, chrom)
        """)
        
        # SpliceAI predictions
        self.client.command("""
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
        
        # GTEx expression
        self.client.command("""
            CREATE TABLE IF NOT EXISTS expression_db.gtex_expression (
                variant_id String,
                gene_id String,
                gene_symbol String,
                tissue_type String,
                slope Float32,
                pvalue Float64
            ) ENGINE = MergeTree()
            ORDER BY (gene_symbol, tissue_type)
        """)
        
        # AlphaFold proteins
        self.client.command("""
            CREATE TABLE IF NOT EXISTS genomics_db.alphafold_proteins (
                gene_symbol String,
                uniprot_id String,
                protein_name String,
                confidence_avg Float32,
                structure_length UInt32
            ) ENGINE = MergeTree()
            ORDER BY gene_symbol
        """)
    
    def migrate_clinvar(self):
        """Migrate complete ClinVar dataset"""
        log("\n📊 MIGRATING CLINVAR VARIANTS")
        log("="*60)
        
        vcf_file = Path("data/global/clinvar/clinvar_GRCh38.vcf.gz")
        if not vcf_file.exists():
            log(f"❌ ClinVar file not found: {vcf_file}")
            return False
        
        log(f"📁 Processing: {vcf_file} ({vcf_file.stat().st_size/(1024*1024):.1f} MB)")
        
        batch = []
        total_processed = 0
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
                    
                    # Extract gene and significance
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
                    
                    batch.append((chrom, pos, rsid, ref, alt, gene_symbol, clinical_sig, disease))
                
                # Insert batch
                if len(batch) >= self.batch_size:
                    try:
                        self.client.insert('genomics_db.clinvar_variants', batch)
                        total_processed += len(batch)
                        
                        if total_processed % self.report_interval == 0:
                            elapsed = time.time() - start_time
                            rate = total_processed / elapsed
                            log(f"   ClinVar: {total_processed:,} variants ({rate:.0f}/sec)")
                        
                        batch = []
                    except Exception as e:
                        log(f"   ❌ ClinVar batch error: {e}")
                        batch = []
        
        # Final batch
        if batch:
            self.client.insert('genomics_db.clinvar_variants', batch)
            total_processed += len(batch)
        
        # Verify
        final_count = self.client.query("SELECT COUNT(*) FROM genomics_db.clinvar_variants").result_rows[0][0]
        total_time = time.time() - start_time
        
        log(f"✅ ClinVar complete: {final_count:,} variants in {total_time/60:.1f} min")
        return True
    
    def migrate_dbsnp(self):
        """Migrate dbSNP common variants"""
        log("\n📊 MIGRATING DBSNP VARIANTS")
        log("="*60)
        
        vcf_file = Path("data/global/dbsnp/dbsnp156_common.vcf.gz")
        if not vcf_file.exists():
            log(f"❌ dbSNP file not found: {vcf_file}")
            return False
        
        log(f"📁 Processing: {vcf_file} ({vcf_file.stat().st_size/(1024*1024):.1f} MB)")
        
        batch = []
        total_processed = 0
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
                    
                    rsid = parts[2]
                    ref = parts[3]
                    alt = parts[4]
                    info = parts[7]
                    
                    # Extract allele frequency
                    allele_freq = 0.0
                    variant_class = "unknown"
                    
                    if "AF=" in info:
                        try:
                            allele_freq = float(info.split("AF=")[1].split(";")[0])
                        except:
                            pass
                    
                    if "VC=" in info:
                        try:
                            variant_class = info.split("VC=")[1].split(";")[0]
                        except:
                            pass
                    
                    batch.append((chrom, pos, rsid, ref, alt, allele_freq, variant_class))
                
                if len(batch) >= self.batch_size:
                    try:
                        self.client.insert('genomics_db.dbsnp_variants', batch)
                        total_processed += len(batch)
                        
                        if total_processed % self.report_interval == 0:
                            elapsed = time.time() - start_time
                            rate = total_processed / elapsed
                            log(f"   dbSNP: {total_processed:,} variants ({rate:.0f}/sec)")
                        
                        batch = []
                    except Exception as e:
                        log(f"   ❌ dbSNP batch error: {e}")
                        batch = []
        
        if batch:
            self.client.insert('genomics_db.dbsnp_variants', batch)
            total_processed += len(batch)
        
        final_count = self.client.query("SELECT COUNT(*) FROM genomics_db.dbsnp_variants").result_rows[0][0]
        total_time = time.time() - start_time
        
        log(f"✅ dbSNP complete: {final_count:,} variants in {total_time/60:.1f} min")
        return True
    
    def migrate_spliceai(self):
        """Migrate complete SpliceAI dataset"""
        log("\n📊 MIGRATING SPLICEAI PREDICTIONS")
        log("="*60)
        log("⚠️  This is the 3.43 BILLION row dataset")
        
        vcf_file = Path("data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz")
        if not vcf_file.exists():
            log(f"❌ SpliceAI file not found: {vcf_file}")
            return False
        
        log(f"📁 Processing: {vcf_file} ({vcf_file.stat().st_size/(1024*1024*1024):.1f} GB)")
        log("⏱️  Estimated time: 8-12 hours")
        
        batch = []
        total_processed = 0
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
                    
                    # Parse SpliceAI data
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
                
                if len(batch) >= self.batch_size:
                    try:
                        self.client.insert('genomics_db.spliceai_predictions', batch)
                        total_processed += len(batch)
                        
                        if total_processed % self.report_interval == 0:
                            elapsed = time.time() - start_time
                            rate = total_processed / elapsed
                            remaining = 3_433_300_000 - total_processed
                            eta_hours = remaining / rate / 3600 if rate > 0 else 0
                            
                            log(f"   SpliceAI: {total_processed:,} variants ({rate:.0f}/sec, ETA: {eta_hours:.1f}h)")
                        
                        batch = []
                    except Exception as e:
                        log(f"   ❌ SpliceAI batch error: {e}")
                        batch = []
        
        if batch:
            self.client.insert('genomics_db.spliceai_predictions', batch)
            total_processed += len(batch)
        
        final_count = self.client.query("SELECT COUNT(*) FROM genomics_db.spliceai_predictions").result_rows[0][0]
        total_time = time.time() - start_time
        
        log(f"✅ SpliceAI complete: {final_count:,} variants in {total_time/3600:.1f} hours")
        return True
    
    def migrate_gtex_expression(self):
        """Migrate GTEx expression data from DuckDB"""
        log("\n📊 MIGRATING GTEX EXPRESSION DATA")
        log("="*60)
        
        try:
            import duckdb
            duckdb_conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
            
            # Get GTEx data from DuckDB
            gtex_data = duckdb_conn.execute("""
                SELECT variant_id, gene_id, gene_symbol, tissue_type, slope, pvalue
                FROM gtex_v10_eqtl_associations
                ORDER BY gene_symbol
            """).fetchall()
            
            duckdb_conn.close()
            
            # Insert into ClickHouse in batches
            total_rows = len(gtex_data)
            log(f"📁 Migrating {total_rows:,} GTEx expression records")
            
            for i in range(0, total_rows, self.batch_size):
                batch = gtex_data[i:i + self.batch_size]
                self.client.insert('expression_db.gtex_expression', batch)
                
                if (i + len(batch)) % 100000 == 0:
                    log(f"   GTEx: {i + len(batch):,}/{total_rows:,} records")
            
            final_count = self.client.query("SELECT COUNT(*) FROM expression_db.gtex_expression").result_rows[0][0]
            log(f"✅ GTEx complete: {final_count:,} expression records")
            return True
            
        except Exception as e:
            log(f"❌ GTEx migration failed: {e}")
            return False
    
    def migrate_alphafold_data(self):
        """Migrate AlphaFold protein data from DuckDB"""
        log("\n📊 MIGRATING ALPHAFOLD PROTEIN DATA")
        log("="*60)
        
        try:
            import duckdb
            duckdb_conn = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)
            
            # Get AlphaFold data
            alphafold_data = duckdb_conn.execute("""
                SELECT gene_symbol, uniprot_id, protein_length, confidence_avg, confidence_min
                FROM alphafold_proteins
                WHERE gene_symbol IS NOT NULL
                ORDER BY gene_symbol
            """).fetchall()
            
            duckdb_conn.close()
            
            # Insert into ClickHouse
            total_rows = len(alphafold_data)
            log(f"📁 Migrating {total_rows:,} AlphaFold protein records")
            
            for i in range(0, total_rows, self.batch_size):
                batch = alphafold_data[i:i + self.batch_size]
                # Convert to match table schema
                converted_batch = [(row[0], row[1], f"Protein_{row[0]}", row[3], row[2]) for row in batch]
                self.client.insert('genomics_db.alphafold_proteins', converted_batch)
                
                if (i + len(batch)) % 50000 == 0:
                    log(f"   AlphaFold: {i + len(batch):,}/{total_rows:,} proteins")
            
            final_count = self.client.query("SELECT COUNT(*) FROM genomics_db.alphafold_proteins").result_rows[0][0]
            log(f"✅ AlphaFold complete: {final_count:,} protein records")
            return True
            
        except Exception as e:
            log(f"❌ AlphaFold migration failed: {e}")
            return False
    
    def run_complete_migration(self):
        """Run complete migration of all genomics data"""
        log("="*80)
        log("COMPLETE GENOMICS DATA MIGRATION")
        log("="*80)
        log("Migrating: ClinVar + dbSNP + SpliceAI + GTEx + AlphaFold")
        log("Estimated total time: 10-15 hours")
        log("="*80)
        
        # Setup
        self.setup_databases()
        
        # Migration sequence
        migrations = [
            ("ClinVar", self.migrate_clinvar),
            ("dbSNP", self.migrate_dbsnp),
            ("GTEx", self.migrate_gtex_expression),
            ("AlphaFold", self.migrate_alphafold_data),
            ("SpliceAI", self.migrate_spliceai)  # Biggest last
        ]
        
        successful = 0
        total_start = time.time()
        
        for dataset_name, migration_func in migrations:
            log(f"\n🚀 STARTING: {dataset_name} migration")
            
            try:
                if migration_func():
                    successful += 1
                    log(f"✅ {dataset_name}: SUCCESS")
                else:
                    log(f"❌ {dataset_name}: FAILED")
            except Exception as e:
                log(f"❌ {dataset_name}: ERROR - {e}")
        
        total_time = time.time() - total_start
        
        log(f"\n{'='*80}")
        log("COMPLETE MIGRATION SUMMARY")
        log('='*80)
        log(f"Successful migrations: {successful}/{len(migrations)}")
        log(f"Total time: {total_time/3600:.1f} hours")
        
        if successful >= 3:
            log("🎉 MIGRATION SUCCESS: Core genomics data migrated")
            log("🎯 Ready for ultra-fast genomics APIs")
        else:
            log("⚠️  PARTIAL SUCCESS: Some data migrated")

def main():
    log("="*80)
    log("STARTING COMPLETE GENOMICS MIGRATION")
    log("="*80)
    log("This will migrate ALL genomics data to ClickHouse")
    log("Estimated time: 10-15 hours for complete datasets")
    log("Press Ctrl+C to stop if needed")
    print()
    
    migrator = GenomicsMigrator()
    migrator.run_complete_migration()

if __name__ == "__main__":
    main()

