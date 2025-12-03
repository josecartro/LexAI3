"""
DNA Expert Model Server
Runs the Qwen3-14B DNA-trained model using llama.cpp
"""

import uvicorn
from pathlib import Path
import sys
import os

def start_dna_expert_server():
    """Start the DNA expert model server using llama.cpp"""
    
    model_path = Path("qwen3-dna-expert.Q4_K_M.gguf")
    
    if not model_path.exists():
        print(f"❌ Model file not found: {model_path}")
        print("Please ensure qwen3-dna-expert.Q4_K_M.gguf is in the LexAIModel directory")
        return
    
    print("🧬 Starting DNA Expert Model Server...")
    print(f"📁 Model: {model_path.name} (8.4GB)")
    print("🔧 Runtime: llama.cpp with Python bindings")
    print("🌐 Port: 8010")
    print("📝 Context: 32k tokens")
    print("🎯 Specialization: DNA genomics analysis")
    print("="*60)
    
    try:
        # Import llama-cpp-python
        from llama_cpp.server import create_app
        from llama_cpp import Llama
        
        # Initialize model with optimal settings for genomics
        llm = Llama(
            model_path=str(model_path),
            n_ctx=32768,          # 32k context for complex genomic analysis
            n_gpu_layers=-1,      # Use GPU if available
            verbose=False,        # Quiet operation
            chat_format="qwen",   # Qwen3 chat format
            n_threads=8,          # Optimize for system
            use_mmap=True,        # Memory mapping for efficiency
            use_mlock=True,       # Lock memory to prevent swapping
            seed=-1               # Random seed
        )
        
        print("✅ Model loaded successfully!")
        print("🚀 Starting server...")
        
        # Create FastAPI app with the model
        model_app = create_app(llm)
        
        # Run server
        uvicorn.run(model_app, host="0.0.0.0", port=8010)
        
    except ImportError:
        print("❌ llama-cpp-python not installed!")
        print("Install with: pip install llama-cpp-python[server]")
        return
    except Exception as e:
        print(f"❌ Model server startup failed: {e}")
        return

if __name__ == "__main__":
    start_dna_expert_server()
