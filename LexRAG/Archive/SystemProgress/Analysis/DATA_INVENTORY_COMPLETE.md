# LexRAG Data Inventory - Complete Catalog

**Date:** 2025-10-24  
**Purpose:** Complete catalog of all data in LexRAG/data/ directory  
**Total Data Size:** ~270+ GB across all categories

---

## DATABASES (48.29 GB)

### Processed DuckDB Databases
**Location:** `data/databases/`

#### Primary Genomic Database
- **genomic_knowledge.duckdb:** 49.4 GB
  - Contains: ClinVar variants, GENCODE transcripts, protein interactions
  - Status: Primary database for LexAPI_Genomics
  - Tables: 100+ tables with processed genomic data

#### Specialized Databases
- **multi_omics.duckdb:** 25.5 MB
  - Contains: Gene expression, metabolic pathways, omics integration
  - Status: Used by LexAPI_Metabolics and LexAPI_Genomics

- **digital_twin.duckdb:** 26.3 MB  
  - Contains: 46 physiological tables (organ specs, body models, simulations)
  - Status: Used by LexAPI_Anatomics for physiological analysis

- **user_profiles_enhanced.duckdb:** 3.5 MB
  - Contains: User profile system, questionnaires, privacy controls
  - Status: Ready for user management system

- **population_risk.duckdb:** 3 MB
  - Contains: Risk models, population data
  - Status: Used by LexAPI_Populomics

- **etl_metadata.duckdb:** 0.3 MB
  - Contains: Data processing metadata
  - Status: ETL tracking and data lineage

---

## RAW GENOMIC DATA (~270+ GB)

### AlphaFold Protein Structures (52.22 GB)
**Location:** `data/global/alphafold/`
- **A1 folder:** 6,205 protein structure files (.gz)
- **A2 folder:** 6,053 protein structure files (.gz) 
- **swissprot_pdb_v4.tar:** Comprehensive protein database
- **Purpose:** 3D protein structure data for structural analysis
- **Status:** Raw data, could be integrated for protein structure queries

### SpliceAI Predictions (122.45 GB)
**Location:** `data/global/spliceai/`
- **34,340 files** with splice site predictions
- **spliceai_snv_working.parquet:** Processed SNV predictions
- **spliceai_indel_working.parquet:** Processed indel predictions
- **Raw VCF files:** Complete genome-wide splice predictions
- **Purpose:** Transcriptomic analysis for alternative splicing
- **Status:** Massive dataset for splice variant analysis

### GTEx Expression Data (64.38 GB)
**Location:** `data/global/gtex_v10/`
- **135 files** with tissue-specific gene expression
- **Tissue types:** All major human tissues and cell types
- **Format:** Compressed expression matrices (.gz, .tar)
- **Purpose:** Tissue-specific gene expression analysis
- **Status:** Rich expression data for LexAPI_Metabolics enhancement

### gnomAD Population Data (26.88 GB)
**Location:** `data/global/gnomad/`
- **gnomad.exomes.v4.0.sites.chr1.vcf.bgz:** Population variant frequencies
- **Purpose:** Population genetics and variant frequency data
- **Status:** Chromosome 1 only, could expand to full genome

### dbSNP Common Variants (4.14 GB)
**Location:** `data/global/dbsnp/`
- **dbsnp156_common.vcf.gz:** Common genetic variants
- **dbsnp156_common.parquet:** Processed variant data
- **Purpose:** Comprehensive variant catalog
- **Status:** Integrated into genomic_knowledge.duckdb

---

## CLINICAL AND DRUG DATA

### PharmGKB Pharmacogenomics (~75 MB)
**Location:** `data/pharmgkb/`
- **drugs.zip:** Drug information and properties
- **genes.zip:** Pharmacogenomic gene data (2.8 MB)
- **drug_gene_interactions.csv:** Drug-gene interaction data
- **clinicalVariants.zip:** Clinical pharmacogenomic variants
- **pathways.json.zip:** Metabolic pathway data (1.8 MB)
- **guidelineAnnotations.json.zip:** Clinical guidelines
- **Purpose:** Pharmacogenomic analysis for drug metabolism
- **Status:** Rich resource for LexAPI_Metabolics enhancement

### ClinVar Clinical Variants (0.16 GB)
**Location:** `data/global/clinvar/`
- **clinvar_GRCh38.vcf.gz:** Clinical variant database
- **Purpose:** Clinical significance of genetic variants
- **Status:** Integrated into genomic_knowledge.duckdb

---

## REGULATORY AND ANNOTATION DATA

### ENCODE Regulatory Elements (0.05 GB)
**Location:** `data/global/encode/`
- **GRCh38-cCREs.bed.gz:** Candidate cis-regulatory elements
- **GRCh38-cCREs-SCREEN.bed.gz:** SCREEN regulatory elements
- **Purpose:** Regulatory element annotation for epigenomic analysis
- **Status:** Available for LexAPI_Genomics regulatory analysis

### GENCODE Gene Annotations (0.03 GB)
**Location:** `data/global/gencode/`
- **gencode.v46.basic.annotation.gtf.gz:** Gene and transcript annotations
- **Purpose:** Gene structure and isoform information
- **Status:** Integrated into genomic databases

### Ontologies (0.14 GB)
**Location:** `data/global/ontologies/`
- **hp.obo:** Human Phenotype Ontology
- **mondo.obo:** Disease ontology
- **uberon-full.obo:** Anatomical structure ontology
- **cl.obo:** Cell type ontology
- **fma.csv.zip:** Foundational Model of Anatomy
- **Purpose:** Standardized biological terminology
- **Status:** Integrated into Neo4j knowledge graph

---

## REFERENCE AND UTILITY DATA

### Reference Genomes and Tools
**Location:** `data/global/liftover/`
- **Genome coordinate conversion:** hg19↔hg38 conversion chains
- **Purpose:** Convert between genome builds
- **Status:** Utility data for coordinate mapping

### Protein Networks and Interactions
**Location:** `data/protein_networks/`
- **string_human_interactions.txt.gz:** Protein-protein interactions
- **biomart_protein_mapping.tsv:** Gene-protein mappings
- **Purpose:** Protein interaction analysis
- **Status:** Available for enhanced protein analysis

### Population Genetics
**Location:** `data/population/`
- **gnomad_v4.1_constraint.tsv:** Gene constraint scores
- **Purpose:** Population-level gene importance metrics
- **Status:** Available for population analysis

---

## VECTOR AND SEARCH DATA

### Qdrant Vector Storage
**Location:** `data/qdrant_storage/` and `data/QDrant/`
- **12 collections** for literature search
- **Vector embeddings** for semantic search
- **Purpose:** Literature and knowledge search capabilities
- **Status:** Operational for LexAPI_Literature

---

## WORKING DIRECTORIES

### ETL and Processing
- **temp/:** Temporary processing files
- **snapshots/:** Data snapshots and backups
- **users/:** User data storage (empty, ready for use)

### Schemas and Indexes
- **schemas/:** SQL schema definitions for optimization
- **reference/:** Reference data for various analyses

---

## DATA SUMMARY BY PURPOSE

### For Genetic Analysis (LexAPI_Genomics)
- **✅ Available:** genomic_knowledge.duckdb (49.4 GB), ClinVar, dbSNP, GENCODE
- **✅ Potential:** SpliceAI (122 GB), AlphaFold proteins (52 GB)
- **Total:** ~225+ GB of genetic data

### For Anatomical Analysis (LexAPI_Anatomics)  
- **✅ Available:** digital_twin.duckdb, Neo4j ontologies
- **✅ Potential:** Ontology files (UBERON, FMA)
- **Total:** ~0.2 GB processed, ontologies integrated

### For Metabolic Analysis (LexAPI_Metabolics)
- **✅ Available:** multi_omics.duckdb, PharmGKB data
- **✅ Potential:** GTEx expression (64 GB), protein networks
- **Total:** ~65+ GB of metabolic/expression data

### For Population Analysis (LexAPI_Populomics)
- **✅ Available:** population_risk.duckdb, gnomAD data
- **✅ Potential:** Population constraint data
- **Total:** ~27+ GB of population data

### For Literature Analysis (LexAPI_Literature)
- **✅ Available:** Qdrant collections, vector storage
- **✅ Potential:** Papers directory (empty, ready for expansion)
- **Total:** Vector database operational

---

## TOTAL DATA ASSETS

**Processed Databases:** 48.3 GB (immediately usable)  
**Raw Genomic Data:** ~270 GB (available for integration)  
**Total Data Value:** ~320 GB of comprehensive biological data

**Key Insight:** We have massive raw data assets that could significantly enhance the LexRAG system beyond the current processed databases. The AlphaFold, SpliceAI, and GTEx data represent enormous untapped potential.

---

## RECOMMENDATIONS

1. **Immediate Use:** Current 48 GB of processed databases fully support all 5 APIs
2. **Enhancement Potential:** 270+ GB of raw data available for system expansion
3. **Data Security:** All data properly organized and preserved
4. **Scalability:** Infrastructure ready for additional data integration

**CONCLUSION:** LexRAG has exceptional data assets - both processed (operational) and raw (expansion potential). The data foundation supports current 74% benchmark performance with massive room for enhancement.

