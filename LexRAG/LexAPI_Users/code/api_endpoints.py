"""
API Endpoints for LexAPI_Users
Main controller file - handles all user management endpoints following LexRAG pattern
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path
import tempfile
import os

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from code.database_manager import UserDatabaseManager
from code.user_manager import UserManager
from code.dna_processor import DNAProcessor
from code.questionnaire_engine import QuestionnaireEngine

# Initialize FastAPI
app = FastAPI(
    title="LexAPI_Users - User Management & Profile API",
    description="User registration, profile management, and DNA processing for LexRAG platform",
    version="1.0.0",
    docs_url="/docs"
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
db_manager = UserDatabaseManager()
user_manager = UserManager()
dna_processor = DNAProcessor()
questionnaire_engine = QuestionnaireEngine()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("[STARTUP] Initializing LexAPI_Users database...")
    if db_manager.initialize_user_database():
        print("[STARTUP] ✅ User database initialized successfully")
    else:
        print("[STARTUP] ❌ Database initialization failed")

@app.get("/health")
async def health_check():
    """Health check with database connectivity verification"""
    try:
        databases_status = db_manager.test_all_connections()
        
        return {
            "status": "healthy",
            "service": "LexAPI_Users",
            "capabilities": [
                "User registration and authentication",
                "DNA file processing (23andMe, AncestryDNA, VCF)",
                "Device data integration",
                "Adaptive questionnaires",
                "Profile completeness scoring",
                "Privacy and consent management"
            ],
            "databases": databases_status,
            "architecture": "modular_user_api",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/users/register")
async def register_user(user_data: Dict[str, Any]):
    """
    Register new user with profile data
    
    Expected format:
    {
        "email": "user@example.com",
        "demographics": {
            "age": 35,
            "sex": "female",
            "height_cm": 165,
            "weight_kg": 60,
            "ethnicity": "european"
        },
        "privacy_settings": {
            "data_sharing": false,
            "research_participation": true
        }
    }
    """
    try:
        result = user_manager.register_user(
            email=user_data.get("email"),
            demographics=user_data.get("demographics", {}),
            privacy_settings=user_data.get("privacy_settings", {})
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {e}")

@app.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """
    Get complete user profile with data summary
    
    Returns comprehensive user information including:
    - Basic demographics and contact info
    - Medical history and health data
    - Genomic data summary
    - Connected devices status
    - Questionnaire completion status
    """
    try:
        result = user_manager.get_user_profile(user_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile retrieval failed: {e}")

@app.get("/users/{user_id}/completeness")
async def get_profile_completeness(user_id: str):
    """
    Get user profile completeness score and recommendations
    
    Returns:
    - Completeness scores by category
    - Overall completeness percentage
    - Recommendations for improvement
    - Data gap identification
    """
    try:
        result = user_manager.calculate_profile_completeness(user_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Completeness calculation failed: {e}")

@app.post("/users/{user_id}/upload-dna")
async def upload_dna_file(user_id: str, file: UploadFile = File(...), file_type: str = "auto"):
    """
    Upload and process DNA file (23andMe, AncestryDNA, VCF, etc.)
    
    Supports:
    - 23andMe raw data files
    - AncestryDNA raw data files  
    - MyHeritage raw data files
    - VCF format files
    - Generic CSV files
    
    Processing includes:
    - Variant extraction and validation
    - Quality assessment
    - Integration with user profile
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = Path(tmp_file.name)
        
        # Process the DNA file
        result = dna_processor.process_dna_file(user_id, tmp_file_path, file_type)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "upload_status": "success",
            "file_info": {
                "original_filename": file.filename,
                "file_size_mb": round(len(content) / (1024 * 1024), 2),
                "content_type": file.content_type
            },
            "processing_results": result,
            "next_steps": [
                "Review genetic findings",
                "Complete adaptive questionnaire", 
                "Connect additional devices",
                "Schedule health consultation if needed"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Clean up on error
        try:
            os.unlink(tmp_file_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"DNA upload failed: {e}")

@app.get("/users/{user_id}/questionnaire")
async def get_adaptive_questionnaire(user_id: str):
    """
    Get adaptive questionnaire based on user's data and gaps
    
    Returns personalized questions based on:
    - DNA analysis findings
    - Missing profile data
    - Risk factors identified
    - Previous responses
    """
    try:
        result = questionnaire_engine.generate_adaptive_questionnaire(user_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Questionnaire generation failed: {e}")

@app.post("/users/{user_id}/questionnaire")
async def submit_questionnaire_responses(user_id: str, responses: List[Dict[str, Any]]):
    """
    Submit questionnaire responses
    
    Expected format:
    [
        {
            "question_id": "health_history_1",
            "question_text": "Do you have any chronic conditions?",
            "response_value": "Type 2 diabetes",
            "confidence_score": 0.9
        }
    ]
    """
    try:
        result = questionnaire_engine.submit_responses(user_id, responses)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response submission failed: {e}")

@app.post("/users/{user_id}/devices/sync")
async def sync_device_data(user_id: str, device_data: Dict[str, Any]):
    """
    Sync data from connected devices
    
    Supports:
    - Smartwatch data (heart rate, activity, sleep)
    - Fitness tracker data
    - Medical device data
    - Manual health measurements
    """
    try:
        # This would integrate with device APIs
        # For now, store the provided data
        conn = db_manager.get_user_db_connection(read_only=False)
        
        device_id = device_data.get("device_id", "manual_entry")
        device_type = device_data.get("device_type", "unknown")
        
        conn.execute("""
            INSERT OR REPLACE INTO user_devices 
            (user_id, device_id, device_type, device_name, last_sync, sync_status, data_points_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            user_id, device_id, device_type, 
            device_data.get("device_name", "Unknown Device"),
            datetime.now(), "synced",
            len(device_data.get("data_points", []))
        ])
        
        conn.close()
        
        return {
            "sync_status": "success",
            "device_id": device_id,
            "data_points_synced": len(device_data.get("data_points", [])),
            "sync_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Device sync failed: {e}")

@app.get("/users/{user_id}/genomics")
async def get_user_genomics(user_id: str, gene_filter: Optional[str] = None):
    """
    Get user's genomic data and analysis
    
    Returns:
    - Uploaded DNA files summary
    - Variant counts and quality metrics
    - Key genetic findings
    - Risk variants identified
    """
    try:
        conn = db_manager.get_user_db_connection()
        
        # Get genomic files
        genomic_files = conn.execute("""
            SELECT file_id, file_name, file_type, variant_count, 
                   quality_score, upload_date, processing_status
            FROM user_genomics
            WHERE user_id = ?
            ORDER BY upload_date DESC
        """, [user_id]).fetchall()
        
        conn.close()
        
        files_summary = []
        for file_data in genomic_files:
            files_summary.append({
                "file_id": file_data[0],
                "file_name": file_data[1],
                "file_type": file_data[2],
                "variant_count": file_data[3],
                "quality_score": file_data[4],
                "upload_date": str(file_data[5]),
                "processing_status": file_data[6]
            })
        
        # Calculate summary statistics
        total_variants = sum(f["variant_count"] or 0 for f in files_summary)
        avg_quality = sum(f["quality_score"] or 0 for f in files_summary) / len(files_summary) if files_summary else 0
        
        return {
            "user_id": user_id,
            "genomic_files": files_summary,
            "summary": {
                "total_files": len(files_summary),
                "total_variants": total_variants,
                "average_quality": round(avg_quality, 3),
                "processing_complete": all(f["processing_status"] == "processed" for f in files_summary)
            },
            "gene_filter": gene_filter,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Genomics data retrieval failed: {e}")

@app.put("/users/{user_id}/profile")
async def update_user_profile(user_id: str, profile_updates: Dict[str, Any]):
    """
    Update user profile information
    
    Allows updating:
    - Demographics
    - Medical history
    - Privacy settings
    - Contact information
    """
    try:
        conn = db_manager.get_user_db_connection(read_only=False)
        
        # Get current profile
        current_profile = conn.execute("""
            SELECT demographics, medical_history, privacy_settings
            FROM user_profiles
            WHERE user_id = ?
        """, [user_id]).fetchall()
        
        if not current_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Merge updates with existing data
        current_demo = json.loads(current_profile[0][0]) if current_profile[0][0] else {}
        current_medical = json.loads(current_profile[0][1]) if current_profile[0][1] else {}
        current_privacy = json.loads(current_profile[0][2]) if current_profile[0][2] else {}
        
        # Update fields
        if "demographics" in profile_updates:
            current_demo.update(profile_updates["demographics"])
        if "medical_history" in profile_updates:
            current_medical.update(profile_updates["medical_history"])
        if "privacy_settings" in profile_updates:
            current_privacy.update(profile_updates["privacy_settings"])
        
        # Save updates
        conn.execute("""
            UPDATE user_profiles 
            SET demographics = ?, medical_history = ?, privacy_settings = ?, last_updated = ?
            WHERE user_id = ?
        """, [
            json.dumps(current_demo),
            json.dumps(current_medical), 
            json.dumps(current_privacy),
            datetime.now(),
            user_id
        ])
        
        conn.close()
        
        return {
            "user_id": user_id,
            "update_status": "success",
            "updated_fields": list(profile_updates.keys()),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile update failed: {e}")

@app.delete("/users/{user_id}")
async def delete_user(user_id: str, confirmation: bool = False):
    """
    Delete user and all associated data
    
    Requires confirmation=true to prevent accidental deletion
    Removes all user data including:
    - Profile information
    - Genomic data
    - Device data
    - Questionnaire responses
    """
    if not confirmation:
        raise HTTPException(status_code=400, detail="Deletion requires confirmation=true")
    
    try:
        conn = db_manager.get_user_db_connection(read_only=False)
        
        # Delete from all tables
        tables = ["user_questionnaires", "user_devices", "user_genomics", "user_profiles"]
        deleted_counts = {}
        
        for table in tables:
            result = conn.execute(f"DELETE FROM {table} WHERE user_id = ?", [user_id])
            deleted_counts[table] = result.fetchone()[0] if hasattr(result, 'fetchone') else 0
        
        conn.close()
        
        return {
            "user_id": user_id,
            "deletion_status": "completed",
            "deleted_records": deleted_counts,
            "deletion_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User deletion failed: {e}")

@app.get("/users/{user_id}/data-status")
async def get_user_data_status(user_id: str):
    """
    Get comprehensive user data status for dashboard
    
    Returns:
    - Profile completeness
    - Data quality scores
    - Processing status
    - Recommendations
    """
    try:
        # Get profile completeness
        completeness = user_manager.calculate_profile_completeness(user_id)
        
        # Get profile data
        profile = user_manager.get_user_profile(user_id)
        
        if "error" in profile:
            raise HTTPException(status_code=404, detail=profile["error"])
        
        return {
            "user_id": user_id,
            "profile_completeness": completeness,
            "data_summary": profile.get("data_summary", {}),
            "status": {
                "profile_complete": completeness.get("completeness_percentage", 0) > 80,
                "dna_uploaded": profile["data_summary"]["genomic_files"] > 0,
                "devices_connected": profile["data_summary"]["devices_connected"] > 0,
                "questionnaire_complete": profile["data_summary"]["questionnaire_responses"] > 10
            },
            "recommendations": completeness.get("recommendations", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data status retrieval failed: {e}")

# Cleanup function
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    db_manager.close_connections()
