"""
Model Configuration for LexAPI_AIGateway
DNA Expert model and LexRAG API integration settings
"""

from pathlib import Path

# DNA Expert Model Settings
# LM Studio hosts the model on 1234; no local GGUF path is required anymore.
MODEL_SERVER_URL = "http://127.0.0.1:1234"
MODEL_PATH = None

# Model Configuration
MODEL_CONFIG = {
    "n_ctx": 32768,           # 32k context for complex genomic analysis
    "temperature": 0.3,       # Lower temperature for factual accuracy
    "top_p": 0.9,            # Nucleus sampling
    "max_tokens": 2048,      # Detailed genomic explanations
    "repeat_penalty": 1.1,    # Prevent repetition
    "stop": ["Human:", "User:", "</s>"]
}

# LexRAG API Endpoints
LEXRAG_APIS = {
    "users": "http://localhost:8007",
    "digital_twin": "http://localhost:8008",
    "genomics": "http://localhost:8001",
    "anatomics": "http://localhost:8002", 
    "literature": "http://localhost:8003",
    "metabolics": "http://localhost:8005",
    "populomics": "http://localhost:8006"
}

# API Settings
API_PORT = 8009
API_HOST = "0.0.0.0"

# Tool Execution Settings
TOOL_TIMEOUT = 60
MAX_TOOL_CALLS = 12  # Allow up to 12 iterations for complex agentic reasoning
ENABLE_TOOL_CHAINING = True

# System Prompt Settings
SYSTEM_PROMPT_PATH = Path("data/system_prompts/dna_expert_prompt.md")
TOOL_DEFINITIONS_PATH = Path("data/tools/lexrag_tools.json")

# Chat Settings
MAX_CONVERSATION_HISTORY = 20
CONVERSATION_TIMEOUT = 3600  # 1 hour

def get_model_config():
    """Get complete model configuration"""
    return {
        "model_server": MODEL_SERVER_URL,
        "model_path": MODEL_PATH,
        "model_config": MODEL_CONFIG,
        "lexrag_apis": LEXRAG_APIS,
        "system_prompt": SYSTEM_PROMPT_PATH,
        "tool_definitions": TOOL_DEFINITIONS_PATH
    }
