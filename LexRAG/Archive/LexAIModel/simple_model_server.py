"""
Simple DNA Expert Model Server
Simplified version with better error handling
"""

import sys
from pathlib import Path

def test_dependencies():
    """Test if all dependencies are available"""
    print("🔍 Testing dependencies...")
    
    try:
        import llama_cpp
        print("✅ llama_cpp available")
    except ImportError:
        print("❌ llama_cpp not available")
        return False
    
    try:
        from llama_cpp import Llama
        print("✅ Llama class available")
    except ImportError:
        print("❌ Llama class not available")
        return False
    
    try:
        from llama_cpp.server import create_app
        print("✅ Server module available")
    except ImportError:
        print("❌ Server module not available")
        return False
    
    return True

def start_simple_server():
    """Start simplified model server"""
    
    print("🧬 Simple DNA Expert Model Server")
    print("="*50)
    
    # Check model file
    model_path = Path("qwen3-dna-expert.Q4_K_M.gguf")
    if not model_path.exists():
        print(f"❌ Model file not found: {model_path}")
        print("Please ensure the model file is in the LexAIModel directory")
        input("Press Enter to exit...")
        return
    
    print(f"✅ Model file found: {model_path.name} ({model_path.stat().st_size / (1024**3):.1f}GB)")
    
    # Test dependencies
    if not test_dependencies():
        print("\n❌ Dependencies missing!")
        print("Run: pip install llama-cpp-python[server]")
        input("Press Enter to exit...")
        return
    
    print("\n🚀 Starting model server...")
    
    try:
        from llama_cpp import Llama
        from llama_cpp.server import create_app
        import uvicorn
        
        print("📥 Loading model... (this may take 30-60 seconds)")
        
        # Load model with basic settings
        llm = Llama(
            model_path=str(model_path),
            n_ctx=8192,           # Smaller context initially
            n_gpu_layers=0,       # CPU only initially
            verbose=True,         # Show loading progress
            n_threads=4           # Conservative thread count
        )
        
        print("✅ Model loaded successfully!")
        
        # Create server app
        app = create_app(llm)
        
        print("🌐 Starting server on port 8010...")
        print("📝 Access at: http://localhost:8010")
        
        # Start server
        uvicorn.run(app, host="0.0.0.0", port=8010, log_level="info")
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if port 8010 is available")
        print("2. Ensure you have enough RAM (10GB+ recommended)")
        print("3. Try restarting your computer if issues persist")
        input("Press Enter to exit...")

if __name__ == "__main__":
    start_simple_server()
