# Data Architecture Rebuild Plan

**Problem:** 3.43B row monster tables are unusable giant spreadsheets  
**Solution:** Rebuild as properly structured, optimized database architecture  
**Goal:** Functional system that can actually use the massive data

---

## CURRENT ARCHITECTURE PROBLEMS

### **❌ GIANT SPREADSHEET APPROACH:**
- **spliceai_scores_production:** 3.43B rows in ONE table (unusable)
- **alphafold_clinical_variant_impact:** 11.6M rows as VIEW (unindexable)
- **Queries timeout** because we're scanning massive flat files
- **No logical data organization** by use case or frequency

### **❌ RESULT:**
- **APIs crash** when trying to access real data
- **Can't use 270+ GB** of available information
- **System becomes slower** instead of better with more data

---

## REBUILT ARCHITECTURE STRATEGY

### **🏗️ PRINCIPLE: SPLIT BY USAGE PATTERNS**

Instead of giant tables, create **purpose-built, optimized tables:**

#### **1. SPLICEAI ARCHITECTURE REBUILD:**

**Current:** 1 table with 3.43B rows (unusable)  
**Rebuild:** Multiple specialized tables by usage

```sql
-- High-impact variants only (clinically relevant)
CREATE TABLE spliceai_high_impact AS
SELECT * FROM spliceai_scores_production 
WHERE (ABS(acceptor_gain_score) > 0.5 OR ABS(donor_gain_score) > 0.5)
-- Result: ~50-100M rows (manageable)

-- By gene (most common lookup pattern)
CREATE TABLE spliceai_by_gene_brca1 AS  
SELECT * FROM spliceai_scores_production WHERE gene_symbol = 'BRCA1'
-- Result: ~10K-1M rows per gene (very fast)

-- By chromosome (genomic region analysis)
CREATE TABLE spliceai_chr1 AS
SELECT * FROM spliceai_scores_production WHERE chrom = '1'
-- Result: ~150-300M rows per chromosome (manageable)

-- Common variants only (population analysis)
CREATE TABLE spliceai_common_variants AS
SELECT sp.* FROM spliceai_scores_production sp
JOIN dbsnp_parquet_production dp ON sp.variant_id = dp.rsid
WHERE dp.allele_frequency > 0.01
-- Result: Much smaller, focused dataset
```

#### **2. ALPHAFOLD ARCHITECTURE REBUILD:**

**Current:** VIEWs that can't be indexed (unusable)  
**Rebuild:** Materialized tables by protein/gene

```sql
-- High-confidence structures only
CREATE TABLE alphafold_high_confidence AS
SELECT * FROM alphafold_clinical_variant_impact 
WHERE structure_confidence_avg > 70
-- Result: High-quality data only

-- By gene family (related proteins)
CREATE TABLE alphafold_cancer_genes AS
SELECT * FROM alphafold_clinical_variant_impact
WHERE gene_symbol IN ('BRCA1', 'BRCA2', 'TP53', 'EGFR', ...)
-- Result: Disease-focused protein analysis

-- By tissue type (tissue-specific analysis)
CREATE TABLE alphafold_breast_tissue AS
SELECT * FROM alphafold_clinical_variant_impact
WHERE tissue_type LIKE '%breast%'
-- Result: Tissue-specific protein data
```

#### **3. GENOMIC DATA ARCHITECTURE REBUILD:**

**Current:** Mixed data in giant tables  
**Rebuild:** Organized by clinical relevance and frequency

```sql
-- Clinical variants (most important)
CREATE TABLE variants_clinical AS
SELECT * FROM clinvar_full_production
WHERE clinical_significance IN ('Pathogenic', 'Likely pathogenic')
-- Result: ~1M highly relevant variants

-- Common population variants (population analysis)
CREATE TABLE variants_common AS  
SELECT * FROM dbsnp_parquet_production
WHERE allele_frequency > 0.05
-- Result: ~5-10M common variants

-- Gene-specific tables (fast gene lookup)
CREATE TABLE variants_brca_genes AS
SELECT * FROM clinvar_full_production  
WHERE gene_symbol IN ('BRCA1', 'BRCA2')
-- Result: ~50K variants per gene family
```

---

## IMPLEMENTATION PLAN

### **Phase 1: Create Optimized Tables (Week 1)**
**Goal:** Split monster tables into usable pieces

#### **Day 1-2: SpliceAI Optimization**
- Create `spliceai_high_impact` (high scores only)
- Create `spliceai_common_genes` (frequently queried genes)
- Test query performance improvement

#### **Day 3-4: AlphaFold Optimization**  
- Materialize VIEWs into base tables
- Create `alphafold_disease_genes` (cancer/disease focus)
- Create `alphafold_high_confidence` (reliable structures only)

#### **Day 5-7: Genomic Data Optimization**
- Create `variants_clinical` (pathogenic variants only)
- Create `variants_pharmacogenomic` (drug-related variants)
- Test integrated performance

### **Phase 2: Index Optimized Tables (Week 2)**
**Goal:** Index the smaller, manageable tables

#### **Indexing Strategy:**
```sql
-- These will work because tables are manageable size
CREATE INDEX idx_splice_high_gene ON spliceai_high_impact(gene_symbol)
CREATE INDEX idx_splice_high_variant ON spliceai_high_impact(variant_id)
CREATE INDEX idx_alphafold_disease_gene ON alphafold_disease_genes(gene_symbol)
CREATE INDEX idx_variants_clinical_gene ON variants_clinical(gene_symbol)
```

### **Phase 3: Update APIs (Week 3)**
**Goal:** Connect APIs to optimized tables instead of monster tables

#### **API Query Updates:**
```python
# Instead of querying 3.43B row table:
# OLD: SELECT * FROM spliceai_scores_production WHERE gene_symbol = 'BRCA2'

# NEW: Query optimized table:
# SELECT * FROM spliceai_high_impact WHERE gene_symbol = 'BRCA2'  # Fast!
```

---

## EXPECTED BENEFITS

### **Performance Improvements:**
- **Query times:** Seconds instead of timeouts
- **Index creation:** Possible on manageable tables
- **System stability:** No more crashes from massive queries
- **Memory usage:** Reasonable instead of hitting limits

### **Functionality Improvements:**
- **APIs actually work** with enhanced data
- **Real cross-axis analysis** becomes possible
- **Benchmark scores improve** because queries succeed
- **Clinical relevance increases** with focused datasets

---

## RESOURCE REQUIREMENTS

### **Storage:**
- **Optimized tables:** ~20-30 GB (instead of unusable 270 GB)
- **Indexes:** ~5-10 GB additional
- **Total:** ~40 GB usable vs 270 GB unusable

### **Memory:**
- **Query memory:** 1-2 GB per query (instead of 25+ GB)
- **Index creation:** Possible with 8-12 GB
- **System stability:** Maintained throughout

---

## IMMEDIATE ACTION PLAN

**STEP 1:** Create optimized SpliceAI table (high-impact variants only)  
**STEP 2:** Test query performance improvement  
**STEP 3:** Create optimized AlphaFold tables  
**STEP 4:** Update LexAPI_Genomics to use optimized tables  
**STEP 5:** Test enhanced system performance

**OUTCOME:** Functional system that can actually use massive biological data for real health insights.

---

**Ready to start rebuilding with optimized, usable data architecture?**
