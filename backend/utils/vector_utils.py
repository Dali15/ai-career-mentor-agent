import math
from typing import Dict, List, Tuple
import re

from ..models.career_profiles import DIMENSIONS, DIMENSION_WEIGHTS, SKILL_VECTORS, INTEREST_BOOSTS

def calculate_cosine_similarity(user_vector: Dict[str, float], career_vector: Dict[str, float]) -> float:
    dot_product = 0.0
    mag1_sq = 0.0
    mag2_sq = 0.0

    total_dot = sum(
        (user_vector.get(d, 0) * DIMENSION_WEIGHTS.get(d, 1.0)) * 
        (career_vector.get(d, 0) * DIMENSION_WEIGHTS.get(d, 1.0)) 
        for d in DIMENSIONS
    )
    
    for dim in DIMENSIONS:
        weight = DIMENSION_WEIGHTS.get(dim, 1.0)
        u_val = user_vector.get(dim, 0.0) * weight
        c_val = career_vector.get(dim, 0.0) * weight
        
        dim_dot = u_val * c_val
        if total_dot > 0 and (dim_dot / total_dot) > 0.4:
            dim_dot = total_dot * 0.4
            
        dot_product += dim_dot
        mag1_sq += u_val ** 2
        mag2_sq += c_val ** 2
    
    mag1 = math.sqrt(mag1_sq)
    mag2 = math.sqrt(mag2_sq)

    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)

def calculate_coverage_score(user_vector: Dict[str, float], career_vector: Dict[str, float]) -> float:
    coverage_num = 0.0
    coverage_den = 0.0
    for dim in DIMENSIONS:
        c_val = career_vector.get(dim, 0.0)
        u_val = user_vector.get(dim, 0.0)
        coverage_num += min(u_val, c_val)
        coverage_den += c_val
        
    return (coverage_num / coverage_den) if coverage_den > 0 else 0.0

def build_user_vector(skills_text: str, interests_text: str, education_text: str = "") -> Tuple[Dict[str, float], int]:
    tokens = [t.strip().lower() for t in re.split(r"[,;\n/|]+", skills_text) if t.strip()]
    user_vector = {dim: 0.0 for dim in DIMENSIONS}
    match_count = 0

    # Primary skill vector contributions
    for token in tokens:
        vec = SKILL_VECTORS.get(token)
        if vec:
            match_count += 1
            for dim, val in vec.items():
                user_vector[dim] += val
    
    if match_count > 0:
        for dim in DIMENSIONS:
            user_vector[dim] = min(1.0, user_vector[dim] / match_count)

    # Education-based weak priors for foundational IT paths, capped to a gentle 15% contribution.
    education_lower = education_text.lower()
    if "it student" in education_lower or "cs student" in education_lower or "computer science" in education_lower:
        education_priors = {
            "backend": 0.12,
            "linux": 0.10,
            "networking": 0.08,
            "database": 0.10,
            "apis": 0.08,
            "system_design": 0.06,
        }
        prior_scale = 0.15
        for dim, prior_val in education_priors.items():
            if dim in user_vector:
                user_vector[dim] = min(1.0, user_vector[dim] + prior_scale * prior_val)

    return user_vector, match_count
