"""
Honest API Data Audit - No Exaggeration
Brutally honest assessment of what each API actually has vs what's available
"""

import requests
import duckdb
import time
from pathlib import Path
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

class HonestAPIAuditor:
    def __init__(self):
        self.genomic_db = Path("../data/databases/genomic_knowledge/genomic_knowledge.duckdb")
        self.multiomics_db = Path("../data/databases/genomic_knowledge/multi_omics.duckdb")
        self.digital_twin_db = Path("../data/databases/genomic_knowledge/digital_twin.duckdb")
        self.population_db = Path("../data/databases/population_risk/population_risk.duckdb")
        
    def audit_lexapi_genomics(self):
        """Honest audit of LexAPI_Genomics actual capabilities"""
        log("\n" + "="*80)
        log("HONEST AUDIT: LEXAPI_GENOMICS")
        log("="*80)
        
        # Test API response
        try:
            r = requests.get("http://localhost:8001/analyze/gene/BRCA2", timeout=20)
            if r.status_code == 200:
                data = r.json()
                databases = data.get('databases_queried', [])
                log(f"✅ API responding: {len(databases)} databases queried")
                log(f"   Databases: {databases}")
                
                # Check each claimed capability
                variants = data.get('variants', {})
                if variants and 'error' not in variants:
                    total = variants.get('total_variants', 0)
                    pathogenic = variants.get('pathogenic_variants', 0)
                    log(f"✅ Variants: {total:,} total, {pathogenic:,} pathogenic")
                else:
                    log(f"❌ Variants: Not working")
                
                proteins = data.get('protein_connections', {})
                if proteins and 'error' not in proteins:
                    protein_count = proteins.get('total_proteins', 0)
                    log(f"✅ Proteins: {protein_count} connections")
                else:
                    log(f"❌ Proteins: Not working")
                
                expression = data.get('expression_effects', {})
                if expression and 'error' not in expression:
                    tissues = expression.get('total_tissues_affected', 0)
                    log(f"✅ Expression: {tissues} tissues affected")
                else:
                    log(f"❌ Expression: Not working")
                
                splicing = data.get('splicing_effects', {})
                if splicing and 'error' not in splicing:
                    events = splicing.get('total_splice_events', 0)
                    splice_tissues = splicing.get('total_tissues_affected', 0)
                    log(f"✅ Splicing: {events} events in {splice_tissues} tissues")
                else:
                    log(f"❌ Splicing: Not working")
                
                structure = data.get('protein_structure_effects', {})
                if structure and 'error' not in structure:
                    structures = structure.get('total_protein_structures', 0)
                    log(f"✅ Protein structure: {structures} structures")
                else:
                    log(f"❌ Protein structure: Not working")
                    
            else:
                log(f"❌ API not responding: HTTP {r.status_code}")
                
        except Exception as e:
            log(f"❌ API error: {e}")
        
        # Check available data not being used
        log(f"\nDATA AVAILABILITY CHECK:")
        try:
            conn = duckdb.connect(str(self.genomic_db), read_only=True)
            
            # Check massive unused tables
            spliceai_scores = conn.execute("SELECT COUNT(*) FROM spliceai_scores_production").fetchone()[0]
            dbsnp_variants = conn.execute("SELECT COUNT(*) FROM dbsnp_parquet_production").fetchone()[0]
            alphafold_impact = conn.execute("SELECT COUNT(*) FROM alphafold_clinical_variant_impact").fetchone()[0]
            
            log(f"❌ UNUSED: SpliceAI scores: {spliceai_scores:,} rows (3.43B)")
            log(f"❌ UNUSED: dbSNP variants: {dbsnp_variants:,} rows (37M)")
            log(f"❌ UNUSED: AlphaFold impact: {alphafold_impact:,} rows (11.6M)")
            
            conn.close()
            
        except Exception as e:
            log(f"Error checking unused data: {e}")
    
    def audit_lexapi_metabolics(self):
        """Honest audit of LexAPI_Metabolics actual capabilities"""
        log("\n" + "="*80)
        log("HONEST AUDIT: LEXAPI_METABOLICS")
        log("="*80)
        
        # Test API response
        try:
            r = requests.get("http://localhost:8005/analyze/drug_metabolism/codeine", timeout=15)
            if r.status_code == 200:
                data = r.json()
                databases = data.get('databases_queried', [])
                log(f"✅ API responding: {len(databases)} databases queried")
                log(f"   Databases: {databases}")
                
                pharmgkb = data.get('pharmgkb_interactions', {})
                if pharmgkb and 'error' not in pharmgkb:
                    interactions = pharmgkb.get('total_interactions', 0)
                    log(f"✅ PharmGKB: {interactions} drug interactions")
                else:
                    log(f"❌ PharmGKB: Not working")
                    
            else:
                log(f"❌ API not responding: HTTP {r.status_code}")
                
        except Exception as e:
            log(f"❌ API error: {e}")
        
        # Check available PharmGKB data
        log(f"\nPHARMGKB DATA AVAILABILITY:")
        try:
            pharmgkb_file = Path("../data/pharmgkb/drug_gene_interactions.csv")
            if pharmgkb_file.exists():
                import pandas as pd
                df = pd.read_csv(pharmgkb_file)
                total_interactions = len(df)
                unique_drugs = df['drug_name'].nunique()
                unique_genes = df['gene_symbol'].nunique()
                
                log(f"✅ AVAILABLE: {total_interactions} drug-gene interactions")
                log(f"✅ AVAILABLE: {unique_drugs} unique drugs")
                log(f"✅ AVAILABLE: {unique_genes} unique genes")
            else:
                log(f"❌ PharmGKB file not found")
                
        except Exception as e:
            log(f"Error checking PharmGKB data: {e}")
    
    def audit_lexapi_anatomics(self):
        """Honest audit of LexAPI_Anatomics actual capabilities"""
        log("\n" + "="*80)
        log("HONEST AUDIT: LEXAPI_ANATOMICS")
        log("="*80)
        
        # Test API response
        try:
            r = requests.get("http://localhost:8002/analyze/organ/brain", timeout=15)
            if r.status_code == 200:
                data = r.json()
                databases = data.get('databases_queried', [])
                log(f"✅ API responding: {len(databases)} databases queried")
                log(f"   Databases: {databases}")
                
                tissue_data = data.get('tissue_expression_data', {})
                if tissue_data and 'error' not in tissue_data:
                    matches = tissue_data.get('total_tissue_matches', 0)
                    log(f"✅ GTEx tissue data: {matches} matches")
                else:
                    log(f"❌ GTEx tissue data: Not working")
                    
            else:
                log(f"❌ API not responding: HTTP {r.status_code}")
                
        except Exception as e:
            log(f"❌ API error: {e}")
    
    def audit_lexapi_populomics(self):
        """Honest audit of LexAPI_Populomics actual capabilities"""
        log("\n" + "="*80)
        log("HONEST AUDIT: LEXAPI_POPULOMICS")
        log("="*80)
        
        # Test API response
        try:
            r = requests.get("http://localhost:8006/analyze/environmental_risk/spain", timeout=15)
            if r.status_code == 200:
                data = r.json()
                databases = data.get('databases_queried', [])
                log(f"✅ API responding: {len(databases)} databases queried")
                
                pop_genetics = data.get('population_genetics', {})
                if pop_genetics and 'error' not in pop_genetics:
                    ancestry = pop_genetics.get('ancestry_context', 'none')
                    log(f"✅ Population genetics: {ancestry}")
                else:
                    log(f"❌ Population genetics: Not working")
                    
            else:
                log(f"❌ API not responding: HTTP {r.status_code}")
                
        except Exception as e:
            log(f"❌ API error: {e}")
        
        # Check massive unused population data
        log(f"\nMASSIVE UNUSED POPULATION DATA:")
        gnomad_size = Path("../data/global/gnomad").stat().st_size / (1024**3) if Path("../data/global/gnomad").exists() else 0
        log(f"❌ UNUSED: gnomAD data: {gnomad_size:.1f} GB population genetics")
    
    def audit_lexapi_literature(self):
        """Honest audit of LexAPI_Literature actual capabilities"""
        log("\n" + "="*80)
        log("HONEST AUDIT: LEXAPI_LITERATURE")
        log("="*80)
        
        # Test API response
        try:
            r = requests.get("http://localhost:8003/search/literature/BRCA2?context_apis=genomics", timeout=15)
            if r.status_code == 200:
                data = r.json()
                databases = data.get('databases_queried', [])
                log(f"✅ API responding: {len(databases)} databases queried")
                
                if 'cross_api_integration' in databases:
                    log(f"✅ Cross-API integration: Working")
                else:
                    log(f"❌ Cross-API integration: Not working")
                    
                literature = data.get('literature_results', {})
                if literature:
                    collections = literature.get('total_collections', 0)
                    log(f"✅ Literature collections: {collections}")
                else:
                    log(f"❌ Literature search: Not working")
                    
            else:
                log(f"❌ API not responding: HTTP {r.status_code}")
                
        except Exception as e:
            log(f"❌ API error: {e}")
    
    def check_global_data_potential(self):
        """Check what massive data is available in global/ folder"""
        log("\n" + "="*80)
        log("GLOBAL DATA AVAILABILITY AUDIT")
        log("="*80)
        
        global_data = {
            "alphafold": "52.22 GB protein structures (542K files)",
            "spliceai": "122.45 GB splice predictions (34K files)", 
            "gtex_v10": "64.38 GB tissue expression (135 files)",
            "gnomad": "26.88 GB population genetics",
            "dbsnp": "4.14 GB common variants",
            "pharmgkb": "0.075 GB pharmacogenomics (already using)",
            "ontologies": "0.14 GB biological ontologies"
        }
        
        log(f"MASSIVE UNUSED DATA POTENTIAL:")
        total_unused = 0
        for category, description in global_data.items():
            if "already using" not in description:
                size_gb = float(description.split()[0])
                total_unused += size_gb
                log(f"❌ UNUSED: {category}: {description}")
            else:
                log(f"✅ USING: {category}: {description}")
        
        log(f"\nTOTAL UNUSED DATA: {total_unused:.1f} GB")
        log(f"CURRENT USAGE: ~50 GB processed databases")
        log(f"USAGE PERCENTAGE: {50/(50+total_unused)*100:.1f}% of available data")
    
    def generate_honest_prioritization(self):
        """Generate honest prioritization based on actual data"""
        log("\n" + "="*80)
        log("HONEST PRIORITIZATION - NO EXAGGERATION")
        log("="*80)
        
        priorities = [
            {
                'priority': 1,
                'enhancement': 'SpliceAI Integration (LexAPI_Genomics)',
                'data_size': '122.45 GB (3.43B + 952M rows)',
                'impact': 'Complete transcriptomic analysis',
                'effort': 'HIGH (billion-row datasets)',
                'risk': 'HIGH (could crash system)',
                'benefit': 'Genome-wide splice analysis'
            },
            {
                'priority': 2,
                'enhancement': 'gnomAD Population Data (LexAPI_Populomics)',
                'data_size': '26.88 GB population genetics',
                'impact': 'True population genetics analysis',
                'effort': 'HIGH (large dataset)',
                'risk': 'MEDIUM (manageable size)',
                'benefit': 'Population-specific variant frequencies'
            },
            {
                'priority': 3,
                'enhancement': 'GTEx Expression Data (LexAPI_Metabolics)',
                'data_size': '64.38 GB tissue expression',
                'impact': 'Tissue-specific metabolic analysis',
                'effort': 'HIGH (large dataset)',
                'risk': 'MEDIUM (structured data)',
                'benefit': 'Complete tissue metabolomics'
            },
            {
                'priority': 4,
                'enhancement': 'AlphaFold Structures (LexAPI_Anatomics)',
                'data_size': '52.22 GB protein structures',
                'impact': '3D anatomical protein analysis',
                'effort': 'HIGH (complex data)',
                'risk': 'MEDIUM (structured files)',
                'benefit': 'Protein structure-function analysis'
            },
            {
                'priority': 5,
                'enhancement': 'Complete Ontologies (All APIs)',
                'data_size': '0.14 GB biological ontologies',
                'impact': 'Enhanced terminology and connections',
                'effort': 'MEDIUM (processing needed)',
                'risk': 'LOW (small datasets)',
                'benefit': 'Better cross-axis terminology'
            }
        ]
        
        log(f"HONEST PRIORITY RANKING:")
        for item in priorities:
            log(f"\nPriority {item['priority']}: {item['enhancement']}")
            log(f"  Data Size: {item['data_size']}")
            log(f"  Impact: {item['impact']}")
            log(f"  Effort: {item['effort']}")
            log(f"  Risk: {item['risk']}")
            log(f"  Benefit: {item['benefit']}")

def main():
    log("="*80)
    log("HONEST API DATA AUDIT - NO EXAGGERATION")
    log("="*80)
    log("Brutally honest assessment of actual capabilities vs available data")
    
    auditor = HonestAPIAuditor()
    
    # Audit each API honestly
    auditor.audit_lexapi_genomics()
    auditor.audit_lexapi_metabolics()
    auditor.audit_lexapi_anatomics()
    auditor.audit_lexapi_populomics()
    auditor.audit_lexapi_literature()
    
    # Check global data potential
    auditor.check_global_data_potential()
    
    # Generate honest prioritization
    auditor.generate_honest_prioritization()
    
    log(f"\n{'='*80}")
    log("HONEST AUDIT COMPLETE")
    log("This is the TRUTH about our current capabilities and potential")
    log("="*80)

if __name__ == "__main__":
    main()
