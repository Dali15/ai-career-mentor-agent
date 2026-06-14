from typing import Dict, Any, List

class FinalResponseBuilder:
    """
    Strict deterministic authority layer for building the final API response.
    Guarantees schema stability, handles fallbacks, and standardizes professional tone.
    """
    
    @staticmethod
    def build(
        user_profile: Dict[str, Any],
        normalized_profile: Dict[str, Any],
        career_scores: List[Dict[str, Any]],
        explanation: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        # 1. Ensure career scores exist
        if not career_scores:
            career_scores = [{
                "career": "Full-Stack Developer",
                "score": 5,
                "top_positive_factors": [],
                "supporting_factors": [],
                "missing_critical_skills": [],
                "reasoning_summary": "Defaulted due to empty scoring data."
            }]
            
        # 2. Extract top career safely
        top_career = career_scores[0].get("career", "Full-Stack Developer")
        top_score = career_scores[0].get("score", 0)
        
        # 3. Fallbacks for explanation engine
        reasoning = explanation.get("reasoning_steps", [])
        if not reasoning:
            reasoning = [
                "Profile interpretation completed.",
                "Skill clusters mapped to industry requirements.",
                "Gaps identified.",
                f"Selected {top_career} as primary recommendation."
            ]
            
        # 4. Generate deterministic Roadmap
        roadmap = explanation.get("roadmap", {}) 
        if not roadmap:
            roadmap = FinalResponseBuilder._build_fallback_roadmap(top_career, top_score)
        
        # 5. Build Certifications & Resources
        certs = FinalResponseBuilder._build_certifications(top_career, top_score)
        resources = FinalResponseBuilder._build_learning_resources(top_career, top_score)
        
        # 6. Extract Strengths and Gaps
        strengths = career_scores[0].get("top_positive_factors", [])
        if not strengths:
            strengths = ["General foundational knowledge"]
            
        gaps = career_scores[0].get("missing_critical_skills", [])
        if not gaps:
            gaps = [f"Advanced {top_career} expertise"]
            
        return {
            "ai_source": "", # Populated by ai_engine.py
            "top_career": top_career,
            "career_scores": career_scores,
            "reasoning": reasoning,
            "roadmap": roadmap,
            "certifications": certs,
            "learning_resources": resources,
            "strengths": strengths,
            "gaps": gaps,
            
            # Carry over transparent layers
            "final_explanation": explanation.get("final_explanation", ""),
            "career_specific_explanations": explanation.get("career_specific_explanations", {}),
            "decision_trace": explanation.get("decision_trace", {}),
            "normalization": normalized_profile
        }

    @staticmethod
    def _build_fallback_roadmap(top_career: str, score: int) -> Dict[str, List[str]]:
        if score < 40:
            return {
                "month_1": [f"Learn fundamentals of {top_career}"],
                "month_2": ["Build a simple introductory project"],
                "month_3": ["Familiarize with industry tools"]
            }
        elif score < 75:
            return {
                "month_1": [f"Deep dive into intermediate {top_career} concepts"],
                "month_2": ["Build a full-stack or complex project"],
                "month_3": ["Prepare for initial interviews"]
            }
        else:
            return {
                "month_1": ["Master advanced architecture and system design"],
                "month_2": ["Contribute to open source or build a production app"],
                "month_3": ["Prepare for senior/mid-level interviews"]
            }
            
    @staticmethod
    def _build_certifications(top_career: str, score: int) -> List[str]:
        if score < 10:
            return []
        if score < 40:
            return [f"Foundational {top_career} Certification"]
        return [f"Professional {top_career} Certification"]
        
    @staticmethod
    def _build_learning_resources(top_career: str, score: int) -> List[Dict[str, Any]]:
        if score < 10:
            return []
        return [
            {"title": f"Introduction to {top_career}", "type": "Course", "url": "https://example.com/intro"},
            {"title": f"{top_career} Best Practices", "type": "Article", "url": "https://example.com/practices"}
        ]
