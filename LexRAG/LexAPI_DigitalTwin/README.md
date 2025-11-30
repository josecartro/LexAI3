# LexAPI_DigitalTwin - Digital Twin Modeling API

## Overview
Digital twin creation and management API with Adam/Eve reference models. Provides intelligent data overlay logic to handle missing user data by falling back to population-matched or generic reference models.

## Features
- **Adam & Eve Reference Models** - Comprehensive default male/female baselines
- **Data Overlay Logic** - User > Population > Sex > Generic priority system
- **Confidence Scoring** - Transparent data source quality assessment
- **Gap Analysis** - Intelligent identification of missing data
- **Adaptive Questionnaires** - Targeted questions based on data gaps
- **Real-time Updates** - Dynamic twin updates as new data arrives

## Architecture
Following LexRAG modular pattern:
- `code/api_endpoints.py` - Main FastAPI endpoints
- `code/database_manager.py` - ClickHouse and user database connections
- `code/twin_manager.py` - Digital twin creation and management
- `code/reference_models.py` - Adam & Eve model management
- `code/data_overlay.py` - Intelligent data overlay engine
- `config/database_config.py` - Database and API configuration

## API Endpoints
- `GET /twin/{user_id}/model` - Get complete digital twin
- `POST /twin/{user_id}/update` - Update twin with latest data
- `GET /twin/{user_id}/confidence` - Get confidence analysis
- `GET /twin/{user_id}/gaps` - Get data gap analysis
- `GET /twin/{user_id}/completeness` - Get completeness score
- `GET /twin/reference/adam` - Get Adam default male model
- `GET /twin/reference/eve` - Get Eve default female model
- `POST /twin/{user_id}/questionnaire/adaptive` - Generate targeted questionnaire

## Data Overlay Logic
```
Priority System:
1. User-specific data (confidence: 1.0)
2. Population-matched data (confidence: 0.7)  
3. Sex-matched data (confidence: 0.5)
4. Generic reference data (confidence: 0.3)
```

## Usage
```bash
# Start the API
api_startup.bat

# Check health
curl http://localhost:8008/health

# Get Adam reference model
curl http://localhost:8008/twin/reference/adam

# Get user digital twin
curl http://localhost:8008/twin/user123/model
```

## Integration
Designed to work with:
- **LexAPI_Users** - User profile and genomic data
- **LexAPI_AIGateway** - AI model query orchestration
- **LexRAG Core APIs** - 7-axis genomic analysis integration
- **ClickHouse** - Fast reference data access with 4.4B records
