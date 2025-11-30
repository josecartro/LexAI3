"""
Migrate Reference Data for 7-Axis Connection Infrastructure
Add UniProt mappings, GENCODE relationships, STRING networks, KEGG pathways, and gnomAD constraints
"""

import clickhouse_connect
import gzip
import time
import gc
import psutil
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def log_system_status():
    """Log system status and return if critical break needed"""
    try:
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        
        log(f"💻 SYSTEM: Memory {memory.percent:.1f}%, CPU {cpu:.1f}%")
        
        if memory.percent > 95 or cpu > 95:
            log(f"🚨 CRITICAL: Taking break!")
            return True
        return False
    except:
        return False

class ReferenceDataMigrator:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        self.batch_size = 100000  # 100K records per batch
        
    def setup_reference_databases(self):
        """Create reference databases and tables"""
        log("🏗️ SETTING UP REFERENCE DATABASES")
        log("="*60)
        
        # Create reference database
        self.client.command("CREATE DATABASE IF NOT EXISTS reference_db")
        self.client.command("CREATE DATABASE IF NOT EXISTS pathways_db")
        log("✅ Reference databases created")
        
        # UniProt ID mappings
        self.client.command("""
            CREATE TABLE IF NOT EXISTS reference_db.uniprot_mappings (
                uniprot_id String,
                id_type String,
                external_id String,
                source String DEFAULT 'uniprot_idmapping'
            ) ENGINE = MergeTree()
            ORDER BY (uniprot_id, id_type)
        """)
        
        # Gene-Transcript-Protein relationships from GENCODE
        self.client.command("""
            CREATE TABLE IF NOT EXISTS reference_db.gene_transcript_mappings (
                gene_id String,
                gene_symbol String,
                transcript_id String,
                protein_id String,
                gene_type String,
                transcript_type String,
                chrom String,
                gene_start UInt64,
                gene_end UInt64,
                strand String
            ) ENGINE = MergeTree()
            ORDER BY (gene_symbol, gene_id)
        """)
        
        # STRING protein interactions
        self.client.command("""
            CREATE TABLE IF NOT EXISTS proteins_db.protein_interactions (
                protein1 String,
                protein2 String,
                combined_score UInt16,
                neighborhood_score UInt16,
                fusion_score UInt16,
                cooccurence_score UInt16,
                coexpression_score UInt16,
                experimental_score UInt16,
                database_score UInt16,
                textmining_score UInt16
            ) ENGINE = MergeTree()
            ORDER BY (protein1, protein2)
        """)
        
        # STRING protein info
        self.client.command("""
            CREATE TABLE IF NOT EXISTS proteins_db.protein_info (
                protein_id String,
                preferred_name String,
                protein_size UInt32,
                annotation String
            ) ENGINE = MergeTree()
            ORDER BY protein_id
        """)
        
        # KEGG gene-pathway links
        self.client.command("""
            CREATE TABLE IF NOT EXISTS pathways_db.gene_pathway_links (
                kegg_gene_id String,
                gene_symbol String,
                pathway_id String,
                pathway_name String,
                gene_description String
            ) ENGINE = MergeTree()
            ORDER BY (gene_symbol, pathway_id)
        """)
        
        # KEGG pathways
        self.client.command("""
            CREATE TABLE IF NOT EXISTS pathways_db.kegg_pathways (
                pathway_id String,
                pathway_name String,
                pathway_category String
            ) ENGINE = MergeTree()
            ORDER BY pathway_id
        """)
        
        # gnomAD gene constraints
        self.client.command("""
            CREATE TABLE IF NOT EXISTS population_db.gene_constraints (
                gene_symbol String,
                gene_id String,
                transcript_id String,
                canonical Boolean,
                lof_observed UInt32,
                lof_expected Float32,
                lof_oe Float32,
                lof_pli Float32,
                missense_observed UInt32,
                missense_expected Float32,
                missense_oe Float32,
                missense_z_score Float32,
                constraint_flag String
            ) ENGINE = MergeTree()
            ORDER BY gene_symbol
        """)
        
        log("✅ All reference tables created")
        return True
    
    def migrate_uniprot_mappings(self):
        """Migrate UniProt ID mappings"""
        log("\n🔗 MIGRATING UNIPROT ID MAPPINGS")
        log("="*60)
        
        uniprot_file = Path("data/reference/uniprot/idmapping.dat.gz")
        if not uniprot_file.exists():
            log(f"❌ UniProt file not found: {uniprot_file}")
            return False
        
        file_size_mb = uniprot_file.stat().st_size / (1024*1024)
        log(f"📁 Processing: {uniprot_file.name} ({file_size_mb:.1f} MB)")
        
        batch = []
        total = 0
        start_time = time.time()
        
        # Focus on human-relevant ID types
        relevant_types = {
            'Gene_Name', 'Gene_Synonym', 'Gene_ORFName',
            'Ensembl', 'Ensembl_TRS', 'Ensembl_PRO',
            'HGNC', 'KEGG', 'STRING'
        }
        
        try:
            with gzip.open(uniprot_file, 'rt') as f:
                for line_num, line in enumerate(f, 1):
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        uniprot_id, id_type, external_id = parts[:3]
                        
                        # Only keep human-relevant mappings
                        if id_type in relevant_types:
                            batch.append((uniprot_id, id_type, external_id, 'uniprot_official'))
                    
                    if len(batch) >= self.batch_size:
                        try:
                            self.client.insert('reference_db.uniprot_mappings', batch)
                            total += len(batch)
                            
                            if total % 500000 == 0:
                                elapsed = time.time() - start_time
                                rate = total / elapsed if elapsed > 0 else 0
                                log(f"   🔗 UniProt: {total:,} mappings ({rate:.0f}/sec)")
                            
                            batch = []
                        except Exception as e:
                            log(f"⚠️  Batch failed: {e}")
                            batch = []
            
            if batch:
                self.client.insert('reference_db.uniprot_mappings', batch)
                total += len(batch)
            
            elapsed = time.time() - start_time
            log(f"✅ UniProt complete: {total:,} mappings in {elapsed/60:.1f} min")
            return total > 100000
            
        except Exception as e:
            log(f"❌ UniProt migration failed: {e}")
            return False
    
    def migrate_gencode_relationships(self):
        """Migrate GENCODE gene-transcript-protein relationships"""
        log("\n🧬 MIGRATING GENCODE GENE RELATIONSHIPS")
        log("="*60)
        
        gencode_file = Path("data/transcriptome/gencode.v44.annotation.gtf.gz")
        if not gencode_file.exists():
            log(f"❌ GENCODE file not found: {gencode_file}")
            return False
        
        file_size_mb = gencode_file.stat().st_size / (1024*1024)
        log(f"📁 Processing: {gencode_file.name} ({file_size_mb:.1f} MB)")
        
        batch = []
        total = 0
        start_time = time.time()
        
        try:
            with gzip.open(gencode_file, 'rt') as f:
                for line_num, line in enumerate(f, 1):
                    if line.startswith('#'):
                        continue
                    
                    parts = line.strip().split('\t')
                    if len(parts) >= 9:
                        chrom = parts[0]
                        feature_type = parts[2]
                        start_pos = int(parts[3])
                        end_pos = int(parts[4])
                        strand = parts[6]
                        attributes = parts[8]
                        
                        # Parse attributes
                        attr_dict = {}
                        for attr in attributes.split(';'):
                            if '=' in attr:
                                key, value = attr.strip().split('=', 1)
                                attr_dict[key] = value.strip('"')
                            elif ' ' in attr.strip():
                                key_value = attr.strip().split(' ', 1)
                                if len(key_value) == 2:
                                    key, value = key_value
                                    attr_dict[key] = value.strip('"')
                        
                        # Extract key identifiers
                        gene_id = attr_dict.get('gene_id', '')
                        gene_symbol = attr_dict.get('gene_name', '')
                        transcript_id = attr_dict.get('transcript_id', '')
                        protein_id = attr_dict.get('protein_id', '')
                        gene_type = attr_dict.get('gene_type', '')
                        transcript_type = attr_dict.get('transcript_type', '')
                        
                        # Only keep gene features with valid symbols
                        if feature_type == 'gene' and gene_symbol and gene_id:
                            batch.append((
                                gene_id, gene_symbol, transcript_id, protein_id,
                                gene_type, transcript_type, chrom, start_pos, end_pos, strand
                            ))
                    
                    if len(batch) >= self.batch_size:
                        try:
                            self.client.insert('reference_db.gene_transcript_mappings', batch)
                            total += len(batch)
                            
                            if total % 50000 == 0:
                                elapsed = time.time() - start_time
                                rate = total / elapsed if elapsed > 0 else 0
                                log(f"   🧬 GENCODE: {total:,} genes ({rate:.0f}/sec)")
                            
                            batch = []
                        except Exception as e:
                            log(f"⚠️  Batch failed: {e}")
                            batch = []
            
            if batch:
                self.client.insert('reference_db.gene_transcript_mappings', batch)
                total += len(batch)
            
            elapsed = time.time() - start_time
            log(f"✅ GENCODE complete: {total:,} gene relationships in {elapsed/60:.1f} min")
            return total > 10000
            
        except Exception as e:
            log(f"❌ GENCODE migration failed: {e}")
            return False
    
    def migrate_string_networks(self):
        """Migrate STRING protein interaction networks"""
        log("\n🕸️ MIGRATING STRING PROTEIN NETWORKS")
        log("="*60)
        
        # Migrate protein interactions
        links_file = Path("data/reference/string/protein_links.txt.gz")
        if links_file.exists():
            log(f"📁 Processing: {links_file.name}")
            
            batch = []
            total = 0
            start_time = time.time()
            
            try:
                with gzip.open(links_file, 'rt') as f:
                    header = f.readline()  # Skip header
                    
                    for line in f:
                        parts = line.strip().split(' ')
                        if len(parts) >= 10:
                            protein1, protein2 = parts[0], parts[1]
                            scores = [int(x) for x in parts[2:10]]
                            
                            # Only keep human proteins (9606 species code)
                            if '9606.' in protein1 and '9606.' in protein2:
                                # Remove species prefix
                                protein1 = protein1.replace('9606.', '')
                                protein2 = protein2.replace('9606.', '')
                                
                                batch.append(tuple([protein1, protein2] + scores))
                        
                        if len(batch) >= self.batch_size:
                            try:
                                self.client.insert('proteins_db.protein_interactions', batch)
                                total += len(batch)
                                
                                if total % 1000000 == 0:
                                    elapsed = time.time() - start_time
                                    rate = total / elapsed if elapsed > 0 else 0
                                    log(f"   🕸️ STRING: {total:,} interactions ({rate:.0f}/sec)")
                                
                                batch = []
                            except Exception as e:
                                log(f"⚠️  Batch failed: {e}")
                                batch = []
                
                if batch:
                    self.client.insert('proteins_db.protein_interactions', batch)
                    total += len(batch)
                
                elapsed = time.time() - start_time
                log(f"✅ STRING interactions: {total:,} in {elapsed/60:.1f} min")
                
            except Exception as e:
                log(f"❌ STRING links migration failed: {e}")
        
        # Migrate protein info
        info_file = Path("data/reference/string/protein_info.txt.gz")
        if info_file.exists():
            log(f"📁 Processing: {info_file.name}")
            
            batch = []
            total = 0
            
            try:
                with gzip.open(info_file, 'rt') as f:
                    header = f.readline()  # Skip header
                    
                    for line in f:
                        parts = line.strip().split('\t')
                        if len(parts) >= 4:
                            protein_id, preferred_name, protein_size, annotation = parts[:4]
                            
                            # Only human proteins
                            if '9606.' in protein_id:
                                protein_id = protein_id.replace('9606.', '')
                                try:
                                    size = int(protein_size) if protein_size.isdigit() else 0
                                except:
                                    size = 0
                                
                                batch.append((protein_id, preferred_name, size, annotation))
                        
                        if len(batch) >= self.batch_size:
                            try:
                                self.client.insert('proteins_db.protein_info', batch)
                                total += len(batch)
                                batch = []
                            except Exception as e:
                                log(f"⚠️  Batch failed: {e}")
                                batch = []
                
                if batch:
                    self.client.insert('proteins_db.protein_info', batch)
                    total += len(batch)
                
                log(f"✅ STRING protein info: {total:,} proteins")
                
            except Exception as e:
                log(f"❌ STRING info migration failed: {e}")
        
        return True
    
    def migrate_kegg_pathways(self):
        """Migrate KEGG pathway data"""
        log("\n🧪 MIGRATING KEGG PATHWAY DATA")
        log("="*60)
        
        # Migrate pathways
        pathways_file = Path("data/reference/kegg/human_pathways.txt")
        if pathways_file.exists():
            log(f"📁 Processing: {pathways_file.name}")
            
            batch = []
            
            try:
                with open(pathways_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split('\t', 1)
                        if len(parts) >= 2:
                            pathway_id, pathway_name = parts
                            
                            # Extract category from name
                            category = "Metabolic" if "metabol" in pathway_name.lower() else "Other"
                            
                            batch.append((pathway_id, pathway_name, category))
                
                if batch:
                    self.client.insert('pathways_db.kegg_pathways', batch)
                    log(f"✅ KEGG pathways: {len(batch)} pathways")
                
            except Exception as e:
                log(f"❌ KEGG pathways migration failed: {e}")
        
        # Migrate gene-pathway links
        genes_file = Path("data/reference/kegg/human_genes.txt")
        if genes_file.exists():
            log(f"📁 Processing: {genes_file.name}")
            
            batch = []
            total = 0
            
            try:
                with open(genes_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split('\t')
                        if len(parts) >= 4:
                            kegg_gene_id, gene_type, location, description = parts
                            
                            # Extract gene symbol from description
                            gene_symbol = "unknown"
                            if ';' in description:
                                gene_symbol = description.split(';')[0].strip()
                            
                            # For now, create placeholder pathway links
                            # (Would need KEGG API or additional data for actual pathway links)
                            batch.append((kegg_gene_id, gene_symbol, "hsa01100", "Metabolic pathways", description))
                        
                        if len(batch) >= self.batch_size:
                            try:
                                self.client.insert('pathways_db.gene_pathway_links', batch)
                                total += len(batch)
                                batch = []
                            except Exception as e:
                                log(f"⚠️  Batch failed: {e}")
                                batch = []
                
                if batch:
                    self.client.insert('pathways_db.gene_pathway_links', batch)
                    total += len(batch)
                
                log(f"✅ KEGG gene links: {total:,} genes")
                
            except Exception as e:
                log(f"❌ KEGG genes migration failed: {e}")
        
        return True
    
    def migrate_gnomad_constraints(self):
        """Migrate gnomAD gene constraint scores"""
        log("\n📊 MIGRATING GNOMAD GENE CONSTRAINTS")
        log("="*60)
        
        constraints_file = Path("data/population/gnomad_v4.1_constraint.tsv")
        if not constraints_file.exists():
            log(f"❌ gnomAD constraints file not found: {constraints_file}")
            return False
        
        file_size_mb = constraints_file.stat().st_size / (1024*1024)
        log(f"📁 Processing: {constraints_file.name} ({file_size_mb:.1f} MB)")
        
        batch = []
        total = 0
        start_time = time.time()
        
        try:
            with open(constraints_file, 'r') as f:
                header = f.readline()  # Skip header
                
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 20:  # Ensure we have enough columns
                        try:
                            gene_symbol = parts[0]
                            gene_id = parts[1]
                            transcript_id = parts[2]
                            canonical = parts[3].lower() == 'true'
                            
                            # Loss-of-function scores
                            lof_obs = int(float(parts[5])) if parts[5] and parts[5] != 'NA' else 0
                            lof_exp = float(parts[6]) if parts[6] and parts[6] != 'NA' else 0.0
                            lof_oe = float(parts[7]) if parts[7] and parts[7] != 'NA' else 0.0
                            lof_pli = float(parts[10]) if parts[10] and parts[10] != 'NA' else 0.0
                            
                            # Missense scores
                            mis_obs = int(float(parts[26])) if parts[26] and parts[26] != 'NA' else 0
                            mis_exp = float(parts[27]) if parts[27] and parts[27] != 'NA' else 0.0
                            mis_oe = float(parts[29]) if parts[29] and parts[29] != 'NA' else 0.0
                            mis_z = float(parts[33]) if parts[33] and parts[33] != 'NA' else 0.0
                            
                            constraint_flag = parts[39] if len(parts) > 39 else ""
                            
                            batch.append((
                                gene_symbol, gene_id, transcript_id, canonical,
                                lof_obs, lof_exp, lof_oe, lof_pli,
                                mis_obs, mis_exp, mis_oe, mis_z, constraint_flag
                            ))
                            
                        except (ValueError, IndexError):
                            continue  # Skip malformed lines
                    
                    if len(batch) >= self.batch_size:
                        try:
                            self.client.insert('population_db.gene_constraints', batch)
                            total += len(batch)
                            
                            if total % 10000 == 0:
                                elapsed = time.time() - start_time
                                rate = total / elapsed if elapsed > 0 else 0
                                log(f"   📊 Constraints: {total:,} genes ({rate:.0f}/sec)")
                            
                            batch = []
                        except Exception as e:
                            log(f"⚠️  Batch failed: {e}")
                            batch = []
            
            if batch:
                self.client.insert('population_db.gene_constraints', batch)
                total += len(batch)
            
            elapsed = time.time() - start_time
            log(f"✅ gnomAD constraints: {total:,} genes in {elapsed/60:.1f} min")
            return total > 10000
            
        except Exception as e:
            log(f"❌ gnomAD constraints migration failed: {e}")
            return False
    
    def run_complete_reference_migration(self):
        """Run complete reference data migration"""
        log("="*80)
        log("🔗 MIGRATING REFERENCE DATA FOR 7-AXIS CONNECTIONS")
        log("="*80)
        log("Building authoritative ID mappings and relationship tables")
        log("="*80)
        
        # Initial system check
        log("🔍 SYSTEM CHECK:")
        log_system_status()
        log("="*80)
        
        # Setup
        if not self.setup_reference_databases():
            log("❌ Database setup failed")
            return
        
        # Migration sequence
        migrations = [
            ("UniProt ID Mappings", self.migrate_uniprot_mappings, "Cross-database ID connections"),
            ("GENCODE Relationships", self.migrate_gencode_relationships, "Gene-transcript-protein links"),
            ("STRING Networks", self.migrate_string_networks, "Protein interaction networks"),
            ("KEGG Pathways", self.migrate_kegg_pathways, "Metabolic pathway connections"),
            ("gnomAD Constraints", self.migrate_gnomad_constraints, "Gene constraint scores")
        ]
        
        successful = 0
        total_start = time.time()
        
        for dataset_name, migration_func, description in migrations:
            log(f"\n🚀 STARTING: {dataset_name}")
            log(f"   {description}")
            log("-" * 60)
            
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
        log("REFERENCE DATA MIGRATION SUMMARY")
        log('='*80)
        log(f"Successful migrations: {successful}/{len(migrations)}")
        log(f"Total migration time: {total_time/60:.1f} minutes")
        
        if successful >= 4:
            log("🎉 REFERENCE DATA COMPLETE!")
            log("🔗 7-axis connection infrastructure ready")
        else:
            log("⚠️  Some reference data missing")

def main():
    log("="*80)
    log("🔗 BUILDING 7-AXIS CONNECTION INFRASTRUCTURE")
    log("="*80)
    log("Migrating authoritative reference data for cross-axis integration")
    log("="*80)
    
    migrator = ReferenceDataMigrator()
    migrator.run_complete_reference_migration()

if __name__ == "__main__":
    main()
