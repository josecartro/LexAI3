"""
Correct DNA Expert Model Server
Using proper llama-cpp-python server approach from documentation
"""

import subprocess
import sys
from pathlib import Path
import time

def start_correct_server():
    """Start model server using the documented llama-cpp-python approach"""
    
    model_path = Path("qwen3-dna-expert.Q4_K_M.gguf")
    
    print("🧬 Correct DNA Expert Model Server")
    print("="*60)
    print(f"📁 Model: {model_path.name}")
    print(f"📊 Size: {model_path.stat().st_size / (1024**3):.1f}GB")
    print("🔧 Method: llama-cpp-python server module")
    print("📖 Based on: https://llama-cpp-python.readthedocs.io/en/latest/")
    print("="*60)
    
    if not model_path.exists():
        print(f"❌ Model file not found: {model_path}")
        return False
    
    try:
        # Test if llama_cpp.server module is available
        import llama_cpp.server
        print("✅ llama_cpp.server module available")
        
        # Build command using documented approach
        cmd = [
            sys.executable, "-m", "llama_cpp.server",
            "--model", str(model_path),
            "--host", "0.0.0.0",
            "--port", "8010",
            "--n_ctx", "32768",           # 32k context
            "--chat_format", "qwen",      # Qwen3 format
            "--n_threads", "8",           # CPU threads
            "--verbose"                   # Show detailed info
        ]
        
        print("🚀 Starting server with command:")
        print(f"   {' '.join(cmd)}")
        print("\n📥 Loading model... (30-60 seconds)")
        print("🌐 Server will be available at: http://localhost:8010")
        print("📖 API docs will be at: http://localhost:8010/docs")
        print("\n" + "="*60)
        
        # Start the server
        subprocess.run(cmd, check=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Try: pip install llama-cpp-python[server] --force-reinstall")
        return False
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting DNA Expert Model Server using documented approach...")
    start_correct_server()
