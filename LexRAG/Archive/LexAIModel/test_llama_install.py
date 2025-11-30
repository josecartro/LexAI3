"""
Test llama-cpp-python installation
"""

print("Testing llama-cpp-python installation...")

try:
    import llama_cpp
    print("✅ llama_cpp imported successfully")
    print(f"   Version: {llama_cpp.__version__ if hasattr(llama_cpp, '__version__') else 'unknown'}")
    
    from llama_cpp import Llama
    print("✅ Llama class imported successfully")
    
    from llama_cpp.server import create_app
    print("✅ Server module imported successfully")
    
    print("\n🎉 All llama-cpp-python components available!")
    print("✅ Ready to run DNA Expert model server")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Try reinstalling: pip install llama-cpp-python[server]")
    
except Exception as e:
    print(f"❌ Other error: {e}")

input("Press Enter to continue...")
