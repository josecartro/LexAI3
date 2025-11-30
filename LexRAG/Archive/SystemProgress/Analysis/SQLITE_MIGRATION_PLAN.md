# SQLite Migration Plan - Complete Implementation Strategy

**Goal:** Test and migrate to SQLite for <1s API responses  
**Current Problem:** DuckDB JOINs take 1-15s (too slow)  
**Target:** SQLite queries <0.5s for real-time health APIs

---

## PHASE 1: SQLITE PERFORMANCE TEST

### **Test Database Location:**
```
LexRAG/
├── data/
│   ├── sqlite_test/                    # NEW - SQLite test databases
│   │   ├── genomics_test.sqlite        # Test genomics data
│   │   ├── metabolics_test.sqlite      # Test metabolics data
│   │   └── test_results.md             # Performance comparison results
│   └── databases/                      # KEEP - Original DuckDB data
│       └── genomic_knowledge/
│           └── genomic_knowledge.duckdb # Source data
```

### **Test Data Sample Selection:**

#### **1. Genomics Test Database (genomics_test.sqlite):**
**Tables to create:**
```sql
-- Genes table (master reference)
CREATE TABLE genes (
    gene_symbol TEXT PRIMARY KEY,
    gene_id TEXT,
    chromosome TEXT,
    total_variants INTEGER,
    pathogenic_variants INTEGER
);

-- Variants table (clinical focus)  
CREATE TABLE variants (
    rsid TEXT PRIMARY KEY,
    gene_symbol TEXT,
    chromosome TEXT,
    position BIGINT,
    ref_allele TEXT,
    alt_allele TEXT,
    clinical_significance TEXT,
    disease_name TEXT,
    pathogenicity_score REAL,
    FOREIGN KEY (gene_symbol) REFERENCES genes(gene_symbol)
);

-- Protein connections
CREATE TABLE protein_connections (
    protein_id TEXT,
    gene_symbol TEXT,
    transcript_id TEXT,
    uniprot_id TEXT,
    source TEXT,
    FOREIGN KEY (gene_symbol) REFERENCES genes(gene_symbol)
);

-- Splice predictions (high-impact subset)
CREATE TABLE splice_predictions (
    variant_id TEXT,
    gene_symbol TEXT,
    chromosome TEXT,
    position BIGINT,
    acceptor_gain REAL,
    acceptor_loss REAL,
    donor_gain REAL,
    donor_loss REAL,
    max_score REAL,
    FOREIGN KEY (gene_symbol) REFERENCES genes(gene_symbol)
);
```

**Sample Data to Include:**
- **20 important genes:** BRCA1, BRCA2, TP53, CFTR, APOE, EGFR, KRAS, etc.
- **~50K variants:** All variants for these 20 genes
- **~5K protein connections:** Protein mappings for these genes
- **~500K splice predictions:** High-impact splice data for these genes

**Total size:** ~100MB (vs 48GB DuckDB) - very manageable

#### **2. Metabolics Test Database (metabolics_test.sqlite):**
```sql
-- Drug interactions
CREATE TABLE drug_interactions (
    drug_name TEXT,
    gene_symbol TEXT,
    interaction_type TEXT,
    clinical_significance TEXT,
    dosing_recommendation TEXT,
    evidence_level TEXT
);

-- Pharmacogenomic variants
CREATE TABLE pharmaco_variants (
    rsid TEXT,
    gene_symbol TEXT,
    drug_effect TEXT,
    population_frequency REAL
);
```

**Sample Data:**
- **All PharmGKB data:** ~1K drug-gene interactions
- **CYP450 variants:** All pharmacogenomic variants
- **Total size:** ~10MB

---

## PHASE 2: PERFORMANCE TESTING

### **Test Queries to Compare:**

#### **DuckDB Current Queries:**
```sql
-- Test 1: Simple gene lookup
SELECT * FROM clinvar_full_production WHERE gene_symbol = 'BRCA2';

-- Test 2: Complex JOIN
SELECT cv.rsid, cv.clinical_significance, sp.max_score
FROM clinvar_full_production cv
JOIN spliceai_practical sp ON cv.gene_symbol = sp.gene_symbol
WHERE cv.gene_symbol = 'BRCA2';

-- Test 3: Multi-table analysis
SELECT cv.gene_symbol, COUNT(cv.rsid), COUNT(sp.variant_id), COUNT(pm.protein_id)
FROM clinvar_full_production cv
LEFT JOIN spliceai_practical sp ON cv.gene_symbol = sp.gene_symbol  
LEFT JOIN biomart_protein_mapping pm ON cv.gene_symbol = pm.gene_symbol
WHERE cv.gene_symbol IN ('BRCA1', 'BRCA2', 'TP53')
GROUP BY cv.gene_symbol;
```

