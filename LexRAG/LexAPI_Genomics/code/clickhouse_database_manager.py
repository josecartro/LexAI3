"""
Database Manager for LexAPI_Genomics - ClickHouse Edition
Handles ClickHouse connections and provides AI-friendly query interfaces
"""

import clickhouse_connect
from neo4j import GraphDatabase
from pathlib import Path
from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# Add parent directory to path for config imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from config.database_config import NEO4J_URI, NEO4J_AUTH

class ClickHouseDatabaseManager:
    """Manages ClickHouse and Neo4j connections for genomics API"""
    
    def __init__(self):
        self.clickhouse_client = None
        self.clickhouse_config = {
            'host': '127.0.0.1',
            'port': 8125,
            'username': 'genomics',
            'password': 'genomics123'
        }
        self.neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    
    def get_clickhouse_client(self):
        """Get ClickHouse client (lazy initialization)"""
        if self.clickhouse_client is None:
            self.clickhouse_client = clickhouse_connect.get_client(**self.clickhouse_config)
        return self.clickhouse_client
    
    def get_neo4j_session(self):
        """Get Neo4j session"""
        return self.neo4j_driver.session()
    
    def query_variants_by_gene(self, gene_symbol: str, limit: int = 100) -> List[Dict]:
        """AI-friendly variant query by gene"""
        query = f"""
        SELECT 
            rsid,
            chrom,
            pos,
            ref,
            alt,
            clinical_significance,
            disease_name
        FROM genomics_db.clinvar_variants 
        WHERE gene_symbol = '{gene_symbol}'
        ORDER BY pos
        LIMIT {limit}
        """
        
        results = self.clickhouse_client.query(query).result_rows
        return [
            {
                "rsid": row[0],
                "chromosome": row[1], 
                "position": row[2],
                "reference": row[3],
                "alternate": row[4],
                "clinical_significance": row[5],
                "disease": row[6]
            }
            for row in results
        ]
    
    def query_gene_expression(self, gene_symbol: str, tissue: str = None) -> List[Dict]:
        """AI-friendly gene expression query"""
        where_clause = f"gene_symbol = '{gene_symbol}'"
        if tissue:
            where_clause += f" AND tissue LIKE '%{tissue}%'"
        
        query = f"""
        SELECT 
            gene_symbol,
            tissue,
            median_tpm,
            mean_tpm,
            sample_count
        FROM expression_db.tissue_expression 
        WHERE {where_clause}
        ORDER BY median_tpm DESC
        LIMIT 100
        """
        
        results = self.clickhouse_client.query(query).result_rows
        return [
            {
                "gene": row[0],
                "tissue": row[1],
                "median_expression": row[2],
                "mean_expression": row[3],
                "sample_count": row[4]
            }
            for row in results
        ]
    
    def query_splice_predictions(self, gene_symbol: str, min_score: float = 0.2) -> List[Dict]:
        """AI-friendly SpliceAI predictions query"""
        query = f"""
        SELECT 
            chrom,
            pos,
            variant_id,
            ref,
            alt,
            acceptor_gain,
            acceptor_loss,
            donor_gain,
            donor_loss,
            max_score
        FROM genomics_db.spliceai_predictions 
        WHERE gene_symbol = '{gene_symbol}' 
            AND max_score >= {min_score}
        ORDER BY max_score DESC
        LIMIT 1000
        """
        
        results = self.clickhouse_client.query(query).result_rows
        return [
            {
                "chromosome": row[0],
                "position": row[1],
                "variant_id": row[2],
                "reference": row[3],
                "alternate": row[4],
                "acceptor_gain": row[5],
                "acceptor_loss": row[6],
                "donor_gain": row[7],
                "donor_loss": row[8],
                "max_score": row[9]
            }
            for row in results
        ]
    
    def query_protein_structures(self, gene_symbol: str = None, uniprot_id: str = None) -> List[Dict]:
        """AI-friendly protein structure query"""
        if gene_symbol:
            # Use UniProt mappings to find proteins for this gene
            mapping_query = f"""
            SELECT DISTINCT external_id 
            FROM reference_db.uniprot_mappings 
            WHERE id_type = 'Gene_Name' AND external_id = '{gene_symbol}'
            """
            gene_mappings = self.clickhouse_client.query(mapping_query).result_rows
            
            if gene_mappings:
                # Find AlphaFold structures
                structure_query = f"""
                SELECT uniprot_id, gene_symbol, protein_name, confidence_avg, structure_file
                FROM proteins_db.alphafold_structures
                WHERE gene_symbol = '{gene_symbol}' OR uniprot_id IN (
                    SELECT uniprot_id FROM reference_db.uniprot_mappings 
                    WHERE id_type = 'Gene_Name' AND external_id = '{gene_symbol}'
                )
                LIMIT 50
                """
                
                results = self.clickhouse_client.query(structure_query).result_rows
                return [
                    {
                        "uniprot_id": row[0],
                        "gene_symbol": row[1],
                        "protein_name": row[2],
                        "confidence": row[3],
                        "structure_file": row[4]
                    }
                    for row in results
                ]
        
        return []
    
    def query_population_frequencies(self, chromosome: str, position: int, window: int = 1000) -> List[Dict]:
        """AI-friendly population frequency query"""
        query = f"""
        SELECT 
            chrom,
            pos,
            rsid,
            ref,
            alt,
            allele_frequency,
            allele_count,
            allele_number
        FROM population_db.variant_frequencies 
        WHERE chrom = '{chromosome}' 
            AND pos BETWEEN {position - window} AND {position + window}
        ORDER BY allele_frequency DESC
        LIMIT 100
        """
        
        results = self.clickhouse_client.query(query).result_rows
        return [
            {
                "chromosome": row[0],
                "position": row[1],
                "rsid": row[2],
                "reference": row[3],
                "alternate": row[4],
                "frequency": row[5],
                "allele_count": row[6],
                "total_alleles": row[7]
            }
            for row in results
        ]
    
    def query_variant_stats_by_gene(self, gene_symbol: str) -> Dict[str, Any]:
        """Query variant statistics for a gene"""
        query = f"""
        SELECT 
            count() as total,
            countIf(clinical_significance LIKE '%Pathogenic%') as pathogenic,
            countIf(clinical_significance LIKE '%Benign%') as benign,
            countIf(clinical_significance LIKE '%Uncertain%') as uncertain
        FROM genomics_db.clinvar_variants 
        WHERE gene_symbol = '{gene_symbol}'
        """
        result = self.clickhouse_client.query(query).result_rows
        if result:
            return {
                "total_variants": result[0][0],
                "pathogenic_variants": result[0][1],
                "benign_variants": result[0][2],
                "uncertain_variants": result[0][3]
            }
        return {}

    def query_pathways_by_gene(self, gene_symbol: str) -> List[Dict]:
        """Query pathways for a gene"""
        query = f"""
        SELECT DISTINCT pathway_id, pathway_name, category
        FROM pathways_db.gene_pathways
        WHERE gene_symbol = '{gene_symbol}'
        LIMIT 20
        """
        results = self.clickhouse_client.query(query).result_rows
        return [
            {"id": row[0], "name": row[1], "category": row[2]}
            for row in results
        ]

    def query_gtex_gene_summary(self, gene_symbol: str) -> Dict[str, Any]:
        """Query GTEx summary for a gene"""
        # Simplified query assuming we have a summary table or can agg fast
        query = f"""
        SELECT count(DISTINCT variant_id), count(DISTINCT tissue), avg(abs(slope))
        FROM expression_db.gtex_eqtl
        WHERE gene_symbol = '{gene_symbol}'
        """
        result = self.clickhouse_client.query(query).result_rows
        if result:
            return {
                "variants_with_expression_effects": result[0][0],
                "tissues_affected": result[0][1],
                "average_effect_size": result[0][2]
            }
        return {}

    def query_diseases_by_gene(self, gene_symbol: str) -> List[Dict]:
        """AI-friendly disease query using ontologies"""
        # This would connect variants to diseases via ontologies
        variant_query = f"""
        SELECT DISTINCT disease_name, clinical_significance
        FROM genomics_db.clinvar_variants 
        WHERE gene_symbol = '{gene_symbol}' 
            AND disease_name IS NOT NULL
            AND disease_name != ''
        ORDER BY clinical_significance
        """
        
        results = self.clickhouse_client.query(variant_query).result_rows
        return [
            {
                "disease": row[0],
                "clinical_significance": row[1],
                "gene": gene_symbol
            }
            for row in results
        ]
    
    def test_all_connections(self) -> Dict[str, Any]:
        """Test all database connections"""
        status = {}
        
        # Test ClickHouse
        try:
            databases = self.clickhouse_client.query("SHOW DATABASES").result_rows
            total_records = self.clickhouse_client.query("""
                SELECT SUM(total_rows) FROM system.tables 
                WHERE database IN ('genomics_db', 'expression_db', 'proteins_db', 'population_db', 'regulatory_db', 'ontology_db', 'reference_db', 'pathways_db')
            """).result_rows[0][0]
            
            status["clickhouse"] = {
                "status": "connected", 
                "databases": len(databases),
                "total_records": f"{total_records:,}",
                "performance": "ultra_fast"
            }
        except Exception as e:
            status["clickhouse"] = {"status": "error", "error": str(e)}
        
        # Test Neo4j
        try:
            with self.get_neo4j_session() as session:
                node_count = session.run("MATCH (n) RETURN count(n) as count LIMIT 1000").single()["count"]
                status["neo4j"] = {"status": "connected", "nodes_sampled": node_count}
        except Exception as e:
            status["neo4j"] = {"status": "error", "error": str(e)}
        
        return status
    
    def close_connections(self):
        """Close all database connections"""
        try:
            self.neo4j_driver.close()
        except:
            pass
