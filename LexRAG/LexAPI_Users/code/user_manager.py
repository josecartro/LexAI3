"""
User Manager for LexAPI_Users
Handles user registration, profile management, and data operations
"""

import uuid
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from code.database_manager import UserDatabaseManager

class UserManager:
    """Manages user profiles and operations"""
    
    def __init__(self):
        self.db_manager = UserDatabaseManager()
        
    def register_user(self, email: str, demographics: Dict, privacy_settings: Dict = None) -> Dict[str, Any]:
        """Register new user with profile data"""
        try:
            # Generate secure user ID
            user_id = str(uuid.uuid4())
            
            # Default privacy settings
            if privacy_settings is None:
                privacy_settings = {
                    "data_sharing": False,
                    "research_participation": False,
                    "marketing_emails": False,
                    "data_retention_years": 5
                }
            
            # Create user profile
            conn = self.db_manager.get_user_db_connection(read_only=False)
            
            conn.execute("""
                INSERT INTO user_profiles (user_id, email, demographics, privacy_settings)
                VALUES (?, ?, ?, ?)
            """, [user_id, email, json.dumps(demographics), json.dumps(privacy_settings)])
            
            conn.close()
            
            return {
                "user_id": user_id,
                "email": email,
                "status": "registered",
                "next_steps": ["upload_dna", "complete_questionnaire", "sync_devices"],
                "created_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Registration failed: {e}"}
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get complete user profile"""
        try:
            conn = self.db_manager.get_user_db_connection()
            
            # Get basic profile
            profile_data = conn.execute("""
                SELECT email, demographics, medical_history, privacy_settings, created_date, last_updated
                FROM user_profiles
                WHERE user_id = ?
            """, [user_id]).fetchall()
            
            if not profile_data:
                conn.close()
                return {"error": "User not found"}
            
            profile = profile_data[0]
            
            # Get genomic data summary
            genomics_data = conn.execute("""
                SELECT COUNT(*) as file_count, 
                       SUM(variant_count) as total_variants,
                       AVG(quality_score) as avg_quality
                FROM user_genomics
                WHERE user_id = ?
            """, [user_id]).fetchall()
            
            # Get device data summary
            devices_data = conn.execute("""
                SELECT COUNT(*) as device_count,
                       MAX(last_sync) as last_sync
                FROM user_devices
                WHERE user_id = ?
            """, [user_id]).fetchall()
            
            # Get questionnaire completion
            questionnaire_data = conn.execute("""
                SELECT COUNT(*) as responses_count,
                       COUNT(DISTINCT question_category) as categories_completed
                FROM user_questionnaires
                WHERE user_id = ?
            """, [user_id]).fetchall()
            
            conn.close()
            
            genomics = genomics_data[0] if genomics_data else (0, 0, 0)
            devices = devices_data[0] if devices_data else (0, None)
            questionnaire = questionnaire_data[0] if questionnaire_data else (0, 0)
            
            return {
                "user_id": user_id,
                "email": profile[0],
                "demographics": json.loads(profile[1]) if profile[1] else {},
                "medical_history": json.loads(profile[2]) if profile[2] else {},
                "privacy_settings": json.loads(profile[3]) if profile[3] else {},
                "created_date": str(profile[4]),
                "last_updated": str(profile[5]),
                "data_summary": {
                    "genomic_files": genomics[0],
                    "total_variants": genomics[1] or 0,
                    "avg_quality_score": round(genomics[2] or 0, 3),
                    "devices_connected": devices[0],
                    "last_device_sync": str(devices[1]) if devices[1] else None,
                    "questionnaire_responses": questionnaire[0],
                    "questionnaire_categories": questionnaire[1]
                }
            }
            
        except Exception as e:
            return {"error": f"Profile retrieval failed: {e}"}
    
    def calculate_profile_completeness(self, user_id: str) -> Dict[str, Any]:
        """Calculate user profile completeness score"""
        try:
            profile = self.get_user_profile(user_id)
            if "error" in profile:
                return profile
            
            # Calculate completeness scores
            demographics_score = 0.0
            medical_history_score = 0.0
            genomics_score = 0.0
            devices_score = 0.0
            questionnaire_score = 0.0
            
            # Demographics completeness (age, height, weight, sex)
            demographics = profile.get("demographics", {})
            required_demo = ["age", "height_cm", "weight_kg", "sex"]
            demographics_score = sum(1 for field in required_demo if demographics.get(field)) / len(required_demo)
            
            # Medical history completeness
            medical_history = profile.get("medical_history", {})
            if medical_history:
                medical_history_score = 0.7  # Base score for having any medical history
                if medical_history.get("family_history"):
                    medical_history_score += 0.2
                if medical_history.get("medications"):
                    medical_history_score += 0.1
            
            # Genomics completeness
            data_summary = profile.get("data_summary", {})
            if data_summary.get("genomic_files", 0) > 0:
                genomics_score = 0.5  # Base for having DNA data
                if data_summary.get("total_variants", 0) > 100000:
                    genomics_score += 0.3  # Good quality/coverage
                if data_summary.get("avg_quality_score", 0) > 0.8:
                    genomics_score += 0.2  # High quality
            
            # Devices completeness
            if data_summary.get("devices_connected", 0) > 0:
                devices_score = 0.6
                if data_summary.get("last_device_sync"):
                    # Recent sync within 7 days
                    devices_score += 0.4
            
            # Questionnaire completeness
            responses = data_summary.get("questionnaire_responses", 0)
            if responses > 0:
                questionnaire_score = min(responses / 20, 1.0)  # 20 questions = 100%
            
            # Overall completeness
            overall_score = (
                demographics_score * 0.2 +
                medical_history_score * 0.15 +
                genomics_score * 0.35 +
                devices_score * 0.15 +
                questionnaire_score * 0.15
            )
            
            return {
                "user_id": user_id,
                "completeness_scores": {
                    "demographics": round(demographics_score, 3),
                    "medical_history": round(medical_history_score, 3),
                    "genomics": round(genomics_score, 3),
                    "devices": round(devices_score, 3),
                    "questionnaire": round(questionnaire_score, 3),
                    "overall": round(overall_score, 3)
                },
                "completeness_percentage": round(overall_score * 100, 1),
                "completeness_grade": (
                    "A" if overall_score >= 0.8 else
                    "B" if overall_score >= 0.6 else
                    "C" if overall_score >= 0.4 else
                    "D"
                ),
                "recommendations": self._get_completeness_recommendations(
                    demographics_score, medical_history_score, genomics_score,
                    devices_score, questionnaire_score
                ),
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Completeness calculation failed: {e}"}
    
    def _get_completeness_recommendations(self, demo_score, medical_score, genomics_score, devices_score, quest_score) -> List[str]:
        """Generate recommendations to improve profile completeness"""
        recommendations = []
        
        if demo_score < 0.8:
            recommendations.append("Complete basic demographics (age, height, weight, sex)")
        
        if medical_score < 0.5:
            recommendations.append("Add medical history and family health information")
        
        if genomics_score < 0.3:
            recommendations.append("Upload DNA data from 23andMe, AncestryDNA, or genetic testing")
        
        if devices_score < 0.3:
            recommendations.append("Connect fitness devices or smartwatch for health monitoring")
        
        if quest_score < 0.5:
            recommendations.append("Complete health and lifestyle questionnaire")
        
        if not recommendations:
            recommendations.append("Profile is well-completed! Consider periodic updates.")
        
        return recommendations
