# LexAPI_Populomics - Comprehensive Population/Environmental Analysis API

**Axis 7: Exposome, Phenome, Population Genetics, Environmental Factors**

## Purpose

Smart domain API that provides comprehensive population and environmental analysis by querying multiple databases internally and returning complete environmental-genetic context for AI model consumption.

## Architecture

### Modular Structure
```
LexAPI_Populomics/
├── code/                          # Business logic (modular, focused)
│   ├── api_endpoints.py          # Main controller
│   ├── database_manager.py      # Database connections
│   ├── risk_analyzer.py         # Risk analysis logic
│   └── environment_analyzer.py  # Environmental analysis logic
├── config/                       # Configuration
│   └── database_config.py       # Database settings
├── data/                         # API-specific data
├── tests/                        # API-specific tests
├── main.py                       # Entry point
├── api_startup.bat              # Startup script
└── README.md                    # This documentation
```

### Database Integration
- **population_risk.duckdb** - Risk models, population data, environmental factors
- **genomic_knowledge.duckdb** - Variant frequencies, population genetics

## API Endpoints

### Comprehensive Analysis Endpoints
```
GET /analyze/environmental_risk/{location}
```
**Purpose:** Environmental risk analysis for location  
**Example:** `/analyze/environmental_risk/spain?genetic_variants=rs7412,rs429358`  
**Returns:** Environmental factors, genetic susceptibility, risk assessment

```
GET /analyze/disease_risk/{disease_type}
```
**Purpose:** Disease risk analysis  
**Example:** `/analyze/disease_risk/cancer?user_variants=rs7412`  
**Returns:** Genetic risk factors, population context, environmental factors

```
POST /analyze/user_risk
```
**Purpose:** Personalized risk assessment  
**Input:** User genetic profile + environmental data  
**Returns:** Comprehensive risk analysis across all factors

## Usage Examples

### For AI Model - Environmental Analysis
```python
# AI scenario: Finnish child moved to Spain
response = requests.get("http://localhost:8006/analyze/environmental_risk/spain?genetic_variants=MC1R_variants")

# Returns UV risk assessment with genetic context and recommendations
```

### For AI Model - Disease Risk
```python
# AI asks: "What's the cancer risk for this genetic profile?"
response = requests.get("http://localhost:8006/analyze/disease_risk/cancer?user_variants=BRCA2_variants")

# Returns comprehensive cancer risk with population context
```

## Current Status

**Status:** ✅ FULLY OPERATIONAL - Modular architecture with comprehensive analysis  
**Testing:** ✅ Health check passed, both databases connected  
**Databases:** ✅ population_risk + genomic_knowledge connected and functional  
**Port:** 8006

### Verified Working Capabilities
- **Database Connections:** Both population_risk and genomic_knowledge databases ✅
- **Health Check:** Service responding properly ✅
- **Modular Structure:** Fixed imports and proper architecture ✅
- **AI Model Ready:** Endpoints available for environmental and disease risk analysis ✅
