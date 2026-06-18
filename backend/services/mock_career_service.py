from __future__ import annotations

import logging
import math
import re
from typing import Any

from .career_mentor_service import CareerMentorService
from .career_profiles import CAREER_VECTORS as SHARED_CAREER_VECTORS, DIMENSIONS as SHARED_DIMENSIONS, DIMENSION_WEIGHTS as SHARED_DIMENSION_WEIGHTS, INTEREST_BOOSTS as SHARED_INTEREST_BOOSTS, SKILL_VECTORS as SHARED_SKILL_VECTORS
from .explanation_engine import ExplanationEngine
from .intent_normalizer import normalize_user_profile
from .final_response_builder import FinalResponseBuilder

logger = logging.getLogger(__name__)

class MockCareerService(CareerMentorService):
    """
    Vector-based semantic recommendation system.
    Replaces keyword-based matching with multidimensional vector similarity.
    Uses fixed-point arithmetic for deterministic scoring across all platforms.
    """

    DEFAULT_COMPARISON_CAREERS = [
        "Frontend Developer", "Backend Developer", "Data Analyst", 
        "DevOps Engineer", "Cloud Engineer", "Mobile Developer"
    ]
    
    # Scoring formula weights (tuned for balanced recommendations)
    # - Cosine similarity (55%): Captures overall skill-to-career alignment
    # - Coverage score (30%): Ensures user has critical skills for the role
    # - Alignment bonus (15%): Boosts careers where user has the top required dimension
    COSINE_WEIGHT = 0.55
    COVERAGE_WEIGHT = 0.30
    ALIGNMENT_WEIGHT = 0.15
    
    # 1. Expanded Hierarchical Vector Space (Flattened for computation)
    DIMENSIONS = SHARED_DIMENSIONS
    DIMENSION_WEIGHTS = SHARED_DIMENSION_WEIGHTS
    SKILL_VECTORS = SHARED_SKILL_VECTORS
    CAREER_VECTORS = SHARED_CAREER_VECTORS
    INTEREST_BOOSTS = SHARED_INTEREST_BOOSTS

    def analyze_profile(self, user_data: dict[str, Any]) -> dict[str, Any]:
        raw_skills    = str(user_data.get("skills", ""))
        raw_interests = str(user_data.get("interests", ""))
        raw_education = str(user_data.get("education", ""))

        logger.info(f"Analyzing profile: skills_len={len(raw_skills)}, interests_len={len(raw_interests)}, education_len={len(raw_education)}")

        # ── Intent Normalization Layer ────────────────────────────────────────
        # Raw input MUST NOT reach the vector builder directly.
        # All messy/slang/multilingual input is cleaned here first.
        normalized = normalize_user_profile(raw_education, raw_skills, raw_interests)
        skills_text    = normalized["normalized_skills_text"]
        interests_text = normalized["normalized_interests_text"]

        logger.debug(f"Normalized: {len(normalized['clean_skills'])} skills detected")

        selected_careers = user_data.get("selected_careers")
        if not selected_careers or not isinstance(selected_careers, list):
            comparison_careers = self.DEFAULT_COMPARISON_CAREERS
            logger.debug("Using default comparison careers")
        else:
            comparison_careers = [str(c).strip() for c in selected_careers if str(c).strip()]
            if not comparison_careers:
                comparison_careers = self.DEFAULT_COMPARISON_CAREERS
                logger.warning("Selected careers list was empty, using defaults")

        user_vector, match_count = self._build_user_vector(skills_text, interests_text, raw_education)
        
        logger.info(f"User vector built with {match_count} skill matches across {len(self.DIMENSIONS)} dimensions")
        
        # Score all careers, then strictly honor the user-selected comparison list.
        all_possible_careers = list(self.CAREER_VECTORS.keys())
        all_scores = self._score_careers(user_vector, match_count, all_possible_careers)
        career_scores = [score for score in all_scores if score["career"] in comparison_careers]

        # Generate decoupled reasoning
        engine_input = {
            "career_scores": career_scores,
            "user_vector": user_vector,
            "top_career": career_scores[0]["career"] if career_scores else "Full-Stack Developer",
            "skill_breakdown": {}
        }
        explanation_output = ExplanationEngine.generate_explanation(engine_input)

        # Let the FinalResponseBuilder construct the strict JSON contract
        return FinalResponseBuilder.build(
            user_profile=user_data,
            normalized_profile={
                "clean_skills": normalized["clean_skills"],
                "detected_intents": normalized["detected_intents"],
                "confidence_map":   normalized["confidence_map"],
            },
            career_scores=career_scores,
            explanation=explanation_output
        )

    def _build_response(self, user_data: dict[str, Any], profile_analysis: dict[str, Any]) -> dict[str, Any]:
        # analyze_profile now directly returns the strict contract built by FinalResponseBuilder
        return profile_analysis

    def _build_user_vector(self, skills_text: str, interests_text: str, education_text: str = "") -> tuple[dict[str, float], int]:
        MAX_SKILL_TOKENS = 100  # Prevent algorithmic DoS
        
        tokens = [t.strip() for t in re.split(r"[,;\n/|]+", skills_text) if t.strip()]
        
        if len(tokens) > MAX_SKILL_TOKENS:
            logger.warning(f"Skills field has {len(tokens)} tokens, truncating to {MAX_SKILL_TOKENS}")
            tokens = tokens[:MAX_SKILL_TOKENS]
        
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

        # 2. Education-based weak priors for IT/CS students.
        education_lower = education_text.lower()
        if "it student" in education_lower or "cs student" in education_lower or "computer science" in education_lower:
            for dim, prior_val in {"backend": 0.12, "linux": 0.10, "networking": 0.08, "database": 0.10, "apis": 0.08}.items():
                if dim in self.DIMENSIONS and user_vector[dim] < 0.35:
                    user_vector[dim] = max(user_vector[dim], prior_val)
        
        return user_vector, match_count

    def _score_careers(self, user_vector: dict[str, float], match_count: int, careers: list[str]) -> list[dict[str, Any]]:
        """
        Score all requested careers against user profile.
        Uses fixed-point arithmetic (multiply by 1000) for deterministic scoring across platforms.
        """
        results = []
        for career in careers:
            career_vector = self.CAREER_VECTORS.get(career)
            if not career_vector:
                career_vector = {dim: 0.2 for dim in self.DIMENSIONS}

            # ─────────────────────────────────────────────────────────────────────
            # 1. COSINE SIMILARITY (55% weight)
            # ─────────────────────────────────────────────────────────────────────
            dot_product_int = 0  # Fixed-point (× 1000)
            mag1_sq_int = 0
            mag2_sq_int = 0

            for dim in self.DIMENSIONS:
                weight = self.DIMENSION_WEIGHTS.get(dim, 1.0)
                u_val_int = int(user_vector.get(dim, 0.0) * 1000)
                c_val_int = int(career_vector.get(dim, 0.0) * 1000)
                weight_int = int(weight * 1000)
                
                u_weighted = (u_val_int * weight_int) // 1000
                c_weighted = (c_val_int * weight_int) // 1000
                
                dot_product_int += (u_weighted * c_weighted) // 1000
                mag1_sq_int += (u_weighted * u_weighted) // 1000
                mag2_sq_int += (c_weighted * c_weighted) // 1000
            
            # Compute magnitudes
            mag1_int = int(math.sqrt(mag1_sq_int / 1000000) * 1000) if mag1_sq_int > 0 else 0
            mag2_int = int(math.sqrt(mag2_sq_int / 1000000) * 1000) if mag2_sq_int > 0 else 0

            if mag1_int == 0 or mag2_int == 0:
                cosine_sim_int = 0
            else:
                denom_int = max(1, (mag1_int * mag2_int) // 1000)
                cosine_sim_int = (dot_product_int * 1000) // denom_int
            
            cosine_sim_int = max(0, min(1000, cosine_sim_int))  # Clamp to [0, 1]

            # ─────────────────────────────────────────────────────────────────────
            # 2. COVERAGE SCORE (30% weight) - Does user have critical skills?
            # ─────────────────────────────────────────────────────────────────────
            coverage_num_int = 0
            coverage_den_int = 0
            for dim in self.DIMENSIONS:
                c_val_int = int(career_vector.get(dim, 0.0) * 1000)
                u_val_int = int(user_vector.get(dim, 0.0) * 1000)
                coverage_num_int += min(u_val_int, c_val_int)
                coverage_den_int += c_val_int
                
            coverage_score_int = (coverage_num_int * 1000) // coverage_den_int if coverage_den_int > 0 else 0

            # ─────────────────────────────────────────────────────────────────────
            # 3. ALIGNMENT BONUS (15% weight) - Does user excel at this career's top dimension?
            # ─────────────────────────────────────────────────────────────────────
            career_top_dim = max(self.DIMENSIONS, key=lambda d: career_vector.get(d, 0.0))
            alignment_bonus_int = int(user_vector.get(career_top_dim, 0.0) * 1000)

            # ─────────────────────────────────────────────────────────────────────
            # 4. UNIFIED FORMULA (fixed-point)
            # hybrid = (0.55 × cosine) + (0.30 × coverage) + (0.15 × alignment)
            # ─────────────────────────────────────────────────────────────────────
            hybrid_int = (
                (550 * cosine_sim_int) // 1000 +
                (300 * coverage_score_int) // 1000 +
                (150 * alignment_bonus_int) // 1000
            )
            
            # Normalize to 0-100 scale
            normalized_score = max(0, min(100, hybrid_int // 10))
            
            # Enforce minimum viability floor (0 is okay for non-matching)
            if normalized_score < 5 and match_count > 0:
                normalized_score = 5  # Small non-zero for at least some signal

            explanation = self._generate_explanation(user_vector, career_vector, career)

            results.append({
                "career": career,
                "score": normalized_score,
                "top_positive_factors": explanation["top_positive_factors"],
                "supporting_factors": explanation["supporting_factors"],
                "missing_critical_skills": explanation["missing_critical_skills"],
                "reasoning_summary": explanation["reasoning_summary"]
            })
            
            logger.debug(f"Scored {career}: {normalized_score}/100 (cosine={cosine_sim_int/1000:.2f}, coverage={coverage_score_int/1000:.2f})")

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

