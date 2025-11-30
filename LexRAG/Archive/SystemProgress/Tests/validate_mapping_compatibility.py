"""
Validate DuckDB Mapping Tables vs ClickHouse Data
Check if the team's ID mappings are compatible and accurate
"""

import duckdb
import clickhouse_connect
from pathlib import Path

def log(msg):
    print(f"{msg}", flush=True)

def validate_mappings():
    """Compare DuckDB mappings with ClickHouse data"""
    log("🔍 VALIDATING MAPPING COMPATIBILITY")
    log("="*80)
    
    # Connect to both databases
    try:
        # DuckDB
        if not Path('data/databases/genomic_knowledge/genomic_knowledge.duckdb').exists():
            log("❌ DuckDB file not found")
            return False
            
        duck_conn = duckdb.connect('data/databases/genomic_knowledge/genomic_knowledge.duckdb', read_only=True)
        
        # ClickHouse
        ch_client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
        
        log("✅ Connected to both databases")
        
        # Test 1: Gene symbol consistency
        log("\n1. GENE SYMBOL CONSISTENCY CHECK:")
        log("-" * 40)
        
        # Get common genes from both
        duck_genes = set([row[0] for row in duck_conn.execute('SELECT DISTINCT gene_symbol FROM variants_clinical WHERE gene_symbol IS NOT NULL LIMIT 100').fetchall()])
        ch_genes = set([row[0] for row in ch_client.query('SELECT DISTINCT gene_symbol FROM genomics_db.clinvar_variants WHERE gene_symbol IS NOT NULL LIMIT 100').result_rows])
        
        common_genes = duck_genes.intersection(ch_genes)
        duck_only = duck_genes - ch_genes
        ch_only = ch_genes - duck_genes
        
        log(f"  Common genes: {len(common_genes)}")
        log(f"  DuckDB only: {len(duck_only)} {list(duck_only)[:3] if duck_only else ''}")
        log(f"  ClickHouse only: {len(ch_only)} {list(ch_only)[:3] if ch_only else ''}")
        
        compatibility_score = len(common_genes) / len(duck_genes.union(ch_genes)) * 100
        log(f"  Compatibility: {compatibility_score:.1f}%")
        
        # Test 2: Check mapping table quality
        log("\n2. MAPPING TABLE QUALITY:")
        log("-" * 40)
        
        try:
            # UniProt mappings
            uniprot_total = duck_conn.execute('SELECT COUNT(*) FROM uniprot_gene_mapping').fetchone()[0]
            uniprot_genes = duck_conn.execute('SELECT COUNT(DISTINCT gene_symbol) FROM uniprot_gene_mapping').fetchone()[0]
            
            log(f"  UniProt mappings: {uniprot_total:,} total, {uniprot_genes:,} unique genes")
            
            # Check for key genes
            key_genes = ['BRCA1', 'TP53', 'CFTR', 'APOE']
            for gene in key_genes:
                uniprot_ids = duck_conn.execute(f'SELECT uniprot_id FROM uniprot_gene_mapping WHERE gene_symbol = \"{gene}\"').fetchall()
                log(f"    {gene}: {len(uniprot_ids)} UniProt mappings")
                
        except Exception as e:
            log(f"  ❌ Error checking UniProt mappings: {e}")
        
        # Test 3: Variant position consistency
        log("\n3. VARIANT POSITION CONSISTENCY:")
        log("-" * 40)
        
        # Check if coordinates match between DuckDB and ClickHouse for same variants
        test_variants = [
            ('BRCA1', 'rs80357713'),
            ('TP53', 'rs11540654'),
            ('CFTR', 'rs113993960')
        ]
        
        for gene, rsid in test_variants:
            try:
                # DuckDB position
                duck_pos = duck_conn.execute(f'SELECT pos_bp FROM variants_clinical WHERE gene_symbol = \"{gene}\" AND rsid = \"{rsid}\" LIMIT 1').fetchall()
                
                # ClickHouse position
                ch_pos = ch_client.query(f'SELECT pos FROM genomics_db.clinvar_variants WHERE gene_symbol = \"{gene}\" AND rsid = \"{rsid}\" LIMIT 1').result_rows
                
                if duck_pos and ch_pos:
                    duck_position = duck_pos[0][0]
                    ch_position = ch_pos[0][0]
                    match = duck_position == ch_position
                    log(f"  {rsid} ({gene}): DuckDB={duck_position}, ClickHouse={ch_position} {'✅' if match else '❌'}")
                else:
                    log(f"  {rsid} ({gene}): Not found in one or both databases")
                    
            except Exception as e:
                log(f"  {rsid} ({gene}): Error - {e}")
        
        duck_conn.close()
        
        log("\n" + "="*80)
        log("VALIDATION SUMMARY:")
        
        if compatibility_score > 90:
            log("✅ HIGH COMPATIBILITY: DuckDB mappings should work with ClickHouse")
            log("✅ RECOMMENDATION: Migrate mapping tables from DuckDB")
        elif compatibility_score > 70:
            log("⚠️  MODERATE COMPATIBILITY: Some mappings may need adjustment")
            log("🔄 RECOMMENDATION: Migrate with validation checks")
        else:
            log("❌ LOW COMPATIBILITY: Build new mappings from scratch")
            log("🏗️  RECOMMENDATION: Use global data sources instead")
        
        return compatibility_score > 70
        
    except Exception as e:
        log(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    validate_mappings()
