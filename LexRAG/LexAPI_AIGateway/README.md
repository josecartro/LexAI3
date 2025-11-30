# LexAPI_AIGateway - AI Model Integration API

## Overview
AI model integration and query orchestration API that connects the DNA-trained Qwen3 model with the LexRAG platform. Provides intelligent genomic analysis through conversational AI with access to 4.4 billion genomic records.

## Features
- **DNA Expert Model Integration** - Qwen3-14B with specialized genomic training
- **Tool Orchestration** - Dynamic access to all LexRAG APIs based on query needs
- **Digital Twin Awareness** - Uses Adam/Eve models when user data missing
- **Conversation Management** - Multi-turn dialogue with context preservation
- **Confidence Scoring** - Transparent data source quality assessment
- **Cross-Axis Analysis** - Intelligent integration across all 7 biological axes

## Architecture
Following LexRAG modular pattern:
- `code/api_endpoints.py` - Main FastAPI endpoints
- `code/ai_orchestrator.py` - AI model communication and query orchestration
- `code/tool_executor.py` - LexRAG API tool execution
- `config/model_config.py` - AI model and API configuration

## Dependencies
- **DNA Expert Model Server** (Port 1234) - LM Studio serving Qwen3-14B
- **LexRAG APIs** (Ports 8001-8008) - All 7 APIs must be running
- **Digital Twin System** - LexAPI_DigitalTwin for user context
- **User Management** - LexAPI_Users for profile data

## API Endpoints
- `POST /chat/{user_id}` - Chat with DNA expert using user context
- `GET /chat/{user_id}/history` - Get conversation history
- `POST /chat/{user_id}/new-conversation` - Start new conversation
- `GET /tools/available` - Get available tool catalog
- `GET /health` - Health check with model and API status

## Chat Interface
```json
POST /chat/{user_id}
{
    "message": "What does my BRCA1 variant mean?",
    "conversation_id": "optional_uuid"
}

Response:
{
    "conversation_id": "uuid",
    "ai_response": {
        "response": "Based on your genetic data...",
        "confidence_level": "high",
        "data_sources": {...},
        "recommendations": [...]
    }
}
```

## Usage
```bash
# Start LM Studio with DNA Expert Model first
# 1. Open LM Studio
# 2. Load qwen3-dna-expert.Q4_K_M.gguf
# 3. Start Server on port 1234

# Then start AI Gateway
api_startup.bat

# Test chat
curl -X POST http://localhost:8009/chat/user123 \
  -H "Content-Type: application/json" \
  -d '{"message": "What should I know about my genetics?"}'
```

## Integration
Designed to work with:
- **DNA Expert Model** - Specialized Qwen3-14B with genomics training (via LM Studio)
- **LexRAG Platform** - All 7 APIs with 4.4B genomic records
- **Digital Twin System** - Adam/Eve models with user data overlay
- **Frontend Applications** - Chat interfaces and user dashboards

## Agentic Capabilities
- **Multi-step reasoning** - Up to 12 tool call iterations for complex questions
- **Tool chaining** - AI can freely explore data sources to build comprehensive answers
- **Cross-axis integration** - Combines genomics, anatomy, literature, and more
- **Adaptive questioning** - AI determines what data it needs dynamically
