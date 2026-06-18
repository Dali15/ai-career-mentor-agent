from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def generate_explanation(user_vector: Dict[str, float], career_vector: Dict[str, float], career_name: str) -> Dict[str, Any]:
    """
    Wrapper function for backward compatibility with scoring_engine.py
    Extracts top positive factors, supporting factors, and missing critical skills.
    """
    contributions = []
    from .career_profiles import DIMENSIONS, DIMENSION_WEIGHTS
    
    for dim in DIMENSIONS:
        weight = DIMENSION_WEIGHTS.get(dim, 1.0)
        u_val = user_vector.get(dim, 0.0)
        c_val = career_vector.get(dim, 0.0)
        contrib = u_val * c_val * weight
        contributions.append((dim, contrib, u_val, c_val))
    
    contributions.sort(key=lambda x: x[1], reverse=True)
    
    # Top Positive Factors
    top_positive = [item[0] for item in contributions if item[1] > 0][:2]
    
    # Supporting Factors
    supporting = [item[0] for item in contributions if item[1] > 0][2:4]
    
    # Missing Critical Skills
    missing_critical = [item[0] for item in contributions if item[3] > 0.7 and item[2] < 0.3]
    
    # Reasoning Summary
    direct_signals = sum(1 for dim, contrib, u_val, c_val in contributions if contrib >= 0.12 or (u_val >= 0.35 and c_val >= 0.35))
    if not top_positive:
        reasoning_summary = f"No strong vector alignments found for {career_name}."
    else:
        top_str = " and ".join(top_positive)
        if direct_signals >= 4:
            reasoning_summary = f"Deep experience in {top_str} indicates strong suitability for {career_name} roles."
        else:
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

