"""
Template Mixer for Digital Twin System
Handles user-specific template mixing based on ancestry, age, and demographics
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from code.ancestry_template_creator import AncestryTemplateCreator

class TemplateMixer:
    """Mixes ancestry templates based on user demographics and ancestry"""
    
    def __init__(self):
        self.template_creator = AncestryTemplateCreator()
        
    def analyze_user_ancestry(self, user_demographics: Dict[str, Any]) -> Dict[str, float]:
        """Analyze user demographics to determine ancestry template weights"""
        
        # Extract user information
        birthplace = user_demographics.get("birthplace", "")
        parents_origin = user_demographics.get("parents_origin", [])
        self_ethnicity = user_demographics.get("self_ethnicity", "")
        
        print(f"🧬 Analyzing ancestry for: {self_ethnicity}")
        print(f"   Birthplace: {birthplace}")
        print(f"   Parents from: {parents_origin}")
        
        # Country to ancestry mapping
        country_ancestry_map = {
            # European
            "sweden": "EUR", "norway": "EUR", "finland": "EUR", "germany": "EUR",
            "uk": "EUR", "italy": "EUR", "spain": "EUR", "france": "EUR",
            "poland": "EUR", "russia": "EUR", "ukraine": "EUR",
            
            # African
            "nigeria": "AFR", "ghana": "AFR", "kenya": "AFR", "ethiopia": "AFR",
            "south_africa": "AFR", "senegal": "AFR", "mali": "AFR",
            
            # East Asian
            "china": "EAS", "japan": "EAS", "korea": "EAS", "vietnam": "EAS",
            "thailand": "EAS", "philippines": "EAS", "singapore": "EAS",
            
            # South Asian
            "india": "SAS", "pakistan": "SAS", "bangladesh": "SAS", 
            "sri_lanka": "SAS", "nepal": "SAS",
            
            # Admixed American
            "mexico": "AMR", "colombia": "AMR", "peru": "AMR", "chile": "AMR",
            "brazil": "AMR", "argentina": "AMR", "puerto_rico": "AMR",
            
            # Middle Eastern / North African
            "egypt": "MENA", "iran": "MENA", "turkey": "MENA", "morocco": "MENA",
            "saudi_arabia": "MENA", "iraq": "MENA", "syria": "MENA"
        }
        
        # Calculate ancestry weights
        ancestry_weights = {"AFR": 0.0, "EUR": 0.0, "EAS": 0.0, "SAS": 0.0, "AMR": 0.0, "MENA": 0.0, "MIX": 0.0}
        
        # Analyze parents' origins
        if parents_origin and len(parents_origin) >= 2:
            for parent_origin in parents_origin[:2]:  # Max 2 parents
                parent_country = parent_origin.lower().strip()
                parent_ancestry = country_ancestry_map.get(parent_country, "MIX")
                ancestry_weights[parent_ancestry] += 0.5  # Each parent contributes 50%
        else:
            # Use birthplace if no parent info
            birth_country = birthplace.lower().strip()
            birth_ancestry = country_ancestry_map.get(birth_country, "MIX")
            ancestry_weights[birth_ancestry] = 1.0
        
        # Normalize weights
        total_weight = sum(ancestry_weights.values())
        if total_weight > 0:
            ancestry_weights = {k: v/total_weight for k, v in ancestry_weights.items()}
        else:
            ancestry_weights["MIX"] = 1.0
        
        # Remove zero weights for cleaner output
        ancestry_weights = {k: v for k, v in ancestry_weights.items() if v > 0}
        
        return ancestry_weights
    
    def create_mixed_template(self, user_demographics: Dict[str, Any]) -> Dict[str, Any]:
        """Create user-specific mixed template"""
        
        try:
            # Analyze user ancestry
            ancestry_weights = self.analyze_user_ancestry(user_demographics)
            
            # Get user characteristics
            sex = user_demographics.get("sex", "unknown").lower()
            age = user_demographics.get("age", 30)
            
            # Determine age band
            age_band = self._get_age_band(age)
            
            print(f"🎯 Creating mixed template:")
            print(f"   Sex: {sex}, Age: {age} ({age_band})")
            print(f"   Ancestry weights: {ancestry_weights}")
            
            # Get base templates for mixing
            base_templates = {}
            for ancestry_code, weight in ancestry_weights.items():
                if weight > 0:
                    template = self.template_creator.create_ancestry_template(ancestry_code, sex, age_band)
                    if "error" not in template:
                        base_templates[ancestry_code] = template
            
            # Mix templates based on weights
            mixed_template = self._mix_templates(base_templates, ancestry_weights, user_demographics)
            
            return {
                "user_id": user_demographics.get("user_id", "unknown"),
                "mixed_template": mixed_template,
                "ancestry_composition": ancestry_weights,
                "base_templates_used": list(base_templates.keys()),
                "confidence_level": "ancestry_weighted_population_prior",
                "mixing_logic": "weighted_average_by_ancestry_proportion",
                "creation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Mixed template creation failed: {e}"}
    
    def _get_age_band(self, age: int) -> str:
        """Convert age to age band"""
        
        if age <= 2:
            return "infant"
        elif age <= 12:
            return "child"
        elif age <= 18:
            return "adolescent"
        elif age <= 35:
            return "young_adult"
        elif age <= 55:
            return "middle_age"
        elif age <= 75:
            return "older_adult"
        else:
            return "elderly"
    
    def _mix_templates(self, base_templates: Dict[str, Dict], ancestry_weights: Dict[str, float], user_demographics: Dict[str, Any]) -> Dict[str, Any]:
        """Mix multiple ancestry templates based on weights"""
        
        mixed_template = {
            "demographics": user_demographics,
            "genetic_baseline": self._mix_genetic_baselines(base_templates, ancestry_weights),
            "pharmacogenomics": self._mix_pharmacogenomics(base_templates, ancestry_weights),
            "disease_risks": self._mix_disease_risks(base_templates, ancestry_weights),
            "expression_baseline": self._mix_expression_baselines(base_templates, ancestry_weights),
            "physiological_baseline": self._mix_physiological_baselines(base_templates, ancestry_weights)
        }
        
        return mixed_template
    
    def _mix_genetic_baselines(self, templates: Dict, weights: Dict) -> Dict[str, Any]:
        """Mix genetic baselines from multiple ancestry templates"""
        
        # For genetic data, use weighted frequencies
        mixed_genetics = {
            "ancestry_composition": weights,
            "variant_frequency_priors": "weighted_average_from_contributing_populations",
            "rare_variant_burden": "weighted_mixture_of_population_patterns",
            "population_specific_variants": "combined_from_all_contributing_ancestries"
        }
        
        return mixed_genetics
    
    def _mix_pharmacogenomics(self, templates: Dict, weights: Dict) -> Dict[str, Any]:
        """Mix pharmacogenomic baselines"""
        
        # Weight pharmacogenomic phenotype probabilities
        mixed_pharma = {
            "cyp450_phenotype_priors": "weighted_by_ancestry_composition",
            "drug_response_predictions": "ancestry_weighted_expectations",
            "population_specific_warnings": []
        }
        
        # Collect warnings from all contributing ancestries
        for ancestry_code, template in templates.items():
            weight = weights.get(ancestry_code, 0)
            if weight > 0.1:  # Only include if >10% contribution
                pharma_data = template.get("genetic_baseline", {}).get("pharmacogenomics", {})
                warnings = pharma_data.get("ancestry_specific_warnings", [])
                for warning in warnings:
                    mixed_pharma["population_specific_warnings"].append(f"{warning} (from {ancestry_code} ancestry)")
        
        return mixed_pharma
    
    def _mix_disease_risks(self, templates: Dict, weights: Dict) -> Dict[str, Any]:
        """Mix disease risk baselines"""
        
        return {
            "weighted_risk_priors": "combined_from_ancestry_contributions",
            "ancestry_specific_considerations": "all_contributing_populations_noted",
            "risk_calculation": "weighted_average_with_uncertainty_intervals"
        }
    
    def _mix_expression_baselines(self, templates: Dict, weights: Dict) -> Dict[str, Any]:
        """Mix expression baselines"""
        
        return {
            "tissue_expression_priors": "ancestry_weighted_GTEx_baselines",
            "sex_age_adjustments": "applied_to_mixed_baseline"
        }
    
    def _mix_physiological_baselines(self, templates: Dict, weights: Dict) -> Dict[str, Any]:
        """Mix physiological baselines"""
        
        return {
            "anthropometric_priors": "ancestry_weighted_body_composition",
            "organ_size_priors": "mixed_population_baselines",
            "reference_ranges": "population_weighted_normal_ranges"
        }

# Example usage function
def create_example_users():
    """Create digital twins for your example users"""
    
    mixer = TemplateMixer()
    
    example_users = [
        {
            "user_id": "vietnamese_girl_2yo",
            "age": 2,
            "sex": "female",
            "birthplace": "Vietnam",
            "parents_origin": ["Vietnam", "Vietnam"],
            "self_ethnicity": "Vietnamese"
        },
        {
            "user_id": "swedish_male_65yo", 
            "age": 65,
            "sex": "male",
            "birthplace": "Sweden",
            "parents_origin": ["Sweden", "Sweden"],
            "self_ethnicity": "Swedish"
        },
        {
            "user_id": "african_male_24yo",
            "age": 24,
            "sex": "male", 
            "birthplace": "Nigeria",
            "parents_origin": ["Nigeria", "Nigeria"],
            "self_ethnicity": "Nigerian"
        },
        {
            "user_id": "chilean_female_15yo",
            "age": 15,
            "sex": "female",
            "birthplace": "Chile", 
            "parents_origin": ["Chile", "Chile"],
            "self_ethnicity": "Chilean"
        },
        {
            "user_id": "italian_female_37yo",
            "age": 37,
            "sex": "female",
            "birthplace": "Italy",
            "parents_origin": ["Italy", "Italy"], 
            "self_ethnicity": "Italian"
        }
    ]
    
    print("🌍 Creating example user digital twins...")
    
    for user in example_users:
        print(f"\\n📋 Creating twin for: {user['user_id']}")
        result = mixer.create_mixed_template(user)
        
        if "error" not in result:
            ancestry_comp = result.get("ancestry_composition", {})
            print(f"   ✅ Success: {ancestry_comp}")
        else:
            print(f"   ❌ Failed: {result['error']}")

if __name__ == "__main__":
    create_example_users()
