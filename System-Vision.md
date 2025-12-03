# Below is a full “what the system is / what it can do / how it works now” description, written as if it were the current project overview. I’ll keep calling it “the system,” per your note.

---

## What the system is (one clear statement)

**The system is a fast, tool-using AI layer on top of huge multi-omics + ontology data stores, built to answer human biology questions by dynamically fetching only the evidence it needs across 7 Axes of human data.**

In practice: you’ve got billions of genomic and expression records in ClickHouse, structured knowledge in Neo4j/Qdrant, and a model that can call specialized APIs to retrieve, integrate, and reason over those datasets in real time.

---

## What the system is able to do

### 1) Real-time retrieval over extremely large biomedical data
Because the core scientific data is in ClickHouse (4.4B records), the system can respond to questions like:

- “What does rs7412 in APOE mean?”  
- “List ClinVar pathogenic variants in BRCA1 with allele frequency < 0.1% (gnomAD).”
- “Which variants in gene X are predicted to disrupt splicing?”

**Key capability:** massive lookups, filtering, ranking, and aggregation over billions of rows without pre-indexing everything into the LLM.

### 2) Cross-axis integration
The system is explicitly designed so an answer is not “one dataset says X,” but “across axes we see: genomic variant → splice impact → tissue expression → phenotype/disease mapping → drug implications.”

That is the heart of the platform:
- **ClickHouse gives breadth and speed.**
- **Neo4j gives semantic structure and causal “shape.”**
- **Qdrant gives literature grounding.**
- **The model orchestrates the join.**

### 3) Ontological reasoning
With MONDO, HPO, UBERON (and other anatomy/cell ontologies), the system can:
- normalize terms (“kidney cysts” → HPO term),
- traverse relationships (“part-of,” “is-a,” disease-phenotype links),
- and use that structure to guide data fetches.

So it can answer things like:
- “Given these phenotypes, what diseases are most likely?”
- “Which anatomical structures relate to this disease mechanism?”

### 4) Explainable, evidence-first answers
The system isn’t a black box chat model; it’s a **retrieval-then-reason engine**. Each answer is built from:
- explicit tool calls,
- returned evidence,
- and a synthesis step that can cite where conclusions come from.

### 5) Personalized context (via Users + Digital Twin)
LexAPI_Users + LexAPI_DigitalTwin allow:
- user profiles, privacy controls, provenance,
- and a baseline “Adam/Eve” reference model to compare a user’s data against.

So queries like:
- “Why are my gene expression levels different than normal?”
become:
- “Compared to baseline model + population, here are the top deviating tissues/genes, and likely drivers.”

---

## The 7 Axes and how the system uses them

Think of the axes as **orthogonal coordinate systems for human biology**.  
A question can live in one axis, or span several. The system’s job is to fetch evidence per axis and integrate.

### **Axis 1: Anatomy (Structural)**
**What it represents:** *where biology happens.*  
Your anatomical graph gives hierarchical and causal structure:
Body → organ system → organ → tissue → cell → organelle → molecule.

**Data/Tools used:**
- Neo4j anatomical graphs (UBERON, CL, FMA-style hierarchy)
- LexAPI_Anatomics (port 8002)

**What the system can do here:**
- map genes/proteins/phenotypes to anatomical structures,
- traverse “part-of” and “located-in” anatomical relationships,
- return multi-scale structural pathways.

**Example query:**  
> “What organs are affected by CFTR mutations?”  
**Tool pattern:**
1. Anatomics: find UBERON structures expressing CFTR / known affected structures.  
2. Literature: confirm clinical manifestations.  
3. Genomics (optional): list key CFTR variants associated with organ-level effects.

---

### **Axis 2: Genomics (DNA)**
**What it represents:** *the variant layer.*  
The raw sequence + variants compared to reference builds.

**Data/Tools used:**
- genomics_db (ClinVar/dbSNP/SpliceAI/GENCODE)
- LexAPI_Genomics (8001)
- LexAPI_Populomics (8006) for gnomAD frequencies

**What the system can do here:**
- variant lookup by rsID / position / HGVS,
- clinical significance retrieval,
- population frequency context,
- gene ↔ variant aggregation.

**Example query:**  
> “I have rs7412 in APOE. What does this mean?”  
**Tool pattern:**
1. Genomics: rs7412 annotation, gene, effect.  
2. Populomics: allele frequency + risk stratification by population.  
3. Literature: clinical implication, especially APOE ε2/ε3/ε4 context.

---

### **Axis 3: Transcriptomics (RNA)**
**What it represents:** *when and how genes are expressed and spliced.*

**Data/Tools used:**
- expression_db (GTEx 54 tissues)
- genomics_db (SpliceAI predictions, GENCODE transcripts)
- LexAPI_Metabolics (8005) for expression + PharmGKB adjacency  
- LexAPI_Genomics for splice impacts