class ExplanationEngine:
    """
    Pure text reasoning layer. 
    Interprets scoring data and returns structured, human-readable explanations.
    Does NOT calculate or modify scores.
    """
    
    @staticmethod
    def _sanitize_text(text: str, max_length: int = 100) -> str:
        """Sanitize text for safe inclusion in JSON responses."""
        if not isinstance(text, str):
            return ""
        # Remove control characters and limit length
        clean = ''.join(c for c in text if ord(c) >= 32 or c in '\n\t')[:max_length]
        return clean.strip()
    
    @staticmethod
    def generate_explanation(input_data: Dict[str, Any]) -> Dict[str, Any]:
        career_scores = input_data.get("career_scores", [])
        user_vector = input_data.get("user_vector", {})
        top_career = input_data.get("top_career", "Unknown Career")
        skill_breakdown = input_data.get("skill_breakdown", {})
        
        # 1. Structured Reasoning Steps
        reasoning_steps = ExplanationEngine._build_reasoning_steps(user_vector, top_career, career_scores)
        
        # 2. Career-Specific Explanations
        career_specific = ExplanationEngine._build_career_specific(career_scores)
        
        # 3. Final Explanation
        final_explanation = ExplanationEngine._build_final_explanation(top_career, career_scores)
        
        return {
            "reasoning_steps": reasoning_steps,
            "final_explanation": final_explanation,
            "career_specific_explanations": career_specific,
            "decision_trace": ExplanationEngine._build_decision_trace(
                top_career, career_scores, user_vector
            ),
        }

    @staticmethod
    def _build_reasoning_steps(user_vector: Dict[str, float], top_career: str, career_scores: List[Dict[str, Any]]) -> List[str]:
        # Step 1: Profile Interpretation
        active_dims = [ExplanationEngine._sanitize_text(dim) for dim, val in user_vector.items() if val > 0]
        if active_dims:
            step1 = f"Profile interpretation: Analyzed user signals across {len(active_dims)} technical dimensions."
        else:
            step1 = "Profile interpretation: No distinct technical signals detected."
            
        # Step 2: Strongest skill clusters
        sorted_dims = sorted(user_vector.items(), key=lambda x: x[1], reverse=True)
        strong_dims = [ExplanationEngine._sanitize_text(d[0]) for d in sorted_dims if d[1] >= 0.3]
        if strong_dims:
            safe_dims = ', '.join(strong_dims[:3])
            step2 = f"Strongest skill clusters: Identified primary capabilities in {safe_dims}."
        else:
            step2 = "Strongest skill clusters: Skills are distributed or foundational, without a dominating technical cluster."
            
        # Step 3: Weakest areas
        top_career_data = next((c for c in career_scores if c["career"] == top_career), None)
        if top_career_data and top_career_data.get("missing_critical_skills"):
            gaps = [ExplanationEngine._sanitize_text(g) for g in top_career_data["missing_critical_skills"][:2]]
            step3 = f"Weakest areas: Identified critical gaps in {', '.join(gaps)}."
        else:
            step3 = "Weakest areas: No immediate critical gaps detected for the targeted trajectory."
            
        # Step 4: Why top career was selected
        safe_career = ExplanationEngine._sanitize_text(top_career)
        if top_career_data and top_career_data.get("score", 0) >= 10:
            step4 = f"Career selection: {safe_career} was selected due to highest vector alignment and overlap with user strengths."
        else:
            step4 = f"Career selection: Defaulted to foundational {safe_career} trajectory due to low overall alignment scores."
            
        return [step1, step2, step3, step4]

    @staticmethod
    def _build_career_specific(career_scores: List[Dict[str, Any]]) -> Dict[str, str]:
        explanations = {}
        for cs in career_scores:
            career_name = ExplanationEngine._sanitize_text(cs.get("career", "Unknown"))
            top_factors = [ExplanationEngine._sanitize_text(f) for f in cs.get("top_positive_factors", [])]
            supporting = [ExplanationEngine._sanitize_text(f) for f in cs.get("supporting_factors", [])]
            
            if not top_factors:
                msg = f"{career_name}: Low alignment detected across required technical dimensions."
            else:
                factors_str = " and ".join(top_factors)
                msg = f"{career_name}: Strong alignment in {factors_str}"
                if supporting:
                    msg += f", with supporting capabilities in {' and '.join(supporting)}."
                else:
                    msg += "."
            explanations[career_name] = msg
            
        return explanations

    @staticmethod
    def _build_final_explanation(top_career: str, career_scores: List[Dict[str, Any]]) -> str:
        safe_career = ExplanationEngine._sanitize_text(top_career)
        top_career_data = next((c for c in career_scores if c["career"] == top_career), None)
        score = top_career_data.get("score", 0) if top_career_data else 0
        
        if score < 10:
            return (
                f"The provided profile lacks specific technical signals to strongly recommend a specialized path. "
                f"A foundational approach towards {safe_career} is recommended to build core competencies."
            )
        
        if score < 50:
            return (
                f"The profile shows early but promising alignment with {top_career}. "
                f"Focusing on closing critical gaps will significantly accelerate job readiness."
            )
            
        return (
            f"The profile demonstrates strong foundational alignment with {top_career}. "
            f"Existing strengths directly map to industry requirements, indicating high potential for immediate success."
        )

    # ─────────────────────────────────────────────────────────────────────
    # DECISION TRACE  (product-friendly, zero technical jargon)
    # ─────────────────────────────────────────────────────────────────────

    # Dimension → plain-English label for product-facing copy
    _DIM_LABELS: Dict[str, str] = {
        "backend":        "backend development skills",
        "frontend":       "frontend and UI skills",
        "data":           "data workflows",
        "cloud":          "cloud infrastructure",
        "devops":         "DevOps and automation",
        "ai":             "AI and machine learning",
        "mobile":         "mobile development",
        "database":       "database and SQL skills",
        "system_design":  "system design and architecture",
        "ui_ux":          "UX and interface design",
        "networking":     "networking and infrastructure",
        "security":       "security practices",
        "testing":        "testing and quality assurance",
        "machine_learning": "machine learning fundamentals",
    }

    @staticmethod
    def _label(dim: str) -> str:
        return ExplanationEngine._DIM_LABELS.get(dim, dim.replace("_", " "))

    @staticmethod
    def _build_decision_trace(
        top_career: str,
        career_scores: List[Dict[str, Any]],
        user_vector: Dict[str, float],
    ) -> Dict[str, Any]:
        """Generate a product-friendly decision audit trail — no maths, no jargon."""
        top_data   = next((c for c in career_scores if c["career"] == top_career), None)
        top_score  = top_data.get("score", 0) if top_data else 0
        others     = [c for c in career_scores if c["career"] != top_career]

        summary          = ExplanationEngine._build_trace_summary(top_career, top_score, top_data, user_vector)
        why_won          = ExplanationEngine._build_why_won(top_career, top_score, top_data)
        why_others_lost  = ExplanationEngine._build_why_others_lost(others, top_score)
        key_drivers      = ExplanationEngine._build_key_drivers(top_data, user_vector)

        return {
            "summary":           summary,
            "why_top_career_won": why_won,
            "why_others_failed": why_others_lost,
            "key_drivers":       key_drivers,
        }

    @staticmethod
    def _build_trace_summary(top_career: str, score: int, top_data: Any, user_vector: Dict[str, float] | None = None) -> str:
        if score < 10:
            return (
                "The profile doesn't yet show strong signals for any specific career path. "
                "Starting with foundational skills will open up clearer options over time."
            )
        if score < 40:
            top_factors = (top_data or {}).get("top_positive_factors", [])
            hint = f" with early signals in {ExplanationEngine._label(top_factors[0])}" if top_factors else ""
            return (
                f"The analysis found a beginning alignment with {top_career}{hint}. "
                "There is clear room to grow, and targeted learning will make a significant impact."
            )
        if score < 70:
            top_factors = (top_data or {}).get("top_positive_factors", [])
            strengths_str = " and ".join(ExplanationEngine._label(f) for f in top_factors[:2]) if top_factors else "relevant skills"
            return (
                f"The profile shows a solid fit with {top_career}, driven by experience in {strengths_str}. "
                "A few targeted improvements would push this into a highly competitive position."
            )
        top_factors = (top_data or {}).get("top_positive_factors", [])
        supporting = (top_data or {}).get("supporting_factors", [])
        strengths_str = " and ".join(ExplanationEngine._label(f) for f in top_factors[:2]) if top_factors else "core skills"
        direct_signals = sum(
            1
            for dim in set(top_factors + supporting)
            if (user_vector or {}).get(dim, 0.0) >= 0.35
        )
        if direct_signals >= 4:
            return (
                f"This profile is a strong match for {top_career}. "
                f"Deep experience in {strengths_str} directly maps to what employers in this role look for."
            )
        return (
            f"This profile is a strong match for {top_career}. "
            f"These strengths map well to the core requirements of this role."
        )

    @staticmethod
    def _build_why_won(top_career: str, score: int, top_data: Any) -> str:
        if not top_data or score < 10:
            return f"{top_career} appeared as a default starting point due to lack of specific signals in the profile."

        top_factors = top_data.get("top_positive_factors", [])
        supporting  = top_data.get("supporting_factors", [])
        missing     = top_data.get("missing_critical_skills", [])

        parts = []
        if top_factors:
            labels = " and ".join(ExplanationEngine._label(f) for f in top_factors[:2])
            parts.append(f"showed the strongest alignment in {labels}")
        if supporting:
            sup_labels = " and ".join(ExplanationEngine._label(f) for f in supporting[:2])
            parts.append(f"backed by solid exposure to {sup_labels}")

        reason = ", ".join(parts) if parts else "outperformed other paths based on overall skill coverage"
        sentence = f"{top_career} was selected because this profile {reason}."

        if missing:
            gap_labels = " and ".join(ExplanationEngine._label(g) for g in missing[:2])
            sentence += f" The main area left to develop is {gap_labels}."

        return sentence

    @staticmethod
    def _build_why_others_lost(
        others: List[Dict[str, Any]],
        top_score: int,
    ) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for career_data in others:
            career = career_data.get("career", "Unknown")
            score  = career_data.get("score", 0)
            missing = career_data.get("missing_critical_skills", [])
            factors = career_data.get("top_positive_factors", [])
            gap_from_top = top_score - score

            if score < 10:
                result[career] = (
                    f"Very limited alignment detected. This path requires a fundamentally different skill set "
                    f"that isn't present in the current profile."
                )
                continue

            parts = []
            if missing:
                gap_labels = " and ".join(ExplanationEngine._label(g) for g in missing[:2])
                parts.append(f"limited exposure to {gap_labels}")
            if gap_from_top > 30:
                parts.append("overall skill coverage falls significantly short of this role's requirements")
            elif gap_from_top > 15:
                parts.append("a moderate gap exists compared to the recommended path")
            elif factors:
                parts.append(f"while {ExplanationEngine._label(factors[0])} is present, it doesn't reach the threshold needed")

            if parts:
                result[career] = f"Scored lower due to: {'; '.join(parts)}."
            else:
                result[career] = f"Close contender but ranked below {top_score} — strengthening core areas would move this up."

        return result

    @staticmethod
    def _build_key_drivers(
        top_data: Any,
        user_vector: Dict[str, float],
    ) -> List[str]:
        """Extract the top 3 human-readable reasons the scoring went the way it did."""
        drivers: List[str] = []

        if not top_data:
            return ["No clear skill signals detected in the profile."]

        top_factors = top_data.get("top_positive_factors", [])
        supporting  = top_data.get("supporting_factors", [])
        missing     = top_data.get("missing_critical_skills", [])
        score       = top_data.get("score", 0)

        # Driver 1: primary strength
        if top_factors:
            primary = ExplanationEngine._label(top_factors[0])
            drivers.append(f"Strong foundation in {primary} — the single biggest factor in this recommendation.")

        # Driver 2: secondary signal or coverage
        if len(top_factors) > 1:
            secondary = ExplanationEngine._label(top_factors[1])
            drivers.append(f"Good exposure to {secondary} provided additional alignment with this career's requirements.")
        elif supporting:
            sup = ExplanationEngine._label(supporting[0])
            drivers.append(f"Supporting experience in {sup} contributed positively to the overall match.")

        # Driver 3: gap or confidence signal
        if missing:
            gap = ExplanationEngine._label(missing[0])
            drivers.append(f"Developing {gap} would be the highest-impact next step to strengthen this recommendation.")
        elif score >= 70:
            drivers.append("Broad skill coverage across multiple required areas makes this a high-confidence match.")
        else:
            drivers.append("Increasing depth in existing skill areas will improve alignment and readiness.")

        return drivers[:3]
