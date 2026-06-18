import logging
from typing import Dict, List, Any

from .career_profiles import DEFAULT_COMPARISON_CAREERS, CAREER_VECTORS, DIMENSIONS, INTEREST_BOOSTS
from .vector_utils import build_user_vector, calculate_cosine_similarity, calculate_coverage_score
from .explanation_engine import generate_explanation

logger = logging.getLogger(__name__)

class ScoringEngine:
    @staticmethod
    def analyze_user_profile(skills_text: str, interests_text: str, selected_careers: List[str] = None, education_text: str = "") -> Dict[str, Any]:
        if not selected_careers or not isinstance(selected_careers, list):
            comparison_careers = DEFAULT_COMPARISON_CAREERS
        else:
            comparison_careers = [str(c).strip() for c in selected_careers if str(c).strip()]

        user_vector, match_count = build_user_vector(skills_text, interests_text, education_text)
        
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
                "hybrid_score": hybrid_score,
                "top_positive_factors": explanation["top_positive_factors"],
                "supporting_factors": explanation["supporting_factors"],
                "missing_critical_skills": explanation["missing_critical_skills"],
                "reasoning_summary": explanation["reasoning_summary"]
            })

        # Apply interest-based tie-breaker: when scores are within 10 points, interests can adjust
        results = ScoringEngine._apply_interest_tie_breaker(results, interests_text)
        
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

        # Remove temporary scoring fields before returning
        for result in results:
            result.pop("hybrid_score", None)

        return {
            "career_scores": results,
            "top_career": top_career,
            "reasoning": reasoning,
            "explanation": explanation
        }
    
    @staticmethod
    def _apply_interest_tie_breaker(results: List[Dict[str, Any]], interests_text: str) -> List[Dict[str, Any]]:
        """
        When scores are within 10 points of each other, interests can act as a tie-breaker.
        Interests can adjust scores by ±5 points.
        """
        if not results:
            return results
        
        # Sort by current score to find close competitors
        sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
        
        if len(sorted_results) < 2:
            return results
        
        top_score = sorted_results[0]["score"]
        interests_lower = interests_text.lower()
        
        # Apply interest boost to careers that match interests
        for result in results:
            career_name_lower = result["career"].lower()
            score_gap = top_score - result["score"]
            
            # Only apply tie-breaker within 10 points
            if score_gap <= 10 and score_gap > 0:
                interest_match = ScoringEngine._calculate_interest_match(career_name_lower, interests_lower)
                if interest_match > 0:
                    # Apply at most +5 points, and only when the scores are close.
                    adjustment = min(5, int(round(interest_match * 5)))
                    result["score"] = min(100, result["score"] + adjustment)
        
        return results
    
    @staticmethod
    def _calculate_interest_match(career_name: str, interests_text: str) -> float:
        """
        Calculate how well a career matches the user's interests.
        Returns a value 0-1 indicating strength of match.
        """
        career_interest_map = {
            "backend developer": ["backend", "api", "system"],
            "frontend developer": ["ui", "ux", "frontend"],
            "devops engineer": ["devops", "infrastructure", "automation", "cloud", "linux"],
            "cloud engineer": ["cloud", "aws", "azure", "gcp", "infrastructure"],
            "data analyst": ["data", "analytics", "visualization"],
            "mobile developer": ["mobile", "ios", "android"],
        }
        
        interests = career_interest_map.get(career_name.lower(), [])
        if not interests:
            return 0.0
        
        matches = sum(1 for interest in interests if interest in interests_text)
        return min(1.0, matches / len(interests)) if interests else 0.0