#### **SQLite Test Queries (Same Logic):**
```sql
-- Test 1: Simple gene lookup
SELECT * FROM variants WHERE gene_symbol = 'BRCA2';

-- Test 2: Complex JOIN  
SELECT v.rsid, v.clinical_significance, sp.max_score
FROM variants v
JOIN splice_predictions sp ON v.gene_symbol = sp.gene_symbol
WHERE v.gene_symbol = 'BRCA2';

-- Test 3: Multi-table analysis
SELECT g.gene_symbol, COUNT(v.rsid), COUNT(sp.variant_id), COUNT(pc.protein_id)
FROM genes g
LEFT JOIN variants v ON g.gene_symbol = v.gene_symbol
LEFT JOIN splice_predictions sp ON g.gene_symbol = sp.gene_symbol
LEFT JOIN protein_connections pc ON g.gene_symbol = pc.gene_symbol
WHERE g.gene_symbol IN ('BRCA1', 'BRCA2', 'TP53')
GROUP BY g.gene_symbol;
```

### **Performance Metrics to Measure:**
- **Query execution time** (target: <0.1s)
- **JOIN performance** (target: <0.5s)
- **API response time** (target: <1s)
- **Memory usage** during queries
- **Concurrent query handling**

---

## PHASE 3: MIGRATION STRATEGY (IF TEST SUCCEEDS)

### **Hot Data Migration (Week 1):**
**Move to SQLite:**
- **variants_clinical:** 174K pathogenic variants
- **spliceai_practical:** 26M splice predictions (or subset)
- **biomart_protein_mapping:** 245K protein connections
- **gtex_v10_eqtl_associations:** 405K expression effects
- **pharmgkb drug interactions:** All drug-gene data

**Database Organization:**
```
data/sqlite/
├── genomics.sqlite          # Variants, genes, splice predictions
├── proteins.sqlite          # Protein structures, connections
├── expression.sqlite        # GTEx expression, tissue data
├── drugs.sqlite            # PharmGKB, drug interactions
└── population.sqlite       # Population genetics, frequencies
```

### **Cold Data (Keep in DuckDB):**
- **Original massive tables** (3.43B SpliceAI, full AlphaFold)
- **Bulk analysis data** (full population genetics)
- **Research datasets** (complete ontologies)

### **API Updates:**
```python
# New SQLite connections (fast)
genomics_db = sqlite3.connect("data/sqlite/genomics.sqlite")
proteins_db = sqlite3.connect("data/sqlite/proteins.sqlite")

# DuckDB for deep analysis (when needed)
analysis_db = duckdb.connect("data/databases/genomic_knowledge/genomic_knowledge.duckdb")
```

---

## IMPLEMENTATION TIMELINE

### **Day 1: Create Test Databases**
- Extract 20 important genes from DuckDB
- Create SQLite test databases
- Import sample data with proper indexes

### **Day 2: Performance Testing**
- Run identical queries on DuckDB vs SQLite
- Measure response times, memory usage
- Test concurrent API calls

### **Day 3: API Integration Test**
- Update one API endpoint to use SQLite
- Test real API performance improvement
- Measure end-to-end response times

### **Day 4-5: Full Migration (If Successful)**
- Migrate all hot data to SQLite
- Update all APIs to use SQLite for real-time queries
- Keep DuckDB for research/analysis queries

### **Day 6-7: Testing & Optimization**
- Run enhanced 35-question benchmark
- Optimize SQLite indexes
- Fine-tune performance

---

## SUCCESS METRICS

### **Performance Targets:**
- **Simple lookups:** <0.01s (vs current 0.005s)
- **JOIN queries:** <0.1s (vs current 1.8s)
- **API responses:** <1s (vs current 7-15s)
- **Benchmark score:** 85%+ (vs current 75.7%)

### **Test Success Criteria:**
- **SQLite 5x+ faster** than DuckDB for JOINs
- **API responses <3s** consistently
- **System stability** maintained
- **All enhanced features** working

---

## RISK MITIGATION

### **Backup Strategy:**
- **Keep all DuckDB data** as backup
- **Test with copies** - don't modify originals
- **Rollback plan** if SQLite doesn't perform

### **Gradual Migration:**
- **Test one API first** (LexAPI_Genomics)
- **Migrate incrementally** if successful
- **Keep DuckDB running** during transition

---

**IMMEDIATE NEXT STEP:** Create SQLite test database with 20 important genes and compare performance vs DuckDB.

**Expected outcome:** 10x faster API responses enabling real-time health analysis.
