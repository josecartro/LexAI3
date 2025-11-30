# LexAPI_Genomics Enhancement Plan - Production Data Integration

**Goal:** Integrate massive production datasets to unlock full 7 Axes potential  
**Current Performance:** 74.3% benchmark score  
**Target Performance:** 90%+ benchmark score  
**Data to Integrate:** 4.4+ billion additional rows

---

## CURRENT STATE ANALYSIS

### What We're Currently Using (MINIMAL)
- **clinvar_full_production:** 3.7M rows ✅ (good, keep using)
- **gencode_v44_transcripts:** 253K rows ✅ (small but functional)
- **Total current data:** ~4M rows

### What We're Missing (MASSIVE)
- **spliceai_scores_production:** 3.43 BILLION rows ❌
- **spliceai_full_production:** 952.8 MILLION rows ❌  
- **dbsnp_parquet_production:** 37.3 MILLION rows ❌
- **alphafold_clinical_variant_impact:** 11.6 MILLION rows ❌
- **alphafold_variant_protein_analysis:** 12.3 MILLION rows ❌
- **Total missing data:** ~4.4 BILLION rows

**We're using <0.1% of available genomic data!**

---

## INTEGRATION PLAN

### Phase 1: Critical Connection Tables (Week 1)
**Priority:** URGENT - These provide the 7 Axes connections

#### 1.1 Gene-Protein Mapping
**Table:** `biomart_protein_mapping` (245K rows)
- **Purpose:** Connect genes to proteins (Axis 2 → Axis 4)
- **Columns:** gene_symbol, protein_id, uniprot_id, transcript_id
- **Integration:** Add to LexAPI_Genomics database manager
- **API Enhancement:** New endpoint `/analyze/gene/{gene}/proteins`

#### 1.2 Variant-Expression Connections  
**Table:** `gtex_v10_eqtl_associations` (405K rows)
- **Purpose:** Connect variants to tissue expression (Axis 2 → Axis 3)
- **Columns:** variant_id, gene_symbol, tissue_type, expression_effect
- **Integration:** Critical for tissue-specific variant effects
- **API Enhancement:** Enhanced `/analyze/variant/{variant}` with tissue effects

#### 1.3 Variant-Splicing Connections
**Table:** `gtex_v10_sqtl_associations` (1.4M rows)  
- **Purpose:** Connect variants to splicing changes (Axis 2 → Axis 3)
- **Columns:** variant_id, gene_id, tissue_type, splicing_effect
- **Integration:** Critical for understanding variant mechanisms
- **API Enhancement:** Add splicing analysis to variant endpoints

#### 1.4 Gene-Pathway Connections
**Table:** `kegg_gene_pathway_links` (854 rows)
- **Purpose:** Connect genes to metabolic pathways (Axis 2 → Axis 5)
- **Columns:** gene_symbol, pathway_id, pathway_name
- **Integration:** Enable pathway-based analysis
- **API Enhancement:** New endpoint `/analyze/pathway/{pathway}/genes`

**Phase 1 Impact:** Enable true cross-axis connections for the first time

---

### Phase 2: Massive Variant Datasets (Week 2-3)
**Priority:** HIGH - Dramatically expand variant coverage

#### 2.1 dbSNP Common Variants
**Table:** `dbsnp_parquet_production` (37.3M rows)
- **Current gap:** We only have ClinVar (3.7M clinical variants)
- **Addition:** 37M common population variants
- **Benefit:** 10x more variant coverage, population genetics analysis
- **Integration approach:** Gradual loading with progress monitoring
- **API Enhancement:** Population frequency analysis for any variant

#### 2.2 AlphaFold Protein Impact Analysis
**Tables:** `alphafold_clinical_variant_impact` + `alphafold_variant_protein_analysis` (24M rows)
- **Current gap:** No protein structure analysis
- **Addition:** Variant effects on protein structure and function
- **Benefit:** True proteomic analysis (Axis 4)
- **Integration approach:** Batch processing with structure analysis
- **API Enhancement:** New endpoints for protein structure impact

**Phase 2 Impact:** 10x variant coverage + protein structure analysis

---

### Phase 3: Transcriptomic Powerhouse (Week 3-4)
**Priority:** CRITICAL - Unlock Axis 3 (Transcriptomics)

#### 3.1 SpliceAI Splice Predictions
**Tables:** `spliceai_scores_production` (3.43B) + `spliceai_full_production` (952M)
- **Current gap:** No splice analysis capability
- **Addition:** 4.4 BILLION splice site predictions
- **Benefit:** Complete transcriptomic analysis across entire genome
- **Integration approach:** Distributed loading, indexed by gene/variant
- **API Enhancement:** New splice analysis endpoints

**Critical Implementation Strategy:**
- **Batch processing:** Load in 1M row chunks with progress monitoring
- **Resource management:** Monitor memory usage, pause if needed
- **Index optimization:** Create gene_symbol and variant_id indexes first
- **Query optimization:** Use prepared statements for large datasets

**Phase 3 Impact:** Complete transcriptomic analysis capability

