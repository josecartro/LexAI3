"""
Questionnaire Engine for LexAPI_Users
Generates adaptive questionnaires based on user data and DNA findings
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from code.database_manager import UserDatabaseManager

class QuestionnaireEngine:
    """Generates intelligent, adaptive questionnaires for users"""
    
    def __init__(self):
        self.db_manager = UserDatabaseManager()
        
        # Pre-defined question categories and priorities
        self.question_categories = {
            "health_history": {
                "priority": 10,
                "questions": [
                    "Do you have any chronic medical conditions?",
                    "Are you currently taking any medications?",
                    "Do you have any known allergies?",
                    "Have you had any surgeries or major medical procedures?",
                    "Do you have a family history of genetic diseases?"
                ]
            },
            "lifestyle": {
                "priority": 7,
                "questions": [
                    "How would you describe your typical diet?",
                    "How many hours of sleep do you get per night?",
                    "How often do you exercise per week?",
                    "Do you smoke or use tobacco products?",
                    "How many alcoholic drinks do you have per week?"
                ]
            },
            "symptoms": {
                "priority": 9,
                "questions": [
                    "Are you experiencing any current health symptoms?",
                    "Do you have any chronic pain?",
                    "Have you noticed any changes in your energy levels?",
                    "Do you have any concerns about your memory or cognition?",
                    "Are you experiencing any digestive issues?"
                ]
            },
            "family_history": {
                "priority": 8,
                "questions": [
                    "Does anyone in your family have heart disease?",
                    "Is there a family history of cancer?",
                    "Does anyone in your family have diabetes?",
                    "Is there a family history of mental health conditions?",
                    "Are there any genetic conditions that run in your family?"
                ]
            },
            "environmental": {
                "priority": 5,
                "questions": [
                    "What is your occupation?",
                    "Are you exposed to any chemicals or toxins at work?",
                    "Do you live in an urban or rural environment?",
                    "Have you lived in areas with high pollution?",
                    "Do you have any concerns about your living environment?"
                ]
            }
        }
    
    def generate_adaptive_questionnaire(self, user_id: str) -> Dict[str, Any]:
        """Generate adaptive questionnaire based on user's data gaps and DNA findings"""
        try:
            # Get user profile to understand data gaps
            conn = self.db_manager.get_user_db_connection()
            
            # Get existing responses
            existing_responses = conn.execute("""
                SELECT question_category, question_id, response_value
                FROM user_questionnaires
                WHERE user_id = ?
            """, [user_id]).fetchall()
            
            # Get user profile data
            profile_data = conn.execute("""
                SELECT demographics, medical_history
                FROM user_profiles
                WHERE user_id = ?
            """, [user_id]).fetchall()
            
            # Get genomic data status
            genomic_data = conn.execute("""
                SELECT COUNT(*) as file_count, AVG(quality_score) as avg_quality
                FROM user_genomics
                WHERE user_id = ? AND processing_status = 'processed'
            """, [user_id]).fetchall()
            
            conn.close()
            
            # Analyze what questions to ask
            answered_categories = set(resp[0] for resp in existing_responses)
            profile = profile_data[0] if profile_data else (None, None)
            genomics = genomic_data[0] if genomic_data else (0, 0)
            
            # Generate priority questions
            priority_questions = []
            
            # High priority if DNA data uploaded but no health history
            if genomics[0] > 0 and "health_history" not in answered_categories:
                priority_questions.extend(self._generate_category_questions("health_history", 5))
            
            # Family history important if DNA data available
            if genomics[0] > 0 and "family_history" not in answered_categories:
                priority_questions.extend(self._generate_category_questions("family_history", 3))
            
            # Symptoms if any medical history indicated
            medical_history = json.loads(profile[1]) if profile[1] else {}
            if medical_history and "symptoms" not in answered_categories:
                priority_questions.extend(self._generate_category_questions("symptoms", 3))
            
            # Lifestyle questions for everyone
            if "lifestyle" not in answered_categories:
                priority_questions.extend(self._generate_category_questions("lifestyle", 4))
            
            # Environmental if no other high-priority gaps
            if len(priority_questions) < 5 and "environmental" not in answered_categories:
                priority_questions.extend(self._generate_category_questions("environmental", 2))
            
            return {
                "user_id": user_id,
                "adaptive_questions": priority_questions,
                "existing_responses": len(existing_responses),
                "data_context": {
                    "has_dna_data": genomics[0] > 0,
                    "dna_quality": round(genomics[1] or 0, 3),
                    "has_medical_history": bool(medical_history),
                    "answered_categories": list(answered_categories)
                },
                "questionnaire_type": "adaptive_based_on_data_gaps",
                "estimated_completion_time": f"{len(priority_questions) * 2} minutes",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Questionnaire generation failed: {e}"}
    
    def _generate_category_questions(self, category: str, count: int) -> List[Dict[str, Any]]:
        """Generate questions for a specific category"""
        category_data = self.question_categories.get(category, {})
        questions = category_data.get("questions", [])
        priority = category_data.get("priority", 5)
        
        selected_questions = []
        for i, question_text in enumerate(questions[:count]):
            selected_questions.append({
                "question_id": f"{category}_{i+1}",
                "question_category": category,
                "question_text": question_text,
                "question_priority": priority,
                "response_type": "text",
                "required": priority >= 8
            })
        
        return selected_questions
    
    def submit_responses(self, user_id: str, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Submit and store questionnaire responses"""
        try:
            conn = self.db_manager.get_user_db_connection(read_only=False)
            
            successful_responses = 0
            
            for response in responses:
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO user_questionnaires
                        (user_id, question_id, question_category, question_text, 
                         response_value, confidence_score, response_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, [
                        user_id,
                        response.get("question_id"),
                        response.get("question_category", "general"),
                        response.get("question_text", ""),
                        response.get("response_value", ""),
                        response.get("confidence_score", 0.8),
                        datetime.now()
                    ])
                    successful_responses += 1
                    
                except Exception as e:
                    print(f"Error storing response {response.get('question_id')}: {e}")
            
            conn.close()
            
            return {
                "user_id": user_id,
                "responses_submitted": successful_responses,
                "total_responses": len(responses),
                "submission_status": "success" if successful_responses == len(responses) else "partial",
                "next_steps": self._get_next_steps(user_id),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Response submission failed: {e}"}
    
    def _get_next_steps(self, user_id: str) -> List[str]:
        """Get recommended next steps for user"""
        # This would analyze user's current data and suggest next actions
        return [
            "Review genetic analysis results",
            "Connect additional health devices",
            "Schedule follow-up questionnaire",
            "Consult with healthcare provider if needed"
        ]
