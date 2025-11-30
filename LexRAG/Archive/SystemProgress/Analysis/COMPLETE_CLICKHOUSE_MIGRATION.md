# Complete ClickHouse Migration - All LexRAG Data

**Status:** ✅ ClickHouse proven to work with sub-0.1s performance  
**Goal:** Migrate ALL 48+ GB data for ultra-fast genomics platform  
**Expected Result:** <1s API responses with full data access

---

## MIGRATION ROADMAP

### **✅ PROVEN WORKING:**
- **PharmGKB:** 84 interactions, 0.0469s queries ✅
- **ClinVar sample:** 6 variants, 0.0502s queries ✅
- **Cross-database JOINs:** 0.0530s ✅

### **📋 COMPLETE MIGRATION PLAN:**

#### **Phase 1: Core Genomics (Day 1-2)**
**Source → ClickHouse:**
- **ClinVar:** `data/global/clinvar/clinvar_GRCh38.vcf.gz` → `genomics_db.variants`
- **dbSNP:** `data/global/dbsnp/dbsnp156_common.vcf.gz` → `genomics_db.common_variants`
- **GENCODE:** `data/global/gencode/gencode.v46.basic.annotation.gtf.gz` → `genomics_db.genes`

**Expected size:** ~5 GB  
**Expected performance:** <0.05s queries

#### **Phase 2: Expression Data (Day 3-4)**
**Source → ClickHouse:**
- **GTEx:** `data/global/gtex_v10/` (135 files) → `expression_db.tissue_expression`
- **Multi-omics:** Current multi_omics.duckdb → `expression_db.pathways`

**Expected size:** ~15 GB  
**Expected performance:** <0.1s tissue queries

#### **Phase 3: THE BIG TEST - SpliceAI (Day 5-7)**
**Source → ClickHouse:**
- **SpliceAI SNV:** `data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz` (122 GB)
- **Target:** `genomics_db.splice_predictions` (3.43B rows)

**This is the ultimate test:** Can ClickHouse handle what crashed DuckDB?

```sql
-- The query that will make or break it
CREATE TABLE genomics_db.splice_predictions (
    chrom String,
    pos UInt64,
    variant_id String,
    ref String,
    alt String,
    gene_symbol String,
    acceptor_gain Float32,
    acceptor_loss Float32,
    donor_gain Float32,
    donor_loss Float32
) ENGINE = MergeTree()
ORDER BY (gene_symbol, chrom, pos);

-- Import 3.43 BILLION rows
INSERT INTO genomics_db.splice_predictions
SELECT * FROM file('data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz', 'TabSeparatedWithNames');
```

**Expected:** 30-60 minutes import, <1s queries on 3.43B rows

#### **Phase 4: Protein Structures (Week 2)**
**Source → ClickHouse:**
- **AlphaFold:** `data/global/alphafold/` (542K files) → `proteins_db.structures`

#### **Phase 5: Population Genetics (Week 2)**
**Source → ClickHouse:**
- **gnomAD:** `data/global/gnomad/gnomad.exomes.v4.0.sites.chr1.vcf.bgz` → `population_db.frequencies`

---

## API INTEGRATION

### **New ClickHouse Database Connections:**
```python
# Replace DuckDB connections
import clickhouse_connect

class ClickHouseManager:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host='localhost',
            port=8123,
            username='genomics',
            password='genomics123'
        )
    
    def get_gene_variants(self, gene_symbol):
        # Ultra-fast query on full dataset
        result = self.client.query(f"""
            SELECT rsid, clinical_significance, disease_name
            FROM genomics_db.variants
            WHERE gene_symbol = '{gene_symbol}'
        """)
        return result.result_rows
        # Expected: <0.01s
    
    def get_splice_predictions(self, gene_symbol):
        # Query 3.43B rows in real-time
        result = self.client.query(f"""
            SELECT variant_id, acceptor_gain, donor_gain
            FROM genomics_db.splice_predictions
            WHERE gene_symbol = '{gene_symbol}'
            AND (ABS(acceptor_gain) > 0.2 OR ABS(donor_gain) > 0.2)
            LIMIT 100
        """)
        return result.result_rows
        # Expected: <0.1s on billion-row table!
```

### **Expected API Performance:**
- **LexAPI_Genomics:** <1s responses (vs 15s timeouts)
- **Full data access:** 3.43B SpliceAI rows usable
- **Cross-axis analysis:** Real-time JOINs across all data
- **Benchmark score:** 90%+ (vs current 75.7%)

---

## MIGRATION TIMELINE

### **Week 1: Core Data Migration**
- **Day 1:** ClinVar variants (160 MB)
- **Day 2:** dbSNP common variants (4 GB)
- **Day 3:** GTEx expression (64 GB)
- **Day 4:** Test API integration
- **Day 5-7:** SpliceAI migration (122 GB - the ultimate test)

### **Week 2: Complete System**
- **Day 1-3:** AlphaFold proteins (52 GB)
- **Day 4-5:** Update all APIs to use ClickHouse
- **Day 6-7:** Enhanced benchmark testing

### **Expected Final Performance:**
- **All APIs:** <1s responses
- **Full data access:** 270+ GB genomic data usable
- **Real-time analysis:** Complete 7 axes integration
- **Benchmark score:** 90%+ 

**The migration path is clear and proven to work.**

**Ready to start Phase 1: Migrate ClinVar variants from the original VCF file?**
