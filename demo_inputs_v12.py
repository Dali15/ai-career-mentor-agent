from services.intent_normalizer import normalize_user_profile
from ai_engine import generate_career_plan

examples = [
    "security",
    "AI machine learning",
    "docker kubernetes aws",
    "react node sql api",
    "python sql react docker",
]


def run_demo():
    for inp in examples:
        norm = normalize_user_profile("", inp, "")
        domains = norm.get("domains", [])
        # Attempt to get top career/score via ai_engine (uses mock service if no API keys)
        try:
            plan = generate_career_plan({"skills": inp, "education": "", "interests": ""})
            top = plan.get("top_career") or (plan.get("career_scores") and plan["career_scores"][0].get("career"))
            score = None
            if plan.get("career_scores"):
                score = plan["career_scores"][0].get("score")
        except Exception as e:
            top = None
            score = None

        print("INPUT:", inp)
        print("  DOMAINS:", domains)
        print("  TOP CAREER:", top)
        print("  SCORE:", score)
        print()


if __name__ == "__main__":
    run_demo()
