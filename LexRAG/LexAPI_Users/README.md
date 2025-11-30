# LexAPI_Users - User Management & Profile API

## Overview
User registration, profile management, and DNA processing API for the LexRAG platform. Provides the foundation for digital twin functionality with secure user data management.

## Features
- **User Registration & Authentication** - Secure user account management
- **DNA File Processing** - Support for 23andMe, AncestryDNA, VCF formats
- **Device Integration** - Smartwatch and fitness tracker data
- **Adaptive Questionnaires** - Intelligent question generation based on data gaps
- **Profile Completeness** - Scoring and recommendations for data improvement
- **Privacy Controls** - Granular consent and data management

## Architecture
Following LexRAG modular pattern:
- `code/api_endpoints.py` - Main FastAPI endpoints
- `code/database_manager.py` - Database connection management
- `code/user_manager.py` - User profile operations
- `code/dna_processor.py` - DNA file processing
- `code/questionnaire_engine.py` - Adaptive questionnaire generation
- `config/database_config.py` - Database and API configuration

## API Endpoints
- `POST /users/register` - Register new user
- `GET /users/{user_id}/profile` - Get user profile
- `PUT /users/{user_id}/profile` - Update user profile
- `POST /users/{user_id}/upload-dna` - Upload DNA file
- `GET /users/{user_id}/genomics` - Get genomic data summary
- `GET /users/{user_id}/questionnaire` - Get adaptive questionnaire
- `POST /users/{user_id}/questionnaire` - Submit questionnaire responses
- `POST /users/{user_id}/devices/sync` - Sync device data
- `GET /users/{user_id}/completeness` - Get profile completeness
- `GET /users/{user_id}/data-status` - Get comprehensive data status

## Usage
```bash
# Start the API
api_startup.bat

# Check health
curl http://localhost:8007/health

# Access documentation
http://localhost:8007/docs
```

## Database Schema
Uses DuckDB for user data with ClickHouse integration for reference data:
- `user_profiles` - Basic user information and preferences
- `user_genomics` - DNA file tracking and variant data
- `user_devices` - Connected device information
- `user_questionnaires` - Questionnaire responses and scoring

## Integration
Designed to work with:
- **LexAPI_DigitalTwin** - Digital twin modeling and reference data
- **LexAPI_AIGateway** - AI model integration and query orchestration
- **LexRAG Core APIs** - 7-axis genomic analysis capabilities
