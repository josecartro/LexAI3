"""
Twin Manager for LexAPI_DigitalTwin
Creates and manages user digital twins with data overlay logic
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from code.database_manager import DigitalTwinDatabaseManager
from code.reference_models import ReferenceModelManager
from code.data_overlay import DataOverlayEngine
from config.database_config import DIGITAL_TWIN_DATABASE

class TwinManager:
    """Manages user digital twin creation and updates"""
    
    def __init__(self):
        self.db_manager = DigitalTwinDatabaseManager()
        self.reference_manager = ReferenceModelManager()
        self.overlay_engine = DataOverlayEngine()
        
    def create_user_twin(self, user_id: str) -> Dict[str, Any]:
        """Create digital twin for user with data overlay"""
        try:
            # Get user data from user database
            user_data = self._get_user_data(user_id)
            
            if "error" in user_data:
                return user_data
            
            # Get appropriate reference model
            user_sex = user_data.get("demographics", {}).get("sex", "unknown")
            user_ancestry = user_data.get("demographics", {}).get("ethnicity", "mixed_european")
            
            # Try population model first, fallback to reference
            reference_model = self.reference_manager.get_population_model(user_ancestry, user_sex)
            if "error" in reference_model:
                reference_model = self.reference_manager.get_reference_model(user_sex)
            
            if "error" in reference_model:
                return {"error": "Could not get reference model"}
            
            # Create composite digital twin using data overlay
            digital_twin = self.overlay_engine.create_composite_twin(user_data, reference_model)
            
            # Store digital twin in ClickHouse
            client = self.db_manager.get_clickhouse_client()
            
            client.insert('digital_twin_db.user_twins', [(
                user_id,
                json.dumps(digital_twin["twin_data"]),
                json.dumps(digital_twin["data_sources"]),
                json.dumps(digital_twin["confidence_scores"]),
                digital_twin["completeness_score"],
                datetime.now()
            )])
            
            return {
                "user_id": user_id,
                "twin_creation_status": "success",
                "digital_twin": digital_twin,
                "creation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Digital twin creation failed: {e}"}
    
    def get_user_twin(self, user_id: str) -> Dict[str, Any]:
        """Get existing digital twin or create if doesn't exist"""
        try:
            client = self.db_manager.get_clickhouse_client()
            
            # Check if twin exists
            existing_twin = client.query(f"""
                SELECT twin_data, data_sources, confidence_scores, completeness_score, last_updated
                FROM digital_twin_db.user_twins
                WHERE user_id = '{user_id}'
                ORDER BY last_updated DESC
                LIMIT 1
            """).result_rows
            
            if existing_twin:
                twin_data = existing_twin[0]
                return {
                    "user_id": user_id,
                    "twin_data": json.loads(twin_data[0]),
                    "data_sources": json.loads(twin_data[1]),
                    "confidence_scores": json.loads(twin_data[2]),
                    "completeness_score": twin_data[3],
                    "last_updated": str(twin_data[4]),
                    "twin_status": "existing"
                }
            else:
                # Create new twin
                new_twin = self.create_user_twin(user_id)
                
                # Fallback for non-existent users (e.g. demo accounts)
                if "error" in new_twin and "User not found" in new_twin["error"]:
                    return self._create_anonymous_twin(user_id)
                    
                if "error" not in new_twin:
                    new_twin["twin_status"] = "newly_created"
                return new_twin
                
        except Exception as e:
            print(f"[ERROR] Twin retrieval failed: {e}")
            return self._create_anonymous_twin(user_id)

    def _create_anonymous_twin(self, user_id: str) -> Dict[str, Any]:
        """Create a default anonymous twin for demo/unregistered users"""
        return {
            "user_id": user_id,
            "twin_data": {
                "demographics": {"sex": "unknown", "age": "unknown"},
                "biomarkers": {},
                "genetics": {}
            },
            "data_sources": {"general": "reference_model"},
            "confidence_scores": {"overall": 0.1},
            "completeness_score": 0.1,
            "twin_status": "anonymous_fallback"
        }
    
    def update_user_twin(self, user_id: str) -> Dict[str, Any]:
        """Update existing digital twin with latest user data"""
        try:
            # Get fresh user data
            user_data = self._get_user_data(user_id)
            
            if "error" in user_data:
                return user_data
            
            # Get current twin
            current_twin = self.get_user_twin(user_id)
            
            if "error" in current_twin:
                return current_twin
            
            # Get reference model
            user_sex = user_data.get("demographics", {}).get("sex", "unknown")
            reference_model = self.reference_manager.get_reference_model(user_sex)
            
            # Update twin with new data
            updated_twin = self.overlay_engine.create_composite_twin(user_data, reference_model)
            
            # Update in database
            client = self.db_manager.get_clickhouse_client()
            
            client.command(f"""
                ALTER TABLE {DIGITAL_TWIN_DATABASE}.user_twins
                UPDATE 
                    twin_data = '{json.dumps(updated_twin["twin_data"])}',
                    data_sources = '{json.dumps(updated_twin["data_sources"])}',
                    confidence_scores = '{json.dumps(updated_twin["confidence_scores"])}',
                    completeness_score = {updated_twin["completeness_score"]},
                    last_updated = now()
                WHERE user_id = '{user_id}'
            """)
            
            return {
                "user_id": user_id,
                "update_status": "success",
                "digital_twin": updated_twin,
                "update_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Twin update failed: {e}"}
    
    def _get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Get user data from user database"""
        try:
            conn = self.db_manager.get_user_db_connection()
            
            # Get user profile
            profile_data = conn.execute("""
                SELECT demographics, medical_history, privacy_settings
                FROM user_profiles
                WHERE user_id = ?
            """, [user_id]).fetchall()
            
            if not profile_data:
                conn.close()
                return {"error": "User not found"}
            
            profile = profile_data[0]
            
            # Get genomic data summary
            genomics_data = conn.execute("""
                SELECT file_type, variant_count, quality_score
                FROM user_genomics
                WHERE user_id = ? AND processing_status = 'processed'
            """, [user_id]).fetchall()
            
            # Get questionnaire responses
            questionnaire_data = conn.execute("""
                SELECT question_category, response_value, confidence_score
                FROM user_questionnaires
                WHERE user_id = ?
            """, [user_id]).fetchall()
            
            # Get device data
            device_data = conn.execute("""
                SELECT device_type, last_sync, data_points_count
                FROM user_devices
                WHERE user_id = ?
            """, [user_id]).fetchall()
            
            conn.close()
            
            return {
                "user_id": user_id,
                "demographics": json.loads(profile[0]) if profile[0] else {},
                "medical_history": json.loads(profile[1]) if profile[1] else {},
                "privacy_settings": json.loads(profile[2]) if profile[2] else {},
                "genomic_data": [
                    {
                        "file_type": g[0],
                        "variant_count": g[1],
                        "quality_score": g[2]
                    } for g in genomics_data
                ],
                "questionnaire_responses": [
                    {
                        "category": q[0],
                        "response": q[1],
                        "confidence": q[2]
                    } for q in questionnaire_data
                ],
                "device_data": [
                    {
                        "device_type": d[0],
                        "last_sync": str(d[1]),
                        "data_points": d[2]
                    } for d in device_data
                ]
            }
            
        except Exception as e:
            return {"error": f"User data retrieval failed: {e}"}
    
    def get_twin_confidence_analysis(self, user_id: str) -> Dict[str, Any]:
        """Get detailed confidence analysis for user's digital twin"""
        try:
            twin = self.get_user_twin(user_id)
            
            if "error" in twin:
                return twin
            
            confidence_scores = twin.get("confidence_scores", {})
            data_sources = twin.get("data_sources", {})
            
            # Analyze confidence by category
            confidence_analysis = {
                "overall_confidence": twin.get("completeness_score", 0),
                "confidence_breakdown": {},
                "data_source_breakdown": {},
                "recommendations": []
            }
            
            for category, confidence in confidence_scores.items():
                confidence_analysis["confidence_breakdown"][category] = {
                    "confidence_score": confidence,
                    "confidence_level": (
                        "high" if confidence >= 0.8 else
                        "medium" if confidence >= 0.6 else
                        "low"
                    ),
                    "data_source": data_sources.get(category, "unknown")
                }
                
                # Generate recommendations for low confidence areas
                if confidence < 0.6:
                    confidence_analysis["recommendations"].append(
                        f"Improve {category} data by providing more specific information"
                    )
            
            return confidence_analysis
            
        except Exception as e:
            return {"error": f"Confidence analysis failed: {e}"}
