"""
Test DigitalTwin API Startup
Identify startup issues
"""

print("Testing DigitalTwin API imports...")

try:
    print("1. Testing basic imports...")
    import sys
    from pathlib import Path
    print("   Basic imports: OK")
    
    print("2. Testing FastAPI import...")
    from fastapi import FastAPI
    print("   FastAPI: OK")
    
    print("3. Testing config imports...")
    sys.path.append(str(Path(__file__).parent))
    from config.database_config import CLICKHOUSE_HOST
    print(f"   Config: OK - ClickHouse host: {CLICKHOUSE_HOST}")
    
    print("4. Testing database manager...")
    from code.database_manager import DigitalTwinDatabaseManager
    print("   Database manager import: OK")
    
    print("5. Testing database manager initialization...")
    db_manager = DigitalTwinDatabaseManager()
    print("   Database manager init: OK")
    
    print("6. Testing other components...")
    from code.twin_manager import TwinManager
    from code.reference_models import ReferenceModelManager
    print("   All components: OK")
    
    print("\\n7. Testing FastAPI app creation...")
    app = FastAPI(title="Test DigitalTwin API")
    print("   FastAPI app: OK")
    
    print("\\nSUCCESS: All imports and initialization working!")
    print("DigitalTwin API should start properly")
    
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
except Exception as e:
    print(f"OTHER ERROR: {e}")

input("Press Enter to continue...")
