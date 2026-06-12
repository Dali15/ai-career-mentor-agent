from __future__ import annotations

import math
import re
from typing import Any

from .career_mentor_service import CareerMentorService

class MockCareerService(CareerMentorService):
    """
    Vector-based semantic recommendation system.
    Replaces keyword-based matching with multidimensional vector similarity.
    """

    DEFAULT_COMPARISON_CAREERS = [
        "Frontend Developer", "Backend Developer", "Data Analyst", 
        "DevOps Engineer", "Cloud Engineer", "Mobile Developer"
    ]
    
    # 1. Expanded Hierarchical Vector Space (Flattened for computation)
    DIMENSIONS = [
        "backend", "frontend", "data", "cloud", "devops", 
        "ai", "mobile", "database", "system_design",
        "ui_ux", "networking", "security", "testing", "machine_learning"
    ]
    
    DIMENSION_WEIGHTS = {
        "backend": 1.1, "frontend": 1.0, "data": 1.1, "cloud": 1.2, "devops": 1.2,
        "ai": 1.3, "mobile": 1.0, "database": 1.1, "system_design": 1.2,
        "ui_ux": 1.0, "networking": 1.1, "security": 1.3, "testing": 1.0, "machine_learning": 1.3
    }

    SKILL_VECTORS = {
        "sql": {"data": 0.8, "database": 0.9, "backend": 0.4},
        "python": {"data": 0.7, "backend": 0.6, "ai": 0.6, "machine_learning": 0.5},
        "react": {"frontend": 0.9, "mobile": 0.3, "backend": 0.2, "ui_ux": 0.4},
        "web apps": {"frontend": 0.6, "backend": 0.6},
        "node": {"backend": 0.9, "frontend": 0.3},
        "node.js": {"backend": 0.9, "frontend": 0.3},
        "docker": {"devops": 0.9, "cloud": 0.6, "backend": 0.4, "networking": 0.2},
        "kubernetes": {"devops": 0.9, "cloud": 0.8, "networking": 0.3},
        "aws": {"cloud": 1.0, "devops": 0.6, "networking": 0.4, "security": 0.3},
        "azure": {"cloud": 1.0, "devops": 0.6, "networking": 0.4, "security": 0.3},
        "javascript": {"frontend": 0.9, "backend": 0.4},
        "html": {"frontend": 0.8, "ui_ux": 0.6},
        "css": {"frontend": 0.8, "ui_ux": 0.7},
        "machine learning": {"ai": 1.0, "data": 0.7, "backend": 0.3, "machine_learning": 1.0},
        "data analysis": {"data": 1.0, "database": 0.6},
        "api": {"backend": 0.8, "system_design": 0.5},
        "apis": {"backend": 0.8, "system_design": 0.5},
        "system design": {"system_design": 1.0, "backend": 0.8, "cloud": 0.6},
        "mobile dev": {"mobile": 1.0, "frontend": 0.6, "ui_ux": 0.5},
        "flutter": {"mobile": 1.0, "frontend": 0.7, "ui_ux": 0.4},
    }

    CAREER_VECTORS = {
        "Data Analyst": {"data": 1.0, "database": 0.9, "backend": 0.4, "ai": 0.5, "machine_learning": 0.3},
        "Backend Developer": {"backend": 1.0, "database": 0.8, "system_design": 0.8, "frontend": 0.3, "testing": 0.4, "security": 0.3},
        "DevOps Engineer": {"devops": 1.0, "cloud": 0.9, "backend": 0.5, "system_design": 0.7, "networking": 0.6, "security": 0.5},
        "Cloud Engineer": {"cloud": 1.0, "devops": 0.7, "backend": 0.4, "system_design": 0.7, "networking": 0.8, "security": 0.6},
        "Mobile Developer": {"mobile": 1.0, "frontend": 0.8, "backend": 0.4, "ai": 0.2, "ui_ux": 0.5},
        "Frontend Developer": {"frontend": 1.0, "mobile": 0.5, "backend": 0.3, "ui_ux": 0.8, "testing": 0.3},
        "Full-Stack Developer": {"frontend": 0.8, "backend": 0.8, "database": 0.6, "system_design": 0.5, "ui_ux": 0.4},
        "Cybersecurity Analyst": {"devops": 0.6, "cloud": 0.7, "backend": 0.5, "system_design": 0.6, "security": 1.0, "networking": 0.9},
    }

    # 2. Interest Boosts (Soft multipliers)
    INTEREST_BOOSTS = {
        "ai": {"ai": 0.05, "data": 0.02, "cloud": 0.02, "machine_learning": 0.05},
        "web apps": {"frontend": 0.05, "backend": 0.05},
        "data analysis": {"data": 0.05, "database": 0.02},
        "data": {"data": 0.05, "database": 0.02},
        "cloud": {"cloud": 0.05, "devops": 0.02},
        "mobile": {"mobile": 0.05, "frontend": 0.02},
    }

    def analyze_profile(self, user_data: dict[str, Any]) -> dict[str, Any]:
        skills_text = str(user_data.get("skills", "")).lower()
        interests_text = str(user_data.get("interests", "")).lower()
        
        selected_careers = user_data.get("selected_careers")
        if not selected_careers or not isinstance(selected_careers, list):
            comparison_careers = self.DEFAULT_COMPARISON_CAREERS
        else:
            comparison_careers = [str(c).strip() for c in selected_careers if str(c).strip()]

        user_vector, match_count = self._build_user_vector(skills_text, interests_text)
        career_scores = self._score_careers(user_vector, match_count, comparison_careers)

        if career_scores:
            top_career = career_scores[0]["career"]
            reasoning = [career_scores[0]["reasoning_summary"]]
        else:
            top_career = "Full-Stack Developer"
            reasoning = ["No strong vector alignments found, falling back to general path."]

        # Returning strictly the required output format
        return {
            "career_scores": career_scores,
            "top_career": top_career,
            "reasoning": reasoning
        }

    def _build_response(self, user_data: dict[str, Any], profile_analysis: dict[str, Any]) -> dict[str, Any]:
        # Return strict output as requested by the user rule
        return {
            "career_scores": profile_analysis.get("career_scores", []),
            "top_career": profile_analysis.get("top_career", "Full-Stack Developer"),
            "reasoning": profile_analysis.get("reasoning", [])
        }

    def _build_user_vector(self, skills_text: str, interests_text: str) -> tuple[dict[str, float], int]:
        tokens = [t.strip() for t in re.split(r"[,;\n/|]+", skills_text) if t.strip()]
        user_vector = {dim: 0.0 for dim in self.DIMENSIONS}
        match_count = 0

        for token in tokens:
            vec = self.SKILL_VECTORS.get(token)
            if vec:
                match_count += 1
                for dim, val in vec.items():
                    user_vector[dim] += val
        
        # Normalize between 0 and 1 by averaging
        if match_count > 0:
            for dim in self.DIMENSIONS:
                user_vector[dim] = min(1.0, user_vector[dim] / match_count)

        # 2. Apply interest integration BEFORE scoring (Soft Multiplier)
        for interest, boosts in self.INTEREST_BOOSTS.items():
            if interest in interests_text:
                for dim, boost_val in boosts.items():
                    # Apply multiplier (e.g. 1.05) instead of direct +0.2 addition
                    user_vector[dim] = min(1.0, user_vector[dim] * (1.0 + boost_val))

        return user_vector, match_count

    def _score_careers(self, user_vector: dict[str, float], match_count: int, careers: list[str]) -> list[dict[str, Any]]:
        results = []
        for career in careers:
            career_vector = self.CAREER_VECTORS.get(career)
            if not career_vector:
                career_vector = {dim: 0.2 for dim in self.DIMENSIONS}

            dot_product = 0.0
            mag1_sq = 0.0
            mag2_sq = 0.0

            # Calculate similarity manually with cap safeguards and DIMENSION WEIGHTS
            total_dot = sum(
                (user_vector.get(d, 0) * self.DIMENSION_WEIGHTS.get(d, 1.0)) * 
                (career_vector.get(d, 0) * self.DIMENSION_WEIGHTS.get(d, 1.0)) 
                for d in self.DIMENSIONS
            )
            
            for dim in self.DIMENSIONS:
                weight = self.DIMENSION_WEIGHTS.get(dim, 1.0)
                u_val = user_vector.get(dim, 0.0) * weight
                c_val = career_vector.get(dim, 0.0) * weight
                
                # Apply soft cap if one dimension contributes >40% of total score
                dim_dot = u_val * c_val
                if total_dot > 0 and (dim_dot / total_dot) > 0.4:
                    dim_dot = total_dot * 0.4
                    
                dot_product += dim_dot
                mag1_sq += u_val ** 2
                mag2_sq += c_val ** 2
            
            mag1 = math.sqrt(mag1_sq)
            mag2 = math.sqrt(mag2_sq)

            if mag1 == 0 or mag2 == 0:
                cosine_sim = 0.0
            else:
                cosine_sim = dot_product / (mag1 * mag2)

            # Importance-aware Coverage Score
            coverage_num = 0.0
            coverage_den = 0.0
            for dim in self.DIMENSIONS:
                c_val = career_vector.get(dim, 0.0)
                u_val = user_vector.get(dim, 0.0)
                coverage_num += min(u_val, c_val)
                coverage_den += c_val
                
            coverage_score = (coverage_num / coverage_den) if coverage_den > 0 else 0.0

            # Adaptive Hybrid Score
            if match_count < 3:
                coverage_weight = 0.5
                cosine_weight = 0.5
            else:
                coverage_weight = 0.3
                cosine_weight = 0.7

            hybrid_score = (cosine_weight * cosine_sim) + (coverage_weight * coverage_score)

            # Ensure top 3 non-zero by having a baseline offset
            normalized_score = int(round(hybrid_score * 100))
            if normalized_score < 5:
                normalized_score = 5

            explanation = self._generate_explanation(user_vector, career_vector, career)

            results.append({
                "career": career,
                "score": normalized_score,
                "top_positive_factors": explanation["top_positive_factors"],
                "supporting_factors": explanation["supporting_factors"],
                "missing_critical_skills": explanation["missing_critical_skills"],
                "reasoning_summary": explanation["reasoning_summary"]
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def _generate_explanation(self, user_vector: dict[str, float], career_vector: dict[str, float], career_name: str) -> dict[str, Any]:
        contributions = []
        for dim in self.DIMENSIONS:
            weight = self.DIMENSION_WEIGHTS.get(dim, 1.0)
            u_val = user_vector.get(dim, 0.0)
            c_val = career_vector.get(dim, 0.0)
            contrib = u_val * c_val * weight
            contributions.append((dim, contrib, u_val, c_val))
            
        contributions.sort(key=lambda x: x[1], reverse=True)
        
        # A. Top Positive Factors
        top_positive = [item[0] for item in contributions if item[1] > 0][:2]
        
        # B. Supporting Factors
        supporting = [item[0] for item in contributions if item[1] > 0][2:4]
        
        # C. Missing Critical Skills
        missing_critical = [item[0] for item in contributions if item[3] > 0.7 and item[2] < 0.3]
        
        # D. Reasoning Summary Rules
        if not top_positive:
            reasoning_summary = f"No strong vector alignments found for {career_name}."
        else:
            top_str = " and ".join(top_positive)
            reasoning_summary = f"Strong alignment in {top_str} indicates suitability for {career_name} roles."
            
            if supporting:
                sup_str = " and ".join(supporting)
                reasoning_summary += f" Additional support from {sup_str} strengthens capability."
                
            if missing_critical:
                gap_str = " and ".join(missing_critical[:2])
                reasoning_summary += f" However, limited presence in {gap_str} reduces full readiness."
                
            reasoning_summary += f" Overall, this profile fits an early-stage {career_name} trajectory."
            
        return {
            "top_positive_factors": top_positive,
            "supporting_factors": supporting,
            "missing_critical_skills": missing_critical,
            "reasoning_summary": reasoning_summary
        }
