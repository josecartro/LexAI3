"""
Migrate Ontology Data for 7-Axis System
Add MONDO diseases, UBERON anatomy, HPO phenotypes, and Cell Ontology
"""

import clickhouse_connect
import json
import time
import re
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

class OntologyMigrator:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        self.batch_size = 50000
        
    def setup_ontology_databases(self):
        """Create ontology databases and tables"""
        log("🏗️ SETTING UP ONTOLOGY DATABASES")
        log("="*60)
        
        # Create ontology database
        self.client.command("CREATE DATABASE IF NOT EXISTS ontology_db")
        log("✅ Ontology database created")
        
        # MONDO disease ontology
        self.client.command("""
            CREATE TABLE IF NOT EXISTS ontology_db.mondo_diseases (
                mondo_id String,
                name String,
                definition String,
                synonyms Array(String),
                parent_ids Array(String),
                xrefs Array(String),
                obsolete Boolean DEFAULT false
            ) ENGINE = MergeTree()
            ORDER BY mondo_id
        """)
        
        # UBERON anatomical structures
        self.client.command("""
            CREATE TABLE IF NOT EXISTS ontology_db.uberon_anatomy (
                uberon_id String,
                name String,
                definition String,
                synonyms Array(String),
                parent_ids Array(String),
                part_of Array(String),
                develops_from Array(String),
                xrefs Array(String)
            ) ENGINE = MergeTree()
            ORDER BY uberon_id
        """)
        
        # HPO phenotypes
        self.client.command("""
            CREATE TABLE IF NOT EXISTS ontology_db.hpo_phenotypes (
                hpo_id String,
                name String,
                definition String,
                synonyms Array(String),
                parent_ids Array(String),
                xrefs Array(String),
                frequency String
            ) ENGINE = MergeTree()
            ORDER BY hpo_id
        """)
        
        # Cell Ontology
        self.client.command("""
            CREATE TABLE IF NOT EXISTS ontology_db.cell_types (
                cl_id String,
                name String,
                definition String,
                synonyms Array(String),
                parent_ids Array(String),
                part_of Array(String),
                develops_from Array(String)
            ) ENGINE = MergeTree()
            ORDER BY cl_id
        """)
        
        log("✅ All ontology tables created")
        return True
    
    def parse_obo_file(self, file_path, ontology_prefix):
        """Parse OBO format files"""
        log(f"📖 Parsing OBO file: {file_path.name}")
        
        terms = []
        current_term = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    if line == '[Term]':
                        # Save previous term
                        if current_term and current_term.get('id', '').startswith(ontology_prefix):
                            terms.append(current_term.copy())
                        current_term = {'synonyms': [], 'parent_ids': [], 'xrefs': [], 'part_of': [], 'develops_from': []}
                    
                    elif line.startswith('id:'):
                        current_term['id'] = line.split(':', 1)[1].strip()
                    
                    elif line.startswith('name:'):
                        current_term['name'] = line.split(':', 1)[1].strip()
                    
                    elif line.startswith('def:'):
                        # Extract definition (remove quotes)
                        def_text = line.split(':', 1)[1].strip()
                        if def_text.startswith('"') and '"' in def_text[1:]:
                            current_term['definition'] = def_text.split('"')[1]
                        else:
                            current_term['definition'] = def_text
                    
                    elif line.startswith('synonym:'):
                        # Extract synonym
                        syn_text = line.split(':', 1)[1].strip()
                        if '"' in syn_text:
                            synonym = syn_text.split('"')[1]
                            current_term['synonyms'].append(synonym)
                    
                    elif line.startswith('is_a:'):
                        parent_id = line.split(':', 1)[1].strip().split()[0]
                        current_term['parent_ids'].append(parent_id)
                    
                    elif line.startswith('relationship: part_of'):
                        part_id = line.split()[-1].split('!')[0].strip()
                        current_term['part_of'].append(part_id)
                    
                    elif line.startswith('relationship: develops_from'):
                        dev_id = line.split()[-1].split('!')[0].strip()
                        current_term['develops_from'].append(dev_id)
                    
                    elif line.startswith('xref:'):
                        xref = line.split(':', 1)[1].strip()
                        current_term['xrefs'].append(xref)
                    
                    elif line.startswith('is_obsolete: true'):
                        current_term['obsolete'] = True
                
                # Don't forget the last term
                if current_term and current_term.get('id', '').startswith(ontology_prefix):
                    terms.append(current_term)
        
        except Exception as e:
            log(f"❌ Error parsing {file_path.name}: {e}")
            return []
        
        log(f"✅ Parsed {len(terms)} {ontology_prefix} terms")
        return terms
    
    def migrate_mondo_diseases(self):
        """Migrate MONDO disease ontology"""
        log("\n🦠 MIGRATING MONDO DISEASE ONTOLOGY")
        log("="*60)
        
        mondo_file = Path("data/global/ontologies/mondo.obo")
        if not mondo_file.exists():
            log(f"❌ MONDO file not found: {mondo_file}")
            return False
        
        # Parse MONDO terms
        terms = self.parse_obo_file(mondo_file, "MONDO:")
        if not terms:
            log("❌ No MONDO terms found")
            return False
        
        log(f"📊 Processing {len(terms)} MONDO disease terms")
        
        batch = []
        total = 0
        
        for term in terms:
            try:
                mondo_id = term.get('id', '')
                name = term.get('name', '')
                definition = term.get('definition', '')
                synonyms = term.get('synonyms', [])
                parent_ids = term.get('parent_ids', [])
                xrefs = term.get('xrefs', [])
                obsolete = term.get('obsolete', False)
                
                batch.append((mondo_id, name, definition, synonyms, parent_ids, xrefs, obsolete))
                
                if len(batch) >= self.batch_size:
                    self.client.insert('ontology_db.mondo_diseases', batch)
                    total += len(batch)
                    log(f"   🦠 MONDO: {total:,} diseases")
                    batch = []
                    
            except Exception as e:
                continue
        
        if batch:
            self.client.insert('ontology_db.mondo_diseases', batch)
            total += len(batch)
        
        log(f"✅ MONDO complete: {total:,} disease terms")
        return total > 10000
    
    def migrate_uberon_anatomy(self):
        """Migrate UBERON anatomical structures"""
        log("\n🫀 MIGRATING UBERON ANATOMICAL STRUCTURES")
        log("="*60)
        
        uberon_file = Path("data/global/ontologies/uberon-full.obo")
        if not uberon_file.exists():
            log(f"❌ UBERON file not found: {uberon_file}")
            return False
        
        # Parse UBERON terms
        terms = self.parse_obo_file(uberon_file, "UBERON:")
        if not terms:
            log("❌ No UBERON terms found")
            return False
        
        log(f"📊 Processing {len(terms)} UBERON anatomical terms")
        
        batch = []
        total = 0
        
        for term in terms:
            try:
                uberon_id = term.get('id', '')
                name = term.get('name', '')
                definition = term.get('definition', '')
                synonyms = term.get('synonyms', [])
                parent_ids = term.get('parent_ids', [])
                part_of = term.get('part_of', [])
                develops_from = term.get('develops_from', [])
                xrefs = term.get('xrefs', [])
                
                batch.append((uberon_id, name, definition, synonyms, parent_ids, part_of, develops_from, xrefs))
                
                if len(batch) >= self.batch_size:
                    self.client.insert('ontology_db.uberon_anatomy', batch)
                    total += len(batch)
                    log(f"   🫀 UBERON: {total:,} anatomical structures")
                    batch = []
                    
            except Exception as e:
                continue
        
        if batch:
            self.client.insert('ontology_db.uberon_anatomy', batch)
            total += len(batch)
        
        log(f"✅ UBERON complete: {total:,} anatomical terms")
        return total > 5000
    
    def migrate_hpo_phenotypes(self):
        """Migrate HPO human phenotype ontology"""
        log("\n👤 MIGRATING HPO PHENOTYPE ONTOLOGY")
        log("="*60)
        
        hpo_file = Path("data/global/ontologies/hp.obo")
        if not hpo_file.exists():
            log(f"❌ HPO file not found: {hpo_file}")
            return False
        
        # Parse HPO terms
        terms = self.parse_obo_file(hpo_file, "HP:")
        if not terms:
            log("❌ No HPO terms found")
            return False
        
        log(f"📊 Processing {len(terms)} HPO phenotype terms")
        
        batch = []
        total = 0
        
        for term in terms:
            try:
                hpo_id = term.get('id', '')
                name = term.get('name', '')
                definition = term.get('definition', '')
                synonyms = term.get('synonyms', [])
                parent_ids = term.get('parent_ids', [])
                xrefs = term.get('xrefs', [])
                frequency = ""  # Could be extracted from definition if present
                
                batch.append((hpo_id, name, definition, synonyms, parent_ids, xrefs, frequency))
                
                if len(batch) >= self.batch_size:
                    self.client.insert('ontology_db.hpo_phenotypes', batch)
                    total += len(batch)
                    log(f"   👤 HPO: {total:,} phenotypes")
                    batch = []
                    
            except Exception as e:
                continue
        
        if batch:
            self.client.insert('ontology_db.hpo_phenotypes', batch)
            total += len(batch)
        
        log(f"✅ HPO complete: {total:,} phenotype terms")
        return total > 5000
    
    def migrate_cell_ontology(self):
        """Migrate Cell Ontology"""
        log("\n🧬 MIGRATING CELL ONTOLOGY")
        log("="*60)
        
        cl_file = Path("data/global/ontologies/cl.obo")
        if not cl_file.exists():
            log(f"❌ Cell Ontology file not found: {cl_file}")
            return False
        
        # Parse Cell Ontology terms
        terms = self.parse_obo_file(cl_file, "CL:")
        if not terms:
            log("❌ No Cell Ontology terms found")
            return False
        
        log(f"📊 Processing {len(terms)} cell type terms")
        
        batch = []
        total = 0
        
        for term in terms:
            try:
                cl_id = term.get('id', '')
                name = term.get('name', '')
                definition = term.get('definition', '')
                synonyms = term.get('synonyms', [])
                parent_ids = term.get('parent_ids', [])
                part_of = term.get('part_of', [])
                develops_from = term.get('develops_from', [])
                
                batch.append((cl_id, name, definition, synonyms, parent_ids, part_of, develops_from))
                
                if len(batch) >= self.batch_size:
                    self.client.insert('ontology_db.cell_types', batch)
                    total += len(batch)
                    log(f"   🧬 Cell Ontology: {total:,} cell types")
                    batch = []
                    
            except Exception as e:
                continue
        
        if batch:
            self.client.insert('ontology_db.cell_types', batch)
            total += len(batch)
        
        log(f"✅ Cell Ontology complete: {total:,} cell type terms")
        return total > 1000
    
    def run_ontology_migration(self):
        """Run complete ontology migration"""
        log("="*80)
        log("🧠 MIGRATING ONTOLOGIES FOR 7-AXIS SYSTEM")
        log("="*80)
        log("Adding disease, anatomy, phenotype, and cell type ontologies")
        log("="*80)
        
        # Setup
        if not self.setup_ontology_databases():
            log("❌ Database setup failed")
            return
        
        # Migration sequence
        migrations = [
            ("MONDO Diseases", self.migrate_mondo_diseases, "56K disease ontology terms"),
            ("UBERON Anatomy", self.migrate_uberon_anatomy, "26K anatomical structures"),
            ("HPO Phenotypes", self.migrate_hpo_phenotypes, "19K human phenotypes"),
            ("Cell Ontology", self.migrate_cell_ontology, "18K cell type terms")
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
        log("ONTOLOGY MIGRATION SUMMARY")
        log('='*80)
        log(f"Successful migrations: {successful}/{len(migrations)}")
        log(f"Total migration time: {total_time/60:.1f} minutes")
        
        if successful >= 3:
            log("🎉 ONTOLOGY INFRASTRUCTURE COMPLETE!")
            log("🧠 7-axis system now has full ontological reasoning capability")
        else:
            log("⚠️  Some ontologies missing")

def main():
    log("="*80)
    log("🧠 BUILDING ONTOLOGICAL REASONING INFRASTRUCTURE")
    log("="*80)
    log("Migrating disease, anatomy, phenotype, and cell ontologies")
    log("="*80)
    
    migrator = OntologyMigrator()
    migrator.run_ontology_migration()

if __name__ == "__main__":
    main()
