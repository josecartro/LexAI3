# LexRAG Data Integration Prioritization

**Goal:** Maximize benchmark improvement (74.3% → 90%+) with efficient data integration  
**Current Status:** Protein connections working (Priority 1 complete)

---

## PRIORITY RANKING (Impact vs Effort)

### 🥇 **PRIORITY 1: COMPLETED** ✅
**Gene→Protein Mapping (biomart_protein_mapping)**
- **Status:** ✅ INTEGRATED AND WORKING
- **Impact:** 19,886 genes with 245K protein connections
- **Result:** Axis 2 → Axis 4 cross-axis analysis enabled

---

### 🥇 **PRIORITY 2: CRITICAL - Variant→Expression (GTEx eQTL)**
**Table:** `gtex_v10_eqtl_associations` (405K rows)  
**Impact:** ⭐⭐⭐⭐⭐ MASSIVE - Enables tissue-specific variant analysis  
**Effort:** ⭐⭐ LOW - Data already processed and ready  
**Connection:** Axis 2 (Genomics) → Axis 3 (Transcriptomics)

**Why Priority 2:**
- **405K variant→expression connections** already processed
- **Tissue-specific analysis** - exactly what we need for health questions
- **Low risk** - manageable data size
- **High impact** - answers "How does variant X affect gene expression in tissue Y?"

**Example Enhancement:**
- **Before:** "rs7412 in APOE" → Basic variant info
- **After:** "rs7412 in APOE" → Variant info + tissue expression effects + clinical significance

---

### 🥈 **PRIORITY 3: HIGH - Variant→Splicing (GTEx sQTL)**
**Table:** `gtex_v10_sqtl_associations` (1.4M rows)  
**Impact:** ⭐⭐⭐⭐ HIGH - Splicing variant analysis  
**Effort:** ⭐⭐⭐ MEDIUM - Larger dataset but manageable  
**Connection:** Axis 2 (Genomics) → Axis 3 (Transcriptomics)

**Why Priority 3:**
- **1.4M variant→splicing connections** processed and ready
- **Alternative splicing analysis** - critical for disease mechanisms
- **Medium risk** - larger but still manageable
- **High impact** - answers "How does variant X affect splicing in tissue Y?"

---

### 🥈 **PRIORITY 4: HIGH - AlphaFold Protein Impact**
**Table:** `alphafold_clinical_variant_impact` (11.6M rows)  
**Impact:** ⭐⭐⭐⭐ HIGH - Protein structure analysis  
**Effort:** ⭐⭐⭐ MEDIUM - Large dataset, needs careful loading  
**Connection:** Axis 2 (Genomics) → Axis 4 (Proteomics)

**Why Priority 4:**
- **11.6M variant→protein structure analyses** processed
- **3D structure impact** - unique capability
- **Medium risk** - large dataset but structured
- **High impact** - answers "How does variant X affect protein structure?"

---

### 🥉 **PRIORITY 5: MEDIUM - Common Variants (dbSNP)**
**Table:** `dbsnp_parquet_production` (37.3M rows)  
**Impact:** ⭐⭐⭐ MEDIUM - Population genetics  
**Effort:** ⭐⭐⭐⭐ HIGH - Very large dataset  
**Connection:** Axis 2 (Genomics) → Axis 7 (Population)

**Why Priority 5:**
- **37.3M common variants** - massive expansion
- **Population frequencies** - important for risk assessment
- **Higher risk** - very large dataset
- **Medium impact** - enhances existing capability rather than enabling new

---

### 🥉 **PRIORITY 6: MEDIUM - Massive Splice Data**
**Tables:** `spliceai_scores_production` (3.43B) + `spliceai_full_production` (952M)  
**Impact:** ⭐⭐⭐⭐⭐ MASSIVE - Complete transcriptomic analysis  
**Effort:** ⭐⭐⭐⭐⭐ EXTREME - Billion-row datasets  
**Connection:** Axis 2 (Genomics) → Axis 3 (Transcriptomics)

**Why Priority 6:**
- **4.4B splice predictions** - ultimate transcriptomic capability
- **Genome-wide coverage** - every possible splice site
- **Extreme risk** - could crash system, needs careful implementation
- **Massive impact** - but only after other foundations are solid

---

### 🔄 **PRIORITY 7: FUTURE - Raw Pathway Processing**
**Sources:** KEGG reference (367 pathways, 24K genes), PharmGKB pathways  
**Impact:** ⭐⭐⭐ MEDIUM - Metabolic pathway analysis  
**Effort:** ⭐⭐⭐⭐⭐ EXTREME - Requires data processing pipeline  
**Connection:** Axis 2 (Genomics) → Axis 5 (Metabolomics)

**Why Priority 7:**
- **Raw data needs processing** - not ready for immediate use
- **Complex ETL required** - build processing pipeline
- **High effort** - significant development work
- **Medium impact** - pathway analysis useful but not critical

---

## RECOMMENDED IMPLEMENTATION ORDER

### **IMMEDIATE (This Week):**
**Priority 2:** Variant→Expression (GTEx eQTL) - 405K rows  
**Expected Impact:** 74.3% → 82%+ benchmark score

### **SHORT TERM (Next Week):**
**Priority 3:** Variant→Splicing (GTEx sQTL) - 1.4M rows  
**Expected Impact:** 82% → 87%+ benchmark score

### **MEDIUM TERM (Following Week):**
**Priority 4:** AlphaFold Protein Impact - 11.6M rows  
**Expected Impact:** 87% → 90%+ benchmark score

### **LONG TERM (Future):**
**Priority 5-7:** Common variants, massive splice data, raw pathway processing

---

## RATIONALE

**Focus on processed, ready data first:**
- GTEx eQTL/sQTL data is already processed and structured
- Manageable sizes that won't crash the system
- High impact on cross-axis analysis
- Low risk implementation

**Save massive datasets for later:**
- Billion-row datasets need careful implementation
- Raw data processing requires significant development
- Better to have solid foundation first

**RECOMMENDATION:** Start with Priority 2 (GTEx eQTL) - it's ready, safe, and high impact for tissue-specific variant analysis.
