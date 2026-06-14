import os
import sys

# Add the backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.mock_career_service import MockCareerService

def validate_response(response: dict):
    # Check all required keys exist — including ExplanationEngine fields
    required_keys = [
        "career_scores", "top_career", "reasoning",
        "roadmap", "certifications", "learning_resources",
        "strengths", "gaps",
        "final_explanation", "career_specific_explanations"
    ]
    for key in required_keys:
        assert key in response, f"Missing required key: {key}"
        assert response[key] is not None, f"Key {key} cannot be None"

    # Validate scores are 0-100 and top_career logic
    career_scores = response["career_scores"]
    assert len(career_scores) > 0, "career_scores cannot be empty"

    career_names = []
    for cs in career_scores:
        assert "score" in cs, "Score missing from career"
        assert 0 <= cs["score"] <= 100, f"Score out of bounds: {cs['score']}"
        assert "career" in cs, "Career name missing"
        career_names.append(cs["career"])

    assert response["top_career"] in career_names, "top_career must exist in career_scores"

    # Roadmap must always have all 3 months
    roadmap = response["roadmap"]
    assert "month_1" in roadmap, "Roadmap missing month_1"
    assert "month_2" in roadmap, "Roadmap missing month_2"
    assert "month_3" in roadmap, "Roadmap missing month_3"

    # Reasoning = 4 structured steps from ExplanationEngine
    reasoning = response["reasoning"]
    assert isinstance(reasoning, list) and len(reasoning) == 4, f"Reasoning must have exactly 4 steps, got {len(reasoning)}"
    assert all(r.strip() != "" for r in reasoning), "No reasoning step can be empty"

    # final_explanation must be a non-empty string
    assert isinstance(response["final_explanation"], str), "final_explanation must be a string"
    assert response["final_explanation"].strip() != "", "final_explanation cannot be empty"

    # career_specific_explanations must cover all careers
    assert isinstance(response["career_specific_explanations"], dict), "career_specific_explanations must be a dict"
    for name in career_names:
        assert name in response["career_specific_explanations"], f"Missing explanation for career: {name}"

def run_test(name, user_data, expectations):
    print(f"Running Test: {name} ...", end=" ")
    try:
        service = MockCareerService()
        response1 = service.analyze_profile(user_data)
        response2 = service.analyze_profile(user_data)
        
        # 1. Validate response structure
        validate_response(response1)
        
        # 2. Validate determinism (identical runs)
        assert response1 == response2, "Responses are not deterministic across runs"
        
        # 3. Execute specific expectations
        expectations(response1)
        
        print("PASS")
    except Exception as e:
        print("FAIL")
        print(f"  Reason: {str(e)}")
        import traceback
        traceback.print_exc()

def expectations_test_1(response):
    # Test Case 1 — Empty Input
    top_score = response["career_scores"][0]["score"]
    assert top_score <= 10, f"Score too high for empty input: {top_score}"
    # reasoning is now 4 structured steps; check step 1 signals empty profile
    assert "No distinct technical signals detected" in response["reasoning"][0]
    # final_explanation is the human-readable summary
    assert "lacks specific technical signals" in response["final_explanation"]

def expectations_test_2(response):
    # Test Case 2 — Single Skill Bias (SQL)
    top = response["career_scores"][0]
    second = response["career_scores"][1]
    
    assert top["career"] == "Data Analyst", f"Expected Data Analyst top, got {top['career']}"
    assert second["career"] == "Backend Developer", f"Expected Backend Developer second, got {second['career']}"
    
    # DevOps / Cloud should be lower
    for c in response["career_scores"][2:]:
        if c["career"] in ["DevOps Engineer", "Cloud Engineer"]:
            assert c["score"] < top["score"], "DevOps/Cloud should be lower"

def expectations_test_3(response):
    # Test Case 3 — Mixed Stack (Python, Flask, SQL, APIs)
    top_career = response["top_career"]
    assert top_career in ["Backend Developer", "Data Analyst"], f"Expected Backend or Data Analyst, got {top_career}"

def expectations_test_4(response):
    # Test Case 4 — Unrelated Skills (Painting, Music, Cooking)
    top_score = response["career_scores"][0]["score"]
    assert top_score < 10, f"Expected score < 10, got {top_score}"
    # final_explanation signals weak alignment (not reasoning[0], which is now step-based)
    assert "lacks specific technical signals" in response["final_explanation"]
    assert len(response["certifications"]) == 0, "Certifications should not be generated"

def expectations_test_5(response):
    # Test Case 5 — Realistic Dev Profile
    top_career = response["top_career"]
    # React, Docker, AI, Excel -> Full-Stack / DevOps / Frontend / Cloud 
    # Just ensure Data Analyst isn't dominating incorrectly
    assert top_career != "Data Analyst", "Data Analyst incorrectly dominating realistic dev profile"

def run_all_tests():
    print("Starting Regression Test Suite...\n")
    
    run_test(
        "Test Case 1 — Empty Input",
        {"skills": "", "education": "", "interests": ""},
        expectations_test_1
    )
    
    run_test(
        "Test Case 2 — Single Skill Bias",
        {"skills": "SQL", "education": "", "interests": ""},
        expectations_test_2
    )
    
    run_test(
        "Test Case 3 — Mixed Stack",
        {"skills": "Python, Flask, SQL, APIs", "education": "", "interests": ""},
        expectations_test_3
    )
    
    run_test(
        "Test Case 4 — Unrelated Skills",
        {"skills": "Painting, Music, Cooking", "education": "", "interests": ""},
        expectations_test_4
    )
    
    run_test(
        "Test Case 5 — Realistic Dev Profile",
        {"skills": "React, Docker, AI, Excel", "education": "", "interests": ""},
        expectations_test_5
    )
    
    print("\nAll tests completed.")

if __name__ == "__main__":
    run_all_tests()
