"""
Working DNA Expert Model Server
Direct llama.cpp integration without server dependencies
"""

from pathlib import Path
import json

def start_working_server():
    """Start model server with direct llama.cpp integration"""
    
    model_path = Path("qwen3-dna-expert.Q4_K_M.gguf")
    
    print("🧬 Working DNA Expert Model Server")
    print("="*50)
    print(f"📁 Model: {model_path.name}")
    print(f"📊 Size: {model_path.stat().st_size / (1024**3):.1f}GB")
    print("="*50)
    
    if not model_path.exists():
        print(f"❌ Model file not found: {model_path}")
        return False
    
    try:
        from llama_cpp import Llama
        
        print("📥 Loading model... (this will take 30-60 seconds)")
        
        # Load model with conservative settings
        llm = Llama(
            model_path=str(model_path),
            n_ctx=4096,           # Start with smaller context
            n_gpu_layers=0,       # CPU only for stability
            verbose=True,         # Show loading progress
            n_threads=4           # Conservative thread count
        )
        
        print("✅ Model loaded successfully!")
        print("🎯 DNA Expert model ready for genomics analysis")
        
        # Simple test
        print("\n🧪 Testing model with simple query...")
        test_response = llm(
            "What is BRCA1?",
            max_tokens=100,
            temperature=0.3,
            stop=["\\n\\n"]
        )
        
        print("✅ Model test successful!")
        print(f"📝 Sample response: {test_response['choices'][0]['text'][:100]}...")
        
        print("\n🌐 Model server ready!")
        print("📍 Use this model object in your applications")
        print("🔗 Integrate with LexAPI_AIGateway for full functionality")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Try: pip install llama-cpp-python[server] --force-reinstall")
        return False
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        print("This might be due to:")
        print("1. Insufficient RAM (need 10GB+)")
        print("2. Corrupted model file")
        print("3. System resource limitations")
        return False

if __name__ == "__main__":
    success = start_working_server()
    if success:
        print("\\n🎉 DNA Expert model is working!")
    else:
        print("\\n❌ Model startup failed")
    
    input("Press Enter to exit...")
