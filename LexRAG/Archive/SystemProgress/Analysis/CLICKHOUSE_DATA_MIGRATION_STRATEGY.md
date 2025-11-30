# ClickHouse Data Migration Strategy

**Question:** Use processed DuckDB data or original source files from data/global/?  
**Answer:** Use original source files - cleaner, more reliable, avoid DuckDB issues

---

## MIGRATION SOURCE ANALYSIS

### **❌ PROBLEMS WITH DUCKDB AS SOURCE:**
- **DuckDB crashes** when reading massive tables
- **Memory issues** during data export
- **Corrupted queries** on 3.43B row tables
- **Complex dependencies** between processed tables
- **May have data quality issues** from processing

### **✅ ADVANTAGES OF ORIGINAL SOURCE FILES:**
- **Clean, raw data** - no processing artifacts
- **ClickHouse can read directly** from many formats
- **Parallel loading** - faster than DuckDB export
- **Data integrity** - original is always correct
- **Simpler pipeline** - source → ClickHouse (skip DuckDB)

---

## SOURCE DATA MAPPING

### **Original Files in data/global/ → ClickHouse Tables:**

#### **1. SpliceAI Data (122.45 GB):**
**Source:** `data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz`
**Target:** `genomics_db.spliceai_predictions`
**Method:** ClickHouse can read VCF files directly
```sql
-- ClickHouse VCF import (much faster than DuckDB)
CREATE TABLE genomics_db.spliceai_predictions (
    chrom String,
    pos UInt64,
    rsid String,
    ref String,
    alt String,
    gene_symbol String,
    acceptor_gain Float32,
    donor_gain Float32
) ENGINE = MergeTree()
ORDER BY (gene_symbol, chrom, pos);

-- Import directly from VCF
INSERT INTO genomics_db.spliceai_predictions 
SELECT * FROM file('data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz', 'TabSeparated');
```

#### **2. ClinVar Variants (0.16 GB):**
**Source:** `data/global/clinvar/clinvar_GRCh38.vcf.gz`
**Target:** `genomics_db.clinical_variants`
**Method:** Direct VCF import
```sql
CREATE TABLE genomics_db.clinical_variants (
    chrom String,
    pos UInt64,
    rsid String,
    ref String,
    alt String,
    clinical_significance String,
    gene_symbol String
) ENGINE = MergeTree()
ORDER BY (gene_symbol, rsid);
```

#### **3. GTEx Expression (64.38 GB):**
**Source:** `data/global/gtex_v10/` (135 files)
**Target:** `expression_db.tissue_expression`
**Method:** Batch import from TSV files
```sql
CREATE TABLE expression_db.tissue_expression (
    gene_id String,
    gene_symbol String,
    tissue_type String,
    expression_level Float32,
    sample_count UInt32
) ENGINE = MergeTree()
ORDER BY (gene_symbol, tissue_type);
```

#### **4. gnomAD Population (26.88 GB):**
**Source:** `data/global/gnomad/gnomad.exomes.v4.0.sites.chr1.vcf.bgz`
**Target:** `population_db.variant_frequencies`
**Method:** Direct VCF import

#### **5. AlphaFold Proteins (52.22 GB):**
**Source:** `data/global/alphafold/` (542K .gz files)
**Target:** `proteins_db.structures`
**Method:** Batch import from compressed files

#### **6. PharmGKB (0.075 GB):**
**Source:** `data/pharmgkb/*.zip` files
**Target:** `drugs_db.interactions`
**Method:** Extract and import CSV/JSON files

---

## CLICKHOUSE IMPORT ADVANTAGES

### **🚀 ClickHouse Import Features:**
- **Native VCF support:** Can read genomic VCF files directly
- **Parallel import:** Uses all CPU cores for loading
- **Compression:** Automatic compression during import
- **Schema detection:** Auto-detects column types
- **Error handling:** Continues on bad rows

### **📊 Expected Import Performance:**
**Current DuckDB ETL:** Hours/days for massive files  
**ClickHouse import:** Minutes for same files

**Example:**
```sql
-- Import 3.43B SpliceAI rows in ClickHouse (estimated 10-30 minutes)
INSERT INTO genomics_db.spliceai_predictions
SELECT * FROM file('data/global/spliceai/spliceai_scores.raw.snv.hg38.vcf.gz', 'TabSeparatedWithNames');
```

---

## MIGRATION IMPLEMENTATION

### **Phase 1: Test Migration (Day 1)**
**Start with smallest files:**
- **PharmGKB data** (75 MB) - test CSV import
- **ClinVar variants** (160 MB) - test VCF import
- **Verify performance** improvement

### **Phase 2: Medium Data (Day 2-3)**
- **GTEx expression** (64 GB) - test large file handling
- **gnomAD population** (27 GB) - test population data
- **Test API integration** with migrated data

### **Phase 3: Massive Data (Day 4-7)**
- **SpliceAI data** (122 GB) - the ultimate test
- **AlphaFold proteins** (52 GB) - protein structure data
- **Performance validation** on full dataset

### **Phase 4: API Integration (Week 2)**
- **Update all APIs** to use ClickHouse
- **Test enhanced performance**
- **Run final benchmark**

---

## IMPLEMENTATION COMMANDS

### **Install ClickHouse Python Client:**
```bash
pip install clickhouse-connect
```

### **Migration Script Structure:**
```python
import clickhouse_connect

# Connect to ClickHouse
client = clickhouse_connect.get_client(
    host='localhost', 
    port=8123,
    username='genomics',
    password='genomics123'
)

# Create database
client.command("CREATE DATABASE genomics_db")

# Import from original files (bypassing DuckDB)
client.command("""
    INSERT INTO genomics_db.variants
    SELECT * FROM file('data/global/clinvar/clinvar_GRCh38.vcf.gz', 'TabSeparated')
""")
```

---

## EXPECTED RESULTS

### **Performance:**
- **API responses:** <1s (vs current 7-15s)
- **3.43B row queries:** <1s (vs DuckDB crashes)
- **JOIN operations:** <0.1s (vs 15s)
- **Concurrent users:** 50+ (vs 1-2)

### **Capabilities:**
- **Full genomic analysis** finally possible
- **Real-time health insights** across all 7 axes
- **Complete transcriptomic analysis** with 3.43B predictions
- **Production-ready performance** on laptop

### **Data Quality:**
- **Original source data** - highest quality
- **No DuckDB artifacts** - clean import
- **Full dataset** - no compromises from memory limits

---

## RECOMMENDATION

**✅ USE ORIGINAL SOURCE FILES:**
- **Bypass DuckDB entirely** for problematic datasets
- **Direct import** from data/global/ folder
- **Cleaner, faster, more reliable**

**🎯 START WITH:** PharmGKB and ClinVar (small files) to test the approach

**Expected outcome:** Ultra-fast genomics platform with full data access for the first time.

**Ready to start migrating from original source files to ClickHouse?**
