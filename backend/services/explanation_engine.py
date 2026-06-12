from typing import Dict, Any
from .career_profiles import DIMENSIONS, DIMENSION_WEIGHTS

def generate_explanation(user_vector: Dict[str, float], career_vector: Dict[str, float], career_name: str) -> Dict[str, Any]:
    contributions = []
    for dim in DIMENSIONS:
        weight = DIMENSION_WEIGHTS.get(dim, 1.0)
        u_val = user_vector.get(dim, 0.0)
        c_val = career_vector.get(dim, 0.0)
        contrib = u_val * c_val * weight
        contributions.append((dim, contrib, u_val, c_val))
        
    contributions.sort(key=lambda x: x[1], reverse=True)
    
    top_positive = [item[0] for item in contributions if item[1] > 0][:2]
    supporting = [item[0] for item in contributions if item[1] > 0][2:4]
    missing_critical = [item[0] for item in contributions if item[3] > 0.7 and item[2] < 0.3]
    
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
