import logging
from typing import Dict, List, Any

from .career_profiles import DEFAULT_COMPARISON_CAREERS, CAREER_VECTORS, DIMENSIONS
from .vector_utils import build_user_vector, calculate_cosine_similarity, calculate_coverage_score
from .explanation_engine import generate_explanation

logger = logging.getLogger(__name__)

class ScoringEngine:
    @staticmethod
    def analyze_user_profile(skills_text: str, interests_text: str, selected_careers: List[str] = None) -> Dict[str, Any]:
        if not selected_careers or not isinstance(selected_careers, list):
            comparison_careers = DEFAULT_COMPARISON_CAREERS
        else:
            comparison_careers = [str(c).strip() for c in selected_careers if str(c).strip()]

        user_vector, match_count = build_user_vector(skills_text, interests_text)
        
        logger.info(f"User Vector Generated (Match Count: {match_count}): {user_vector}")

        results = []
        for career in comparison_careers:
            career_vector = CAREER_VECTORS.get(career)
            if not career_vector:
                career_vector = {dim: 0.2 for dim in DIMENSIONS}
                
            cosine_sim = calculate_cosine_similarity(user_vector, career_vector)
            coverage_score = calculate_coverage_score(user_vector, career_vector)
            
            if match_count < 3:
                coverage_weight = 0.5
                cosine_weight = 0.5
            else:
                coverage_weight = 0.3
                cosine_weight = 0.7

            hybrid_score = (cosine_weight * cosine_sim) + (coverage_weight * coverage_score)

            normalized_score = int(round(hybrid_score * 100))
            if normalized_score < 5:
                normalized_score = 5

            explanation = generate_explanation(user_vector, career_vector, career)

            results.append({
                "career": career,
                "score": normalized_score,
                "top_positive_factors": explanation["top_positive_factors"],
                "supporting_factors": explanation["supporting_factors"],
                "missing_critical_skills": explanation["missing_critical_skills"],
                "reasoning_summary": explanation["reasoning_summary"]
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        
        if results:
            top_career = results[0]["career"]
            reasoning = {"summary": results[0]["reasoning_summary"]}
            explanation = {
                "top_positive_factors": results[0]["top_positive_factors"],
                "supporting_factors": results[0]["supporting_factors"],
                "missing_critical_skills": results[0]["missing_critical_skills"]
            }
            logger.info(f"Top Career Identified: {top_career} with score {results[0]['score']}")
        else:
            top_career = "Full-Stack Developer"
            reasoning = {"summary": "No strong vector alignments found, falling back to general path."}
            explanation = {}

        return {
            "career_scores": results,
            "top_career": top_career,
            "reasoning": reasoning,
            "explanation": explanation
        }
