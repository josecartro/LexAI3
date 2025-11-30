"""
Test Complete ClickHouse Database - All 7 Axes Data
Verify all migrated datasets are working and accessible
"""

import clickhouse_connect
import time
from pathlib import Path

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

class CompleteDatabaseTester:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
    
    def test_all_databases(self):
        """Test all databases and their key functionality"""
        log("🧪 TESTING COMPLETE CLICKHOUSE DATABASE")
        log("="*80)
        log("Testing all 7-axis data integration capabilities")
        log("="*80)
        
        tests = [
            ("Genomics Core", self.test_genomics_data),
            ("Expression Data", self.test_expression_data), 
            ("Population Genetics", self.test_population_data),
            ("Protein Structures", self.test_protein_data),
            ("Regulatory Elements", self.test_regulatory_data),
            ("Cross-Axis Integration", self.test_cross_axis_queries),
            ("Performance Benchmarks", self.test_performance)
        ]
        
        passed = 0
        total_start = time.time()
        
        for test_name, test_func in tests:
            log(f"\n🔬 TESTING: {test_name}")
            log("-" * 60)
            
            test_start = time.time()
            try:
                if test_func():
                    test_time = time.time() - test_start
                    passed += 1
                    log(f"✅ {test_name}: PASSED ({test_time:.3f}s)")
                else:
                    log(f"❌ {test_name}: FAILED")
            except Exception as e:
                log(f"❌ {test_name}: ERROR - {e}")
        
        total_time = time.time() - total_start
        
        log(f"\n{'='*80}")
        log("COMPLETE DATABASE TEST SUMMARY")
        log('='*80)
        log(f"Tests passed: {passed}/{len(tests)}")
        log(f"Total test time: {total_time:.1f}s")
        
        if passed >= 6:
            log("🎉 DATABASE READY: All major systems functional")
            log("🎯 Ready for 7-axis integration and API testing")
        else:
            log("⚠️  Some systems need attention")
    
    def test_genomics_data(self):
        """Test core genomics datasets"""
        log("Testing genomics datasets...")
        
        # Test ClinVar
        clinvar_count = self.client.query("SELECT COUNT(*) FROM genomics_db.clinvar_variants").result_rows[0][0]
        log(f"   ClinVar variants: {clinvar_count:,}")
        
        # Test dbSNP
        dbsnp_count = self.client.query("SELECT COUNT(*) FROM genomics_db.dbsnp_variants").result_rows[0][0]
        log(f"   dbSNP variants: {dbsnp_count:,}")
        
        # Test SpliceAI
        spliceai_count = self.client.query("SELECT COUNT(*) FROM genomics_db.spliceai_predictions").result_rows[0][0]
        log(f"   SpliceAI predictions: {spliceai_count:,}")
        
        # Test sample queries
        brca2_variants = self.client.query("SELECT COUNT(*) FROM genomics_db.clinvar_variants WHERE gene_symbol = 'BRCA2'").result_rows[0][0]
        log(f"   BRCA2 clinical variants: {brca2_variants}")
        
        return clinvar_count > 3000000 and dbsnp_count > 30000000 and spliceai_count > 3000000000
    
    def test_expression_data(self):
        """Test GTEx expression data"""
        log("Testing expression datasets...")
        
        gtex_count = self.client.query("SELECT COUNT(*) FROM expression_db.tissue_expression").result_rows[0][0]
        log(f"   GTEx expression records: {gtex_count:,}")
        
        # Test tissue-specific queries
        brain_expr = self.client.query("SELECT COUNT(*) FROM expression_db.tissue_expression WHERE tissue LIKE '%Brain%'").result_rows[0][0]
        log(f"   Brain tissue expressions: {brain_expr:,}")
        
        return gtex_count > 400000000
    
    def test_population_data(self):
        """Test gnomAD population data"""
        log("Testing population genetics...")
        
        gnomad_count = self.client.query("SELECT COUNT(*) FROM population_db.variant_frequencies").result_rows[0][0]
        log(f"   gnomAD population variants: {gnomad_count:,}")
        
        # Test frequency queries
        common_variants = self.client.query("SELECT COUNT(*) FROM population_db.variant_frequencies WHERE allele_frequency > 0.01").result_rows[0][0]
        log(f"   Common variants (>1%): {common_variants:,}")
        
        return gnomad_count > 15000000
    
    def test_protein_data(self):
        """Test AlphaFold protein structures"""
        log("Testing protein structure data...")
        
        alphafold_count = self.client.query("SELECT COUNT(*) FROM proteins_db.alphafold_structures").result_rows[0][0]
        log(f"   AlphaFold structures: {alphafold_count:,}")
        
        # Test UniProt queries
        sample_proteins = self.client.query("SELECT uniprot_id FROM proteins_db.alphafold_structures LIMIT 5").result_rows
        log(f"   Sample UniProt IDs: {[p[0] for p in sample_proteins]}")
        
        return alphafold_count > 500000
    
    def test_regulatory_data(self):
        """Test ENCODE regulatory elements"""
        log("Testing regulatory element data...")
        
        encode_count = self.client.query("SELECT COUNT(*) FROM regulatory_db.regulatory_elements").result_rows[0][0]
        log(f"   ENCODE regulatory elements: {encode_count:,}")
        
        # Test regulatory queries
        chr1_elements = self.client.query("SELECT COUNT(*) FROM regulatory_db.regulatory_elements WHERE chrom = '1'").result_rows[0][0]
        log(f"   Chromosome 1 elements: {chr1_elements:,}")
        
        return encode_count > 1000000
    
    def test_cross_axis_queries(self):
        """Test cross-database integration queries"""
        log("Testing cross-axis data integration...")
        
        # Test 1: Gene with clinical variants + expression data
        start_time = time.time()
        brca_query = """
        SELECT 
            c.gene_symbol,
            COUNT(c.rsid) as clinical_variants,
            COUNT(DISTINCT e.tissue) as tissues_expressed
        FROM genomics_db.clinvar_variants c
        LEFT JOIN expression_db.tissue_expression e ON c.gene_symbol = e.gene_symbol
        WHERE c.gene_symbol = 'BRCA1'
        GROUP BY c.gene_symbol
        """
        brca_result = self.client.query(brca_query).result_rows
        query1_time = time.time() - start_time
        
        if brca_result:
            gene, variants, tissues = brca_result[0]
            log(f"   BRCA1 integration: {variants} variants, {tissues} tissues ({query1_time:.3f}s)")
        
        # Test 2: Population frequency + splice predictions
        start_time = time.time()
        freq_splice_query = """
        SELECT COUNT(*) 
        FROM population_db.variant_frequencies p
        JOIN genomics_db.spliceai_predictions s ON p.chrom = s.chrom AND p.pos = s.pos
        WHERE p.allele_frequency > 0.01 AND s.max_score > 0.5
        LIMIT 1000
        """
        cross_result = self.client.query(freq_splice_query).result_rows[0][0]
        query2_time = time.time() - start_time
        
        log(f"   Cross-axis JOIN: {cross_result} records ({query2_time:.3f}s)")
        
        return query1_time < 1.0 and query2_time < 5.0
    
    def test_performance(self):
        """Test query performance benchmarks"""
        log("Testing query performance...")
        
        # Test 1: Simple lookup
        start_time = time.time()
        self.client.query("SELECT COUNT(*) FROM genomics_db.clinvar_variants WHERE gene_symbol = 'TP53'")
        simple_time = time.time() - start_time
        
        # Test 2: Complex aggregation
        start_time = time.time()
        self.client.query("SELECT gene_symbol, COUNT(*) FROM genomics_db.clinvar_variants GROUP BY gene_symbol LIMIT 100")
        agg_time = time.time() - start_time
        
        # Test 3: Large table scan
        start_time = time.time()
        self.client.query("SELECT COUNT(*) FROM genomics_db.spliceai_predictions WHERE max_score > 0.9 LIMIT 10000")
        scan_time = time.time() - start_time
        
        log(f"   Simple lookup: {simple_time:.3f}s")
        log(f"   Aggregation: {agg_time:.3f}s") 
        log(f"   Large scan: {scan_time:.3f}s")
        
        # All queries should be sub-second for ClickHouse
        return simple_time < 0.1 and agg_time < 0.5 and scan_time < 2.0

def main():
    log("="*80)
    log("🧪 COMPLETE DATABASE FUNCTIONALITY TEST")
    log("="*80)
    log("Testing all migrated datasets for 7-axis integration")
    log("Preparing for LexAPI connections and benchmark questions")
    log("="*80)
    
    tester = CompleteDatabaseTester()
    tester.test_all_databases()

if __name__ == "__main__":
    main()
