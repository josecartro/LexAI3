"""
API Endpoints for LexAPI_AIGateway
Main controller file - handles AI model integration endpoints following LexRAG pattern
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path
import uuid
import json
import asyncio
from queue import Queue
from threading import Thread

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.ai_orchestrator import DNAExpertOrchestrator
from code.tool_executor import ToolExecutor
from config.model_config import MODEL_SERVER_URL

# Initialize FastAPI
app = FastAPI(
    title="LexAPI_AIGateway - AI Model Integration API",
    description="DNA Expert model integration with LexRAG platform for intelligent genomic analysis",
    version="1.0.0",
    docs_url="/docs"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI components
ai_orchestrator = DNAExpertOrchestrator()
tool_executor = ToolExecutor()

@app.get("/health")
async def health_check():
    """Health check with AI model and LexRAG API connectivity verification"""
    try:
        # Test AI model server connection (LM Studio)
        model_status = "unknown"
        try:
            import requests
            model_response = requests.get(f"{MODEL_SERVER_URL}/v1/models", timeout=5)
            model_status = "connected" if model_response.status_code == 200 else "disconnected"
        except:
            model_status = "disconnected"
        
        # Test LexRAG API connections
        api_status = {}
        for api_name, api_url in ai_orchestrator.tool_executor.apis.items():
            try:
                response = requests.get(f"{api_url}/health", timeout=5)
                api_status[api_name] = "connected" if response.status_code == 200 else "error"
            except:
                api_status[api_name] = "disconnected"
        
        return {
            "status": "healthy" if model_status == "connected" else "degraded",
            "service": "LexAPI_AIGateway",
            "capabilities": [
                "DNA Expert model integration (Qwen3-14B + DNA training)",
                "LexRAG tool orchestration (7 APIs)",
                "Digital twin aware analysis",
                "Multi-axis genomic reasoning",
                "Conversation management",
                "Confidence scoring and transparency"
            ],
            "ai_model": {
                "status": model_status,
                "server": "LM Studio",
                "port": 1234,
                "model": "qwen3-dna-expert.Q4_K_M.gguf",
                "context_length": "32k tokens",
                "specialization": "DNA genomics",
                "api_compatible": "OpenAI v1"
            },
            "lexrag_apis": api_status,
            "architecture": "modular_ai_gateway",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/chat/{user_id}")
async def chat_with_dna_expert(user_id: str, chat_request: Dict[str, Any]):
    """
    Chat with DNA Expert model using user's digital twin context
    
    Request format:
    {
        "message": "What does my BRCA1 variant mean?",
        "conversation_id": "optional_conversation_id"
    }
    
    Returns comprehensive genomic analysis with:
    - AI model response with DNA expertise
    - Tool execution results from LexRAG APIs
    - User context and confidence scoring
    - Data source transparency
    """
    try:
        message = chat_request.get("message", "")
        conversation_id = chat_request.get("conversation_id")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Process query with AI orchestrator
        result = ai_orchestrator.process_user_query(user_id, message, conversation_id)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "query": message,
            "ai_response": result,
            "processing_info": {
                "model_used": "qwen3-dna-expert",
                "tools_executed": "dynamic_based_on_query",
                "data_integration": "7_axis_lexrag_platform"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {e}")

@app.post("/chat/{user_id}/stream")
async def chat_with_dna_expert_stream(user_id: str, chat_request: Dict[str, Any]):
    """
    Stream chat with DNA Expert model using Server-Sent Events
    
    This endpoint provides real-time progress updates as the AI:
    - Loads user context
    - Reasons through the problem
    - Calls tools to gather data
    - Formulates the final response
    
    Returns: Server-Sent Event stream with progress updates
    """
    message = chat_request.get("message", "")
    conversation_id = chat_request.get("conversation_id")
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Generate conversation ID if not provided
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    
    async def generate_sse_updates():
        """Generator function for SSE updates"""
        # Use thread-safe queue for sync/async communication
        progress_queue = Queue()
        
        def progress_callback(update: Dict):
            """Callback to receive progress updates from AI orchestrator"""
            try:
                # Put update in thread-safe queue (works from sync context)
                progress_queue.put(update)
            except Exception as e:
                print(f"Error in progress callback: {e}")
        
        # Process query in background thread
        def process_query_sync():
            try:
                result = ai_orchestrator.process_user_query(
                    user_id, 
                    message, 
                    conversation_id,
                    progress_callback=progress_callback
                )
                # Signal completion
                progress_queue.put({"status": "done", "result": result})
            except Exception as e:
                print(f"Error in process_query_sync: {e}")
                import traceback
                traceback.print_exc()
                progress_queue.put({"status": "error", "error": str(e)})
        
        # Start processing in background thread
        thread = Thread(target=process_query_sync, daemon=True)
        thread.start()
        
        # Send initial event
        yield f"data: {json.dumps({'status': 'connected', 'conversation_id': conversation_id})}\n\n"
        
        # Stream progress updates
        done = False
        while not done:
            try:
                # Check queue with timeout (non-blocking)
                import queue
                try:
                    update = progress_queue.get(timeout=0.1)
                    
                    # Send update as SSE
                    yield f"data: {json.dumps(update)}\n\n"
                    
                    # Check if done
                    if update.get("status") == "done":
                        done = True
                    elif update.get("status") == "error":
                        done = True
                        
                except queue.Empty:
                    # Send keepalive
                    yield f": keepalive\n\n"
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                print(f"Error in stream loop: {e}")
                yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
                done = True
        
        # Wait for thread to complete
        thread.join(timeout=5)
    
    return StreamingResponse(
        generate_sse_updates(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

@app.get("/chat/{user_id}/history")
async def get_conversation_history(user_id: str, conversation_id: str = None):
    """
    Get conversation history for user
    
    Returns:
    - Recent conversation exchanges
    - Context for continued conversation
    - User interaction patterns
    """
    try:
        if conversation_id:
            # Get specific conversation
            history = ai_orchestrator.conversation_history.get(conversation_id, [])
        else:
            # Get all conversations for user (would need user-conversation mapping)
            history = []
        
        return {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "history": history,
            "total_exchanges": len(history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {e}")

@app.post("/chat/{user_id}/new-conversation")
async def start_new_conversation(user_id: str):
    """
    Start new conversation with fresh context
    
    Returns:
    - New conversation ID
    - User context summary
    - Suggested starter questions
    """
    try:
        # Generate new conversation ID
        conversation_id = str(uuid.uuid4())
        
        # Get user context for suggestions
        user_twin = tool_executor.get_user_digital_twin(user_id)
        
        # Generate starter questions based on user data
        starter_questions = self._generate_starter_questions(user_twin)
        
        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "user_context_summary": {
                "data_completeness": f"{user_twin.get('completeness_score', 0)*100:.1f}%",
                "has_genomic_data": user_twin.get("completeness_score", 0) > 0.3,
                "confidence_level": "high" if user_twin.get("completeness_score", 0) > 0.8 else "medium" if user_twin.get("completeness_score", 0) > 0.5 else "low"
            },
            "starter_questions": starter_questions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"New conversation creation failed: {e}")

@app.get("/tools/available")
async def get_available_tools():
    """
    Get list of available tools for AI model
    
    Returns comprehensive tool catalog for:
    - User data access
    - Genomic analysis
    - Cross-axis integration
    - Risk assessment
    """
    try:
        tools = {
            "user_data_tools": [
                {
                    "name": "get_user_digital_twin",
                    "description": "Get complete user model with Adam/Eve overlay and confidence scores",
                    "parameters": ["user_id"],
                    "endpoint": "/twin/{user_id}/model"
                },
                {
                    "name": "get_user_genomics", 
                    "description": "Get user's genetic variants and DNA analysis",
                    "parameters": ["user_id", "gene_filter (optional)"],
                    "endpoint": "/users/{user_id}/genomics"
                }
            ],
            "genomic_analysis_tools": [
                {
                    "name": "analyze_gene",
                    "description": "Comprehensive gene analysis using 4.4B genomic records",
                    "parameters": ["gene_symbol", "user_id (optional)"],
                    "endpoint": "/analyze/gene/{gene_symbol}"
                },
                {
                    "name": "analyze_variant",
                    "description": "Specific genetic variant interpretation",
                    "parameters": ["variant_id", "user_id (optional)"],
                    "endpoint": "/analyze/variant/{variant_id}"
                }
            ],
            "cross_axis_tools": [
                {
                    "name": "cross_axis_analysis",
                    "description": "Multi-axis biological analysis across all 7 systems",
                    "parameters": ["query", "axes", "user_id (optional)"],
                    "endpoint": "Multiple APIs coordinated"
                },
                {
                    "name": "risk_assessment",
                    "description": "Comprehensive health risk analysis",
                    "parameters": ["user_id", "condition (optional)"],
                    "endpoint": "Multiple APIs coordinated"
                }
            ]
        }
        
        return {
            "available_tools": tools,
            "total_tools": sum(len(category) for category in tools.values()),
            "platform_integration": "LexRAG 7-axis platform with 4.4B records",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool catalog retrieval failed: {e}")

def _generate_starter_questions(user_twin: Dict[str, Any]) -> List[str]:
    """Generate personalized starter questions based on user data"""
    
    completeness = user_twin.get("completeness_score", 0)
    has_genomic_data = completeness > 0.3
    
    if has_genomic_data:
        return [
            "What do my genetic variants mean for my health?",
            "What medications should I avoid based on my genetics?", 
            "What is my risk for common diseases?",
            "How do my genes affect my response to exercise and diet?",
            "Should my family members get genetic testing?"
        ]
    else:
        return [
            "What can genetic testing tell me about my health?",
            "How do I interpret genetic test results?",
            "What are the most important genes to test for?",
            "How does family history affect my genetic risk?",
            "What should I know about pharmacogenomics?"
        ]

# Cleanup function
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown"""
    # Any cleanup needed for AI model or API connections
    pass
