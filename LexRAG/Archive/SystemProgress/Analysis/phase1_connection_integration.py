"""
Phase 1: Connection Tables Integration
Safely integrate critical connection tables for 7 Axes cross-axis analysis
"""

import duckdb
import time
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

class ConnectionTableIntegrator:
    def __init__(self):
        self.db_path = "../../data/databases/genomic_knowledge/genomic_knowledge.duckdb"
        self.connection_tables = {
            'gene_protein_mapping': 'biomart_protein_mapping',
            'variant_expression': 'gtex_v10_eqtl_associations', 
            'variant_splicing': 'gtex_v10_sqtl_associations',
            'gene_pathways': 'kegg_gene_pathway_links',
            'gene_symbols': 'ensembl_gene_symbol_mapping'
        }
        
    def analyze_connection_table(self, table_name):
        """Safely analyze a connection table"""
        log(f"Analyzing connection table: {table_name}")
        
        try:
            conn = duckdb.connect(self.db_path, read_only=True)
            
            # Basic info
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            columns = conn.execute(f"DESCRIBE {table_name}").fetchall()
            
            log(f"  Rows: {count:,}")
            log(f"  Columns: {len(columns)}")
            
            # Show column structure
            column_names = [col[0] for col in columns]
            log(f"  All columns: {column_names}")
            
            # Sample data to understand structure
            sample = conn.execute(f"SELECT * FROM {table_name} LIMIT 3").fetchall()
            log(f"  Sample data:")
            for i, row in enumerate(sample):
                log(f"    Row {i+1}: {row}")
            
            # Check for key connection columns
            connection_indicators = ['gene', 'variant', 'protein', 'tissue', 'pathway', 'uniprot', 'rsid']
            found_connections = []
            for col in column_names:
                for indicator in connection_indicators:
                    if indicator in col.lower():
                        found_connections.append(col)
                        break
            
            log(f"  Key connection columns: {found_connections}")
            
            conn.close()
            
            return {
                'table': table_name,
                'rows': count,
                'columns': column_names,
                'connections': found_connections,
                'sample_data': sample
            }
            
        except Exception as e:
            log(f"  ERROR analyzing {table_name}: {e}")
            return {'table': table_name, 'error': str(e)}
    
    def test_current_genomics_queries(self):
        """Test what LexAPI_Genomics currently queries to understand gaps"""
        log("\nTesting current LexAPI_Genomics query patterns")
        log("-" * 50)
        
        try:
            conn = duckdb.connect(self.db_path, read_only=True)
            
            # Test current BRCA2 analysis
            log("Testing current BRCA2 analysis:")
            
            # Current ClinVar query
            brca2_variants = conn.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN clinical_significance LIKE '%Pathogenic%' THEN 1 END) as pathogenic
                FROM clinvar_full_production
                WHERE gene_symbol = 'BRCA2'
            """).fetchone()
            
            log(f"  Current BRCA2 variants: {brca2_variants[0]:,} total, {brca2_variants[1]:,} pathogenic")
            
            # Test what connections we're missing
            log("\nTesting missing connections:")
            
            # Can we connect BRCA2 to proteins?
            try:
                brca2_proteins = conn.execute("""
                    SELECT COUNT(*) FROM biomart_protein_mapping
                    WHERE gene_symbol = 'BRCA2'
                """).fetchone()[0]
                log(f"  BRCA2 protein connections available: {brca2_proteins}")
            except:
                log(f"  BRCA2 protein connections: NOT ACCESSIBLE")
            
            # Can we connect BRCA2 to tissue expression?
            try:
                brca2_expression = conn.execute("""
                    SELECT COUNT(*) FROM gtex_v10_eqtl_associations
                    WHERE gene_symbol = 'BRCA2'
                """).fetchone()[0]
                log(f"  BRCA2 expression connections available: {brca2_expression}")
            except:
                log(f"  BRCA2 expression connections: NOT ACCESSIBLE")
            
            # Can we connect BRCA2 to pathways?
            try:
                brca2_pathways = conn.execute("""
                    SELECT COUNT(*) FROM kegg_gene_pathway_links
                    WHERE gene_symbol = 'BRCA2'
                """).fetchone()[0]
                log(f"  BRCA2 pathway connections available: {brca2_pathways}")
            except:
                log(f"  BRCA2 pathway connections: NOT ACCESSIBLE")
            
            conn.close()
            
        except Exception as e:
            log(f"ERROR testing current queries: {e}")
    
    def create_enhanced_query_examples(self):
        """Show what enhanced queries would look like with connection tables"""
        log("\nENHANCED QUERY EXAMPLES (after integration)")
        log("-" * 50)
        
        examples = [
            {
                'name': 'Complete BRCA2 Analysis',
                'description': 'Gene + Variants + Proteins + Expression + Pathways',
                'tables_needed': ['clinvar_full_production', 'biomart_protein_mapping', 'gtex_v10_eqtl_associations', 'kegg_gene_pathway_links'],
                'query': '''
                -- Complete BRCA2 analysis across all axes
                SELECT 
                    cv.gene_symbol,
                    COUNT(DISTINCT cv.rsid) as total_variants,
                    COUNT(DISTINCT bpm.protein_id) as connected_proteins,
                    COUNT(DISTINCT geqtl.tissue_type) as expression_tissues,
                    COUNT(DISTINCT kgpl.pathway_id) as involved_pathways
                FROM clinvar_full_production cv
                LEFT JOIN biomart_protein_mapping bpm ON cv.gene_symbol = bpm.gene_symbol
                LEFT JOIN gtex_v10_eqtl_associations geqtl ON cv.gene_symbol = geqtl.gene_symbol
                LEFT JOIN kegg_gene_pathway_links kgpl ON cv.gene_symbol = kgpl.gene_symbol
                WHERE cv.gene_symbol = 'BRCA2'
                '''
            },
            {
                'name': 'Variant Cross-Axis Impact',
                'description': 'Variant + Clinical + Expression + Splicing + Protein',
                'tables_needed': ['clinvar_full_production', 'gtex_v10_eqtl_associations', 'gtex_v10_sqtl_associations', 'alphafold_clinical_variant_impact'],
                'query': '''
                -- Complete variant impact analysis
                SELECT 
                    cv.rsid,
                    cv.clinical_significance,
                    COUNT(DISTINCT geqtl.tissue_type) as expression_tissues,
                    COUNT(DISTINCT gsqtl.tissue_type) as splicing_tissues,
                    COUNT(DISTINCT afcvi.protein_name) as affected_proteins
                FROM clinvar_full_production cv
                LEFT JOIN gtex_v10_eqtl_associations geqtl ON cv.rsid = geqtl.variant_id
                LEFT JOIN gtex_v10_sqtl_associations gsqtl ON cv.rsid = gsqtl.variant_id  
                LEFT JOIN alphafold_clinical_variant_impact afcvi ON cv.gene_symbol = afcvi.gene_symbol
                WHERE cv.rsid = 'rs7412'
                '''
            }
        ]
        
        for example in examples:
            log(f"\n{example['name']}:")
            log(f"  Purpose: {example['description']}")
            log(f"  Tables needed: {', '.join(example['tables_needed'])}")
            log(f"  Enhanced capability: True cross-axis analysis")
    
    def create_integration_priority_list(self):
        """Create prioritized list for integration"""
        log("\nINTEGRATION PRIORITY LIST")
        log("-" * 50)
        
        priorities = [
            {
                'priority': 1,
                'table': 'biomart_protein_mapping',
                'purpose': 'Gene → Protein connections (Axis 2 → Axis 4)',
                'impact': 'Enable protein analysis for any gene',
                'size': '245K rows',
                'risk': 'LOW'
            },
            {
                'priority': 2, 
                'table': 'kegg_gene_pathway_links',
                'purpose': 'Gene → Pathway connections (Axis 2 → Axis 5)',
                'impact': 'Enable metabolic pathway analysis',
                'size': '854 rows',
                'risk': 'LOW'
            },
            {
                'priority': 3,
                'table': 'gtex_v10_eqtl_associations', 
                'purpose': 'Variant → Expression connections (Axis 2 → Axis 3)',
                'impact': 'Tissue-specific variant effects',
                'size': '405K rows',
                'risk': 'LOW'
            },
            {
                'priority': 4,
                'table': 'gtex_v10_sqtl_associations',
                'purpose': 'Variant → Splicing connections (Axis 2 → Axis 3)',
                'impact': 'Splicing variant analysis',
                'size': '1.4M rows',
                'risk': 'MEDIUM'
            },
            {
                'priority': 5,
                'table': 'alphafold_clinical_variant_impact',
                'purpose': 'Variant → Protein structure (Axis 2 → Axis 4)',
                'impact': 'Protein structure analysis',
                'size': '11.6M rows',
                'risk': 'MEDIUM'
            }
        ]
        
        for item in priorities:
            log(f"Priority {item['priority']}: {item['table']}")
            log(f"  Purpose: {item['purpose']}")
            log(f"  Impact: {item['impact']}")
            log(f"  Size: {item['size']}")
            log(f"  Risk: {item['risk']}")
            log("")

def main():
    log("="*80)
    log("PHASE 1: CONNECTION TABLES INTEGRATION ANALYSIS")
    log("="*80)
    log("Goal: Enable 7 Axes cross-axis analysis")
    
    integrator = ConnectionTableIntegrator()
    
    # Step 1: Analyze each connection table
    log("\nSTEP 1: Analyzing connection tables")
    for purpose, table_name in integrator.connection_tables.items():
        log(f"\n--- {purpose.upper()} ---")
        result = integrator.analyze_connection_table(table_name)
        time.sleep(1)  # Prevent CPU overload
    
    # Step 2: Test current query gaps
    integrator.test_current_genomics_queries()
    
    # Step 3: Show enhanced capabilities
    integrator.create_enhanced_query_examples()
    
    # Step 4: Create integration priority
    integrator.create_integration_priority_list()
    
    log("\n" + "="*80)
    log("PHASE 1 ANALYSIS COMPLETE")
    log("Ready to begin connection table integration")
    log("="*80)

if __name__ == "__main__":
    main()
