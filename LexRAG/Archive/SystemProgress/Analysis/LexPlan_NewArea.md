# LexRAG New Area Implementation Plan

**Date:** 2025-10-22  
**Goal:** Create comprehensive 7 Axes RAG system with smart domain APIs  
**Architecture:** Each API queries multiple databases internally, returns comprehensive domain answers

---

## NEW STRUCTURE OVERVIEW

### **LexRAG Folder Structure:**
```
LexRAG/
├── data/                    # Moved from LexMS - all databases
├── LexAPI_Genomics/         # Axes 2,3,4,6 (Genomics/Transcriptomics/Proteomics/Epigenomics)
├── LexAPI_Anatomics/        # Axis 1 (Anatomy/Structure)
├── LexAPI_Metabolics/       # Axis 5 (Metabolomics/Biochemistry)
├── LexAPI_Populomics/       # Axis 7 (Exposome/Phenome/Population)
├── LexAPI_Literature/       # Cross-Axis (Literature/Knowledge Search)
└── SystemProgress/          # Analysis and test results
    ├── Analysis/
    └── Tests/
```

### **Database Assets Confirmed:**
- **DuckDB:** 6 databases with 52.5B+ records
- **Neo4j:** 4M+ nodes with ontologies + genomic entities
- **Qdrant:** Literature vectors and semantic search

---

## TASK BREAKDOWN

### **PHASE 1: SMART API ARCHITECTURE (Week 1-2)**

#### **Task 1.1: LexAPI_Genomics (Axes 2,3,4,6)** ✅ COMPLETED
**Status:** ✅ Modular structure implemented  
**Details:** See `LexAPI_Genomics/README.md` for complete API documentation

#### **Task 1.2: LexAPI_Anatomics (Axis 1)** ✅ STRUCTURE CREATED
**Status:** ✅ Modular structure implemented  
**Details:** See `LexAPI_Anatomics/README.md` for complete API documentation

#### **Task 1.3: LexAPI_Metabolics (Axis 5)**
**Purpose:** Comprehensive metabolic analysis  
**Databases:** multi_omics.duckdb + genomic_knowledge.duckdb  
**Port:** 8005

**Capabilities to implement:**
- [ ] Metabolic profile: "How do genetics affect metabolism?"
  - Query multi_omics: Metabolite levels, pathway activities
  - Query genomic: CYP450 variants, metabolic genes
  - Return: Complete metabolic profile with genetic context

- [ ] Drug metabolism: "How does user process medications?"
  - Query genomic: Pharmacogenomic variants (CYP450, etc.)
  - Query multi_omics: Metabolic pathway activities
  - Return: Complete pharmacogenomic profile

**Endpoints to build:**
- [ ] `GET /analyze/metabolism/{user_id}` - Complete metabolic analysis
- [ ] `GET /analyze/drug_metabolism/{drug_name}` - Drug processing analysis
- [ ] `GET /analyze/pathway_metabolism/{pathway}` - Metabolic pathway analysis

#### **Task 1.4: LexAPI_Populomics (Axis 7)**
**Purpose:** Population and environmental analysis  
**Databases:** population_risk.duckdb + genomic_knowledge.duckdb  
**Port:** 8006

**Capabilities to implement:**
- [ ] Risk analysis: "What's my cancer risk?"
  - Query population_risk: Risk models and population data
  - Query genomic: User variants and frequencies
  - Return: Complete risk assessment with population context

- [ ] Environmental analysis: "How does environment affect my genetics?"
  - Query population_risk: Environmental risk factors
  - Query genomic: Environmental-gene interactions
  - Return: Complete environmental genomics analysis

**Endpoints to build:**
- [ ] `GET /analyze/risk/{disease_type}` - Complete disease risk analysis
- [ ] `GET /analyze/environment/{location}` - Environmental risk analysis
- [ ] `POST /analyze/user_risk` - Personalized risk assessment

#### **Task 1.5: LexAPI_Literature (Cross-Axis)**
**Purpose:** Literature search and knowledge synthesis  
**Databases:** Qdrant + calls to other APIs for context  
**Port:** 8003