---

## TECHNICAL IMPLEMENTATION

### Database Connection Updates
```python
# Enhanced database manager with production tables
class EnhancedDatabaseManager:
    def __init__(self):
        self.production_tables = {
            'variants': 'clinvar_full_production',  # Current
            'common_variants': 'dbsnp_parquet_production',  # NEW
            'splice_scores': 'spliceai_scores_production',  # NEW
            'splice_full': 'spliceai_full_production',  # NEW
            'protein_impact': 'alphafold_clinical_variant_impact',  # NEW
            'protein_analysis': 'alphafold_variant_protein_analysis',  # NEW
            'gene_protein_map': 'biomart_protein_mapping',  # NEW
            'variant_expression': 'gtex_v10_eqtl_associations',  # NEW
            'variant_splicing': 'gtex_v10_sqtl_associations',  # NEW
            'gene_pathways': 'kegg_gene_pathway_links'  # NEW
        }
```

### Enhanced API Endpoints
```python
@app.get("/analyze/variant/{variant_id}/complete")
async def analyze_variant_complete(variant_id: str):
    """Complete variant analysis using ALL production tables"""
    # Query clinical significance (current)
    # + population frequency (dbSNP)
    # + tissue expression effects (GTEx eQTL)
    # + splicing effects (GTEx sQTL)  
    # + protein structure impact (AlphaFold)
    # + pathway involvement (KEGG)
    
@app.get("/analyze/gene/{gene}/transcriptomics")
async def analyze_gene_transcriptomics(gene: str):
    """Complete transcriptomic analysis using SpliceAI data"""
    # Query 4.4B splice predictions for gene
    # + tissue-specific expression (GTEx)
    # + alternative splicing patterns
    # + variant effects on splicing

@app.get("/analyze/protein_structure/{gene}")
async def analyze_protein_structure(gene: str):
    """Protein structure analysis using AlphaFold data"""  
    # Query 24M protein structure analyses
    # + variant effects on protein folding
    # + confidence scores and predictions
```

---

## PERFORMANCE PREDICTIONS

### Current Capability Enhancement
**Before Integration:**
- **Variants:** 3.7M clinical variants only
- **Genes:** Basic gene info only
- **Proteins:** No protein analysis
- **Transcriptomics:** No splice analysis
- **Cross-axis connections:** Very limited

**After Integration:**
- **Variants:** 41M variants (clinical + common)
- **Genes:** Complete gene analysis with pathways, proteins, expression
- **Proteins:** 24M protein structure analyses
- **Transcriptomics:** 4.4B splice predictions
- **Cross-axis connections:** Rich connections across all axes

### Expected Benchmark Improvement
- **Current:** 74.3% (limited data)
- **After Phase 1:** 85%+ (connection tables enable cross-axis analysis)
- **After Phase 2:** 90%+ (10x variant coverage + protein analysis)
- **After Phase 3:** 95%+ (complete transcriptomic analysis)

---

## IMPLEMENTATION TIMELINE

### Week 1: Connection Tables Integration
- **Day 1-2:** Integrate biomart_protein_mapping and gene_pathway_links
- **Day 3-4:** Integrate GTEx eQTL and sQTL associations
- **Day 5-7:** Test cross-axis connections and enhanced endpoints

### Week 2: Variant Expansion  
- **Day 1-3:** Integrate dbsnp_parquet_production (37M variants)
- **Day 4-5:** Integrate AlphaFold protein impact tables (24M rows)
- **Day 6-7:** Test enhanced variant and protein analysis

### Week 3: Transcriptomic Integration
- **Day 1-3:** Integrate spliceai_full_production (952M rows)
- **Day 4-7:** Integrate spliceai_scores_production (3.43B rows) with careful resource management

### Week 4: Testing and Optimization
- **Day 1-2:** Comprehensive testing of all new capabilities
- **Day 3-4:** Performance optimization and indexing
- **Day 5-7:** Re-run test-set.md benchmark for new score

---

## RISK MITIGATION

### Resource Management
- **Memory monitoring:** Pause if memory usage >80%
- **Batch processing:** Load large tables in chunks
- **Progress indicators:** Show detailed progress for billion-row operations
- **Rollback capability:** Ability to revert if issues arise

### Data Integrity
- **Backup current state** before any changes
- **Validate data quality** after each integration
- **Test API functionality** after each phase
- **Maintain current functionality** while adding new capabilities

---

## SUCCESS METRICS

**Phase 1 Success:** Cross-axis queries work (gene→protein, variant→expression)  
**Phase 2 Success:** 10x variant coverage, protein structure analysis working  
**Phase 3 Success:** Complete transcriptomic analysis across entire genome  
**Overall Success:** 90%+ benchmark score on test-set.md

**OUTCOME:** LexAPI_Genomics becomes a true 7 Axes powerhouse with comprehensive biological analysis across all domains.

---

**IMMEDIATE NEXT STEP:** Start Phase 1 - integrate the critical connection tables that enable cross-axis analysis.
