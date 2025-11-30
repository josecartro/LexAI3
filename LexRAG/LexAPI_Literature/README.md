# LexAPI_Literature - Comprehensive Literature/Knowledge Search API

**Cross-Axis: Literature Search, Knowledge Synthesis, Research Integration**

## Purpose

Smart domain API that provides comprehensive literature search and knowledge synthesis by querying Qdrant vector database and integrating with other domain APIs for contextual analysis.

## Architecture

### Modular Structure
```
LexAPI_Literature/
├── code/                          # Business logic (modular, focused)
│   ├── api_endpoints.py          # Main controller
│   ├── database_manager.py      # Database connections
│   ├── literature_searcher.py   # Literature search logic
│   └── knowledge_synthesizer.py # Knowledge synthesis logic
├── config/                       # Configuration
│   └── database_config.py       # Database settings
├── data/                         # API-specific data
├── tests/                        # API-specific tests
├── main.py                       # Entry point
├── api_startup.bat              # Startup script
└── README.md                    # This documentation
```

### Database Integration
- **Qdrant** - Literature vectors, semantic search, research papers
- **Cross-API Integration** - Calls other LexRAG APIs for domain context

## API Endpoints

### Comprehensive Analysis Endpoints
```
GET /search/literature/{topic}
```
**Purpose:** Literature search with domain context  
**Example:** `/search/literature/BRCA2_therapy?context_apis=genomics,anatomics`  
**Returns:** Literature results + current domain knowledge integration

```
GET /synthesize/knowledge/{domain}
```
**Purpose:** Knowledge synthesis for domain  
**Example:** `/synthesize/knowledge/DNA_repair`  
**Returns:** Synthesized current knowledge state with literature support

```
GET /research/multi_turn/{initial_query}
```
**Purpose:** Multi-step research with iterative knowledge building  
**Example:** `/research/multi_turn/cancer_immunotherapy?max_turns=3`  
**Returns:** Progressive research with expanding knowledge base

## Usage Examples

### For AI Model - Literature Context
```python
# AI asks: "What's the latest research on BRCA2 therapy?"
response = requests.get("http://localhost:8003/search/literature/BRCA2_therapy?context_apis=genomics")

# Returns literature synthesis with current genetic knowledge
```

### For AI Model - Knowledge Synthesis
```python
# AI asks: "What do we know about DNA repair mechanisms?"
response = requests.get("http://localhost:8003/synthesize/knowledge/DNA_repair")

# Returns synthesized knowledge from literature + current data
```

## Current Status

**Implementation:** Modular structure created, core endpoints defined  
**Database Connections:** Qdrant + cross-API integration  
**Port:** 8003
