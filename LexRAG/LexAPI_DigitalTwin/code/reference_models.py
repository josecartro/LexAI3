"""
Reference Models for LexAPI_DigitalTwin
Creates and manages Adam & Eve default models with comprehensive baselines
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from code.database_manager import DigitalTwinDatabaseManager
from code.genetic_baseline_creator import GeneticBaselineCreator

class ReferenceModelManager:
    """Manages Adam & Eve reference models and population baselines"""
    
    def __init__(self):
        self.db_manager = DigitalTwinDatabaseManager()
        self.genetic_creator = GeneticBaselineCreator()
        
    def create_adam_eve_models(self) -> Dict[str, Any]:
        """Create comprehensive Adam & Eve reference models"""
        try:
            # Initialize database first
            if not self.db_manager.initialize_digital_twin_database():
                return {"error": "Database initialization failed"}
            
            # Create comprehensive genetic baselines using actual population data
            print("🧬 Creating genetic baselines from 4.4B record database...")
            
            # Get comprehensive genetic baselines
            adam_genetic_baseline = self.genetic_creator.create_adam_genetic_baseline()
            eve_genetic_baseline = self.genetic_creator.create_eve_genetic_baseline()
            
            if "error" in adam_genetic_baseline or "error" in eve_genetic_baseline:
                return {"error": "Genetic baseline creation failed"}
            
            # Adam - Comprehensive Male Model with Real Genetics
            adam_data = {
                "model_id": "adam_comprehensive_male",
                "model_name": "Adam_Comprehensive_Male", 
                "sex": "male",
                "age_category": "adult_35",
                "demographics": {
                    "age_years": 35,
                    "height_cm": 175,
                    "weight_kg": 75,
                    "bmi": 24.5,
                    "ethnicity": "mixed_european",
                    "ancestry_composition": adam_genetic_baseline["genetic_profile"]["ancestry_composition"]
                },
                "physiology": {
                    "heart_rate_bpm": 70,
                    "blood_pressure": "120/80",
                    "metabolic_rate": 1800,
                    "body_fat_percentage": 15,
                    "muscle_mass_percentage": 42
                },
                "genomic_baseline": adam_genetic_baseline["genetic_profile"],
                "expression_baseline": {
                    "tissue_profile": "gtex_male_35_comprehensive",
                    "expression_data": adam_genetic_baseline["genetic_profile"]["expression_baseline"]
                },
                "lifestyle_defaults": {
                    "exercise": "moderate_3x_week",
                    "diet": "standard_western",
                    "sleep": "7.5_hours",
                    "stress": "moderate",
                    "alcohol": "moderate",
                    "smoking": "never"
                },
                "health_baseline": {
                    "chronic_conditions": [],
                    "medications": [],
                    "family_history": "average_risk_all_conditions",
                    "preventive_care": "up_to_date"
                }
            }
            
            # Eve - Comprehensive Female Model with Real Genetics
            eve_data = {
                "model_id": "eve_comprehensive_female",
                "model_name": "Eve_Comprehensive_Female",
                "sex": "female", 
                "age_category": "adult_32",
                "demographics": {
                    "age_years": 32,
                    "height_cm": 162,
                    "weight_kg": 65,
                    "bmi": 24.7,
                    "ethnicity": "mixed_european",
                    "ancestry_composition": eve_genetic_baseline["genetic_profile"]["ancestry_composition"]
                },
                "physiology": {
                    "heart_rate_bpm": 75,
                    "blood_pressure": "110/70",
                    "metabolic_rate": 1500,
                    "body_fat_percentage": 25,
                    "muscle_mass_percentage": 36
                },
                "reproductive_health": eve_genetic_baseline.get("reproductive_profile", {}),
                "genomic_baseline": eve_genetic_baseline["genetic_profile"],
                "expression_baseline": {
                    "tissue_profile": "gtex_female_32_comprehensive",
                    "expression_data": eve_genetic_baseline["genetic_profile"]["expression_baseline"],
                    "reproductive_expression": eve_genetic_baseline["genetic_profile"].get("reproductive_genetics", {})
                },
                "lifestyle_defaults": {
                    "exercise": "moderate_3x_week",
                    "diet": "standard_western",
                    "sleep": "8_hours",
                    "stress": "moderate",
                    "alcohol": "low",
                    "smoking": "never"
                },
                "health_baseline": {
                    "chronic_conditions": [],
                    "medications": [],
                    "family_history": "average_risk_all_conditions",
                    "reproductive_health": "normal_premenopausal",
                    "preventive_care": "up_to_date"
                }
            }
            
            # Insert models into ClickHouse
            client = self.db_manager.get_clickhouse_client()
            
            for model_data in [adam_data, eve_data]:
                # Use explicit column names to avoid created_date DEFAULT column
                client.insert('digital_twin_db.reference_models', [(
                    model_data["model_id"],
                    model_data["model_name"],
                    model_data["sex"],
                    model_data["age_category"],
                    json.dumps(model_data["demographics"]),
                    json.dumps(model_data["physiology"]),
                    json.dumps(model_data["genomic_baseline"]),
                    json.dumps(model_data["expression_baseline"]),
                    json.dumps(model_data["lifestyle_defaults"]),
                    json.dumps(model_data["health_baseline"])
                )], column_names=[
                    'model_id', 'model_name', 'sex', 'age_category', 'demographics',
                    'physiology', 'genomic_baseline', 'expression_baseline', 
                    'lifestyle_defaults', 'health_baseline'
                ])
            
            return {
                "status": "success",
                "models_created": ["Adam_Default_Male", "Eve_Default_Female"],
                "creation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Reference model creation failed: {e}"}
    
    def get_reference_model(self, sex: str) -> Dict[str, Any]:
        """Get Adam or Eve reference model"""
        try:
            client = self.db_manager.get_clickhouse_client()
            
            model_name = "Adam_Comprehensive_Male" if sex.lower() == "male" else "Eve_Comprehensive_Female"
            
            result = client.query(f"""
                SELECT model_id, model_name, sex, demographics, physiology,
                       genomic_baseline, expression_baseline, lifestyle_defaults, health_baseline
                FROM digital_twin_db.reference_models
                WHERE model_name = '{model_name}'
                LIMIT 1
            """).result_rows
            
            if not result:
                return {"error": f"Reference model not found for {sex}"}
            
            model_data = result[0]
            
            return {
                "model_id": model_data[0],
                "model_name": model_data[1],
                "sex": model_data[2],
                "demographics": model_data[3] if isinstance(model_data[3], dict) else json.loads(model_data[3]),
                "physiology": model_data[4] if isinstance(model_data[4], dict) else json.loads(model_data[4]),
                "genomic_baseline": model_data[5] if isinstance(model_data[5], dict) else json.loads(model_data[5]),
                "expression_baseline": model_data[6] if isinstance(model_data[6], dict) else json.loads(model_data[6]),
                "lifestyle_defaults": model_data[7] if isinstance(model_data[7], dict) else json.loads(model_data[7]),
                "health_baseline": model_data[8] if isinstance(model_data[8], dict) else json.loads(model_data[8])
            }
            
        except Exception as e:
            return {"error": f"Reference model retrieval failed: {e}"}
    
    def get_population_model(self, ancestry: str, sex: str) -> Dict[str, Any]:
        """Get population-specific model (fallback to reference for now)"""
        # For now, return enhanced reference model
        base_model = self.get_reference_model(sex)
        if "error" not in base_model:
            base_model["population_context"] = ancestry
            base_model["source"] = "population_matched"
        return base_model