**Capabilities to implement:**
- [ ] Literature search: "Find research about BRCA2 therapy"
  - Query Qdrant: Semantic search of literature
  - Query other APIs: Current knowledge context
  - Return: Literature synthesis with current knowledge integration

- [ ] Knowledge synthesis: "What's the latest on DNA repair?"
  - Query Qdrant: Recent papers and research
  - Query Genomics API: Current DNA repair gene data
  - Return: Synthesized current knowledge state

**Endpoints to build:**
- [ ] `GET /search/literature/{topic}` - Literature search with context
- [ ] `GET /synthesize/knowledge/{domain}` - Knowledge synthesis
- [ ] `POST /research/multi_turn` - Multi-step research queries

---

### **PHASE 2: DATABASE INTEGRATION (Week 2-3)**

#### **Task 2.1: Verify Database Connections**
- [ ] Test all database files exist in new data/ location
- [ ] Update all connection strings to new paths
- [ ] Verify data integrity after move
- [ ] Test basic queries to each database

#### **Task 2.2: Build Cross-API Connection System**
- [ ] Create connection tables in Neo4j:
  - `gene_tissue_expression` (which genes expressed where)
  - `variant_disease_risk` (which variants cause which diseases)
  - `pathway_gene_membership` (which genes in which pathways)
  - `drug_gene_interaction` (which drugs affected by which genes)
  - `tissue_anatomy_location` (which tissues in which organs)

#### **Task 2.3: Populate Connection Tables**
- [ ] Extract gene-tissue data from multi_omics.duckdb
- [ ] Extract disease-gene data from existing ontologies
- [ ] Extract pathway data from reference databases
- [ ] Extract drug-gene data from PharmGKB
- [ ] Validate connection data quality

---

### **PHASE 3: HYBRID QUERY SYSTEM (Week 3-4)**

#### **Task 3.1: Implement Comprehensive Endpoints**
- [ ] Each API gets `/analyze/{entity}` endpoint that queries ALL its databases
- [ ] Returns complete domain knowledge for any entity
- [ ] Includes cross-references to other domains

#### **Task 3.2: Implement Specific Query Endpoints**
- [ ] Each API gets SQL-like query capabilities
- [ ] AI Model can ask targeted questions
- [ ] Direct database access for specific data needs

#### **Task 3.3: Build AI Model Integration Interface**
- [ ] Create standardized query format across all APIs
- [ ] Implement response formatting for AI Model consumption
- [ ] Add query orchestration capabilities

---

### **PHASE 4: TESTING AND VALIDATION (Week 4-5)**

#### **Task 4.1: SystemProgress Documentation**
- [ ] All tests go to SystemProgress/Tests/
- [ ] All analysis goes to SystemProgress/Analysis/
- [ ] Track progress and results systematically

#### **Task 4.2: Comprehensive Testing**
- [ ] Test each API individually
- [ ] Test cross-API queries and connections
- [ ] Validate against test-set.md benchmark
- [ ] Performance testing with large queries

#### **Task 4.3: AI Model Integration Testing**
- [ ] Test hybrid query approach (broad + specific)
- [ ] Validate AI Model can orchestrate complex analyses
- [ ] Test real-world scenarios (beach example, mole analysis)

---

## SUCCESS CRITERIA

**Phase 1 Complete:** All 5 APIs operational with multi-database access  
**Phase 2 Complete:** Cross-API connections enable complex reasoning  
**Phase 3 Complete:** Hybrid query system working (broad + specific)  
**Phase 4 Complete:** AI Model can orchestrate comprehensive health analysis

**Final Goal:** RAG system that enables AI Model to answer complex questions like:
- "What does BRCA2 affect in my body?" (complete 7-axis analysis)
- "Why might I have back pain based on my genetics?" (cross-domain reasoning)
- "How does my Finnish genetics affect living in Spain?" (environmental-genetic interaction)

---

## IMMEDIATE NEXT STEPS

1. **Start with LexAPI_Genomics** - most critical for health analysis
2. **Verify database connections** in new data/ location
3. **Build first comprehensive endpoint** - `/analyze/gene/{gene_symbol}`
4. **Test with BRCA2 example** - prove concept works
5. **Iterate and expand** to other APIs

**Timeline:** 5 weeks to complete comprehensive RAG system  
**Priority:** Focus on connection quality over speed
