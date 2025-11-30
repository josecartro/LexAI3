# LexRAG - 7 Axes RAG System

**Comprehensive genomic data platform with intelligent domain APIs**

## Overview

LexRAG is a modular RAG (Retrieval-Augmented Generation) system designed to support AI models with comprehensive biological and genomic knowledge across 7 biological axes.

## Architecture

### Smart Domain APIs
Each API is a specialized domain expert that queries multiple databases internally and returns comprehensive analysis:

- **LexAPI_Genomics** (Port 8001) - Axes 2,3,4,6 (Genomics/Transcriptomics/Proteomics/Epigenomics)
- **LexAPI_Anatomics** (Port 8002) - Axis 1 (Anatomy/Structure)
- **LexAPI_Metabolics** (Port 8005) - Axis 5 (Metabolomics/Biochemistry)
- **LexAPI_Populomics** (Port 8006) - Axis 7 (Exposome/Phenome/Population)
- **LexAPI_Literature** (Port 8003) - Cross-Axis (Literature/Knowledge Search)

### Database Infrastructure
- **DuckDB:** 52.5B+ records (variants, genes, expression, clinical data)
- **Neo4j:** 4M+ nodes (ontologies, causal relationships, gene-tissue connections)
- **Qdrant:** Literature vectors and semantic search

## Quick Start

```bash
# Start all APIs
cd LexRAG
start_all_apis.bat

# Test system
cd SystemProgress/Tests
python test_comprehensive_system.py
```

## API Documentation

Each API has detailed documentation in its README.md:
- `LexAPI_Genomics/README.md` - Genetic analysis capabilities
- `LexAPI_Anatomics/README.md` - Anatomical analysis capabilities
- `LexAPI_Metabolics/README.md` - Metabolic analysis capabilities
- `LexAPI_Populomics/README.md` - Population/environmental analysis
- `LexAPI_Literature/README.md` - Literature search and synthesis

## For AI Model Integration

### Comprehensive Analysis
```python
# Get complete genetic analysis
response = requests.get("http://localhost:8001/analyze/gene/BRCA2")
# Returns: variants, expression, causal connections, clinical relevance

# Get complete anatomical analysis  
response = requests.get("http://localhost:8002/analyze/organ/breast")
# Returns: structure, gene expression, disease connections, physiology
```

### Specific Queries
```python
# Targeted genetic query
response = requests.get("http://localhost:8001/query/variants?gene=APOE&pathogenic_only=true")
# Returns: specific variant data for focused analysis
```

## Development

### Folder Structure
```
LexRAG/
├── data/                    # All databases
├── LexAPI_{Domain}/         # Each API follows modular structure:
│   ├── code/               # Business logic (small, focused files)
│   ├── config/             # Configuration and settings
│   ├── data/               # API-specific data
│   ├── tests/              # API-specific tests
│   ├── main.py             # Entry point
│   ├── api_startup.bat     # Startup script
│   └── README.md           # API documentation
├── SystemProgress/          # System-wide testing and analysis
└── start_all_apis.bat      # Master startup script
```

### Testing
- **API-specific tests:** `{API}/tests/` - Test individual API functionality
- **System tests:** `SystemProgress/Tests/` - Test cross-API integration
- **Analysis:** `SystemProgress/Analysis/` - Performance and capability analysis

## Success Metrics

**Current Status:** All 5 APIs operational with comprehensive multi-database analysis  
**Goal:** Enable AI models to answer complex health questions through intelligent RAG queries  
**Benchmark:** Test-set.md 7 Axes benchmark questions
