# LexAPI_Metabolics - Comprehensive Metabolic Analysis API

**Axis 5: Metabolomics, Biochemistry, Multi-omics Integration**

## Purpose

Smart domain API that provides comprehensive metabolic analysis by querying multiple databases internally and returning complete metabolic context for AI model consumption.

## Architecture

### Modular Structure
```
LexAPI_Metabolics/
├── code/                          # Business logic (modular, focused)
│   ├── api_endpoints.py          # Main controller
│   ├── database_manager.py      # Database connections
│   ├── metabolism_analyzer.py    # Metabolic analysis logic
│   └── drug_analyzer.py         # Pharmacogenomic analysis logic
├── config/                       # Configuration
│   └── database_config.py       # Database settings
├── data/                         # API-specific data
├── tests/                        # API-specific tests
├── main.py                       # Entry point
├── api_startup.bat              # Startup script
└── README.md                    # This documentation
```

### Database Integration
- **multi_omics.duckdb** - Metabolite levels, pathway activities, omics integration
- **genomic_knowledge.duckdb** - CYP450 variants, metabolic genes, pharmacogenomics

## API Endpoints

### Comprehensive Analysis Endpoints
```
GET /analyze/metabolism/{user_id}
```
**Purpose:** Complete metabolic analysis  
**Example:** `/analyze/metabolism/user123`  
**Returns:** Metabolite profile, pathway activities, genetic factors

```
GET /analyze/drug_metabolism/{drug_name}
```
**Purpose:** Drug metabolism analysis  
**Example:** `/analyze/drug_metabolism/warfarin`  
**Returns:** CYP450 variants, metabolic pathways, dosing implications

```
GET /analyze/pathway_metabolism/{pathway}
```
**Purpose:** Metabolic pathway analysis  
**Example:** `/analyze/pathway_metabolism/glycolysis`  
**Returns:** Pathway genes, metabolite flows, genetic variants

## Usage Examples

### For AI Model - Metabolic Profile
```python
# AI asks: "How do genetics affect metabolism?"
response = requests.get("http://localhost:8005/analyze/metabolism/user123")

# Returns comprehensive metabolic analysis with genetic context
```

### For AI Model - Drug Processing
```python
# AI asks: "How does this user process medications?"
response = requests.get("http://localhost:8005/analyze/drug_metabolism/warfarin")

# Returns pharmacogenomic profile with dosing recommendations
```

## Current Status

**Status:** ✅ FULLY OPERATIONAL - Modular architecture with comprehensive analysis  
**Testing:** ✅ All endpoints tested and working (4 standard + 1 GraphQL)  
**GraphQL:** ✅ Easy → Medium → Hard tests all successful  
**Databases:** ✅ multi_omics + genomic_knowledge connected and functional  
**Port:** 8005

### Verified Working Capabilities
- **Metabolism Analysis:** All test users responding with genetic factors ✅
- **Drug Metabolism:** Warfarin, aspirin, ibuprofen all working with 30 CYP450 variants ✅
- **Pharmacogenomic Analysis:** 30 variants across multiple CYP genes ✅
- **GraphQL Queries:** Metabolite lookup, pharmacogenomic analysis, complex queries ✅
- **AI Model Ready:** Both comprehensive endpoints and flexible GraphQL available ✅
