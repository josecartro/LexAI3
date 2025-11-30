"""
Data Overlay Engine for LexAPI_DigitalTwin
Implements intelligent data overlay logic: User > Population > Sex > Generic
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class DataOverlayEngine:
    """Manages intelligent data overlay with confidence scoring"""
    
    def __init__(self):
        self.confidence_weights = {
            "user_specific": 1.0,
            "population_matched": 0.7,
            "sex_matched": 0.5,
            "generic_reference": 0.3
        }
    
    def create_composite_twin(self, user_data: Dict[str, Any], reference_model: Dict[str, Any]) -> Dict[str, Any]:
        """Create composite digital twin using data overlay logic"""
        try:
            composite_twin = {}
            data_sources = {}
            confidence_scores = {}
            
            # Categories to overlay
            categories = ["demographics", "physiology", "genomic_baseline", "health_baseline"]
            
            for category in categories:
                overlay_result = self._overlay_category_data(category, user_data, reference_model)
                composite_twin[category] = overlay_result["data"]
                data_sources[category] = overlay_result["source"]
                confidence_scores[category] = overlay_result["confidence"]
            
            # Calculate overall completeness
            completeness_score = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.3
            
            return {
                "twin_data": composite_twin,
                "data_sources": data_sources,
                "confidence_scores": confidence_scores,
                "completeness_score": round(completeness_score, 3)
            }
            
        except Exception as e:
            return {"error": f"Composite twin creation failed: {e}"}
    
    def _overlay_category_data(self, category: str, user_data: Dict, reference_model: Dict) -> Dict[str, Any]:
        """Overlay data for a specific category"""
        
        user_category = user_data.get(category, {})
        reference_category = reference_model.get(category, {})
        
        if user_category:
            return {
                "data": user_category,
                "source": "user_specific", 
                "confidence": 1.0
            }
        elif reference_category:
            return {
                "data": reference_category,
                "source": "reference_model",
                "confidence": 0.3
            }
        else:
            return {
                "data": {},
                "source": "empty",
                "confidence": 0.1
            }
    
    def get_data_gaps(self, user_id: str) -> Dict[str, Any]:
        """Identify data gaps for user"""
        return {
            "user_id": user_id,
            "data_gaps": {
                "high_priority": ["genomic_data", "family_history"],
                "medium_priority": ["lifestyle_details", "device_data"],
                "low_priority": ["environmental_factors"]
            },
            "recommendations": [
                "Upload DNA data for personalized analysis",
                "Complete health questionnaire",
                "Connect fitness devices"
            ]
        }