**What the system can do here:**
- tissue-specific expression profiles for genes,
- alternative splicing impact predictions per transcript,
- connect splice disruptions to tissue symptoms.

**Example query:**  
> “Explain why the same variant causes different symptoms in different tissues.”  
**Tool pattern:**
1. Genomics: splice/variant consequence candidates.  
2. Metabolics/Expression: tissue expression ranks for affected transcripts.  
3. Anatomics: map tissues to organ systems.  
4. Literature: known tissue-specific disease presentations.

---

### **Axis 4: Proteomics (Protein)**
**What it represents:** *functional molecular machines and networks.*

**Data/Tools used:**
- proteins_db (AlphaFold + STRING networks)
- LexAPI_Genomics for variant → protein mapping  
- (Potentially Literature for functional consequences)

**What the system can do here:**
- show protein structural context for variants,
- list interaction partners,
- infer disrupted pathways from interaction edges.

**Example query:**  
> “How does a missense mutation disrupt a metabolic pathway?”  
**Tool pattern:**
1. Genomics: variant → affected protein domain.  
2. Proteins: AlphaFold region + STRING interaction neighbors.  
3. Pathways: which KEGG pathway those proteins sit in.  
4. Synthesis: likely cascade effects.

---

### **Axis 5: Metabolomics (Biochemistry)**
**What it represents:** *downstream chemical state and pathways.*

**Data/Tools used:**
- pathways_db (KEGG pathways)
- LexAPI_Metabolics (8005)
- PharmGKB adjacency for nutrient/drug metabolism

**What the system can do here:**
- map genes/proteins to metabolic pathways,
- infer metabolite perturbations from variant effects,
- connect to diet/drug metabolism impact.

**Example query:**  
> “How do my variants affect metabolism and diet?”  
**Tool pattern:**
1. Genomics: list impactful enzymes/genes.  
2. Pathways/Metabolics: locate those enzymes in KEGG pathways.  
3. Literature: phenotype/drug/nutrient evidence.  
4. Output: diet/drug risk notes with confidence.

---

### **Axis 6: Epigenomics (Regulation)**
**What it represents:** *control of gene activity beyond sequence.*

**Data/Tools used:**
- regulatory_db (ENCODE regulatory elements)
- genomics_db (regulatory-gene proximity links)
- LexAPI_Genomics for overlap queries

**What the system can do here:**
- identify regulatory elements overlapping variants,
- infer gene regulation shifts,
- connect regulation to expression changes and phenotypes.

**Example query:**  
> “How do environmental factors affect gene expression epigenetically?”  
**Tool pattern:**
1. Literature: known exposure → epigenetic marks.  
2. Regulatory: map affected regions to target genes.  
3. Expression: see if targets show tissue deviation.  
4. Output: plausible regulation → expression → phenotype chain.

---

### **Axis 7: Exposome / Phenome**
**What it represents:** *environment + observable traits and outcomes.*

**Data/Tools used:**
- ontology_db (HPO, MONDO)
- LexAPI_Anatomics for anatomy ↔ phenotype context  
- LexAPI_Literature (8003) for exposure evidence  
- LexAPI_Users for individualized exposure/lifestyle data

**What the system can do here:**
- phenotype normalization to HPO,
- disease linking via MONDO,
- environmental/lifestyle modulation of risk.

**Example query:**  
> “How do lifestyle choices interact with genetics?”  
**Tool pattern:**
1. Users: lifestyle/exposure profile.  
2. Genomics/Populomics: genetic risk baseline.  
3. Ontology: map phenotypes to risks/diseases.  
4. Literature: gene-environment interaction evidence.  
5. Output: combined risk narrative + ranked factors.

---

## How the APIs map to the axes

Here’s an “operational view” of your services.

### **LexAPI_Genomics (8001)**
**Primary axes:** 2, 3, 6  
**What it should return well:**
- variant annotation (ClinVar/dbSNP),
- splice prediction summaries (SpliceAI),
- variant ↔ gene ↔ transcript mappings,
- regulatory overlap results.

### **LexAPI_Anatomics (8002)**
**Primary axes:** 1, 7  
**What it should return well:**
- UBERON/CL/FMA traversals,
- structure hierarchies,
- part-of/located-in graphs,
- anatomy ↔ phenotype/disease links.

### **LexAPI_Literature (8003)**
**Supports all axes**
- semantic literature retrieval in Qdrant,
- evidence for uncertain claims,
- recent or rare findings that aren’t in structured DBs.

### **LexAPI_Metabolics (8005)**
**Primary axes:** 3, 5 (+2)
- GTEx expression retrieval per tissue,
- KEGG pathway membership,
- PharmGKB drug-gene adjacency.

### **LexAPI_Populomics (8006)**
**Primary axes:** 2, 7  
- gnomAD allele frequencies,
- population stratification context,
- rarity assessment.

### **LexAPI_Users (8007)**
**Primary axes:** 7 (personalization)  
- user profiles, privacy, preferences,
- structured user context for risk modulations.

### **LexAPI_DigitalTwin (8008)**
**Primary axes:** baseline across all  
- reference “normal” models (Adam/Eve),
- used for comparisons and deviation scoring.

### **LexAPI_AIGateway (8009)**
**Not an axis; it’s orchestration**
- tool calling sandbox,
- system prompt + jinja tool definitions,
- controls max tool calls, formatting, guardrails.

---

## How the AI model works now (new orchestration)

### Old approach (your previous structure)
1. User asks a question.
2. A smart logic layer prefetches likely-needed data.
3. The model gets: user prompt + user context + prefetched RAG context.
4. It answers in one shot.

**Pros:** predictable, fewer tool calls, fast for common patterns.  
**Cons:** logic layer must anticipate every query type; brittle for new tasks.

### New approach (current system)
1. User asks a question.
2. The model receives only the prompt + system tool schema.
3. The model decides:
   - which axis(es) this question touches,
   - which APIs to call,
   - in what order,
   - stopping once it has enough evidence.
4. It can use up to **12 tool calls** (unless you change that).
5. It synthesizes the final answer.

**Pros:**
- **flexible:** model can handle novel questions without new routing code.
- **self-correcting:** it can refine queries based on returned data.
- **axis-aware by nature:** because tools are axis-shaped.

**Cons:**
- If tool budget is too low, complex multi-axis queries may truncate.
- Needs strong tool descriptions and return formats to avoid wandering.

---

## What “good model behavior” looks like

A strong response pattern is:

1) **Classify the query by axis**  
   - “This touches Axis 2 (variant), Axis 3 (splice), Axis 1 (tissue/organ), Axis 7 (phenotype).”

2) **Plan tool calls** (lightweight internal plan)  
   - “First fetch variant annotation, then expression, then anatomy, then literature if needed.”

3) **Execute iteratively**
   - The model *reads* what comes back.
   - If evidence is sufficient, stop early.
   - If not, refine and call again.

4) **Synthesize with boundaries**
   - Explicitly mark what is factual from DB vs inferred.
   - Provide uncertainty and rationale.

---

## Two concrete multi-axis examples (end-to-end)

### Example A: Variant → splice → tissue → phenotype
**User:**  
> “I have a rare variant in PKD1. Why does it mainly affect kidneys?”

**Model tool flow:**
1. **Genomics:** retrieve variant consequence + SpliceAI impact + transcript list.  
2. **Metabolics/Expression:** query GTEx for PKD1 expression across tissues.  
3. **Anatomics:** map top tissues/cell types to UBERON kidney structures.  
4. **Literature (optional):** confirm known mechanism for renal cysts.

**Answer skeleton:**
- Variant evidence (Axis 2)  
- Splicing evidence and most affected isoforms (Axis 3)  
- Kidney-dominant expression and developmental context (Axis 3→1)  
- Phenotype/disease mapping (Axis 7)  
- Clear conclusion with uncertainty bounds

---

### Example B: Drug metabolism risk
**User:**  
> “Given my variants, are there any drugs I should avoid?”

**Model tool flow:**
1. **Genomics:** pull user CYP variants and functional annotations.  
2. **Metabolics/PharmGKB:** map variants to drug-gene interactions and pathways.  
3. **Populomics:** allele frequency context (rare vs common) to calibrate confidence.  
4. **Literature:** for ambiguous/novel variants.

**Answer skeleton:**
- List of affected enzymes  
- Drug classes impacted  
- Directionality (poor metabolizer/ultrarapid)  
- Suggested clinical follow-up framing

---

## About the 12-call budget

You’re right to question it. Whether 12 is “too few” depends on:
- average axes per query (1–2 vs 4–7),
- how often API calls need refinement,
- how chunky each API response is.

A rule of thumb:
- **Level-1/2 queries:** 1–5 calls.
- **Level-3 multi-axis queries:** 6–15 calls.
- **Level-4 predictive / cross-axis:** can exceed 15–25 if you allow refinement.

So 12 is a **reasonable default**, but you may want:
- **dynamic budgets** by detected complexity, or
- a “retry reserve,” e.g. soft stop at 12 but allow up to 20 if confidence is low.

---

## The simplest way to explain the system to others

If you need a short pitch:

> “The system is a multi-omics RAG platform. All scientific data lives in ClickHouse, ontologies in Neo4j, papers in Qdrant. Instead of prefetching context, the AI model uses tools to pull the evidence it needs across 7 biological axes—genome, transcriptome, proteome, metabolome, epigenome, anatomy, and phenome/exposome—then integrates it into an explainable answer in real time.”
