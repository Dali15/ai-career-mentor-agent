"""
Edge case tests for AI Career Mentor Agent backend.
Tests empty inputs, oversized inputs, special characters, and malicious inputs.
"""

import pytest
import json
from services.mock_career_service import MockCareerService


@pytest.fixture
def service():
    return MockCareerService()


class TestEmptyAndMinimalInputs:
    """Test edge cases with empty or minimal input."""
    
    def test_completely_empty_profile(self, service):
        """Empty profile should not crash and should return valid structure."""
        result = service.analyze_profile({
            "education": "",
            "skills": "",
            "interests": ""
        })
        assert result is not None
        assert "career_scores" in result
        assert isinstance(result["career_scores"], list)
        assert len(result["career_scores"]) > 0
    
    def test_whitespace_only_profile(self, service):
        """Profile with only whitespace should be treated as empty."""
        result = service.analyze_profile({
            "education": "   \n  \t  ",
            "skills": "   ",
            "interests": "\n\n"
        })
        assert result is not None
        assert "career_scores" in result
    
    def test_single_skill(self, service):
        """Single skill should be processed without error."""
        result = service.analyze_profile({
            "education": "",
            "skills": "Python",
            "interests": ""
        })
        assert result is not None
        assert result["top_career"] in service.DEFAULT_COMPARISON_CAREERS


class TestLargeInputs:
    """Test oversized inputs that could cause DoS."""
    
    def test_extremely_large_skills_field(self, service):
        """Very large skills field should be truncated, not crash."""
        huge_skills = "Python, " * 10000  # ~100KB
        result = service.analyze_profile({
            "education": "",
            "skills": huge_skills,
            "interests": ""
        })
        assert result is not None
        # Verify JSON is valid and serializable
        json_str = json.dumps(result)
        assert isinstance(json_str, str)
    
    def test_many_comma_separated_tokens(self, service):
        """Excessive number of tokens should be truncated to MAX_SKILL_TOKENS."""
        tokens = ", ".join([f"skill{i}" for i in range(500)])
        result = service.analyze_profile({
            "education": "",
            "skills": tokens,
            "interests": ""
        })
        assert result is not None


class TestSpecialCharacters:
    """Test inputs with special characters."""
    
    def test_json_breaking_characters(self, service):
        """Input with JSON control characters should not break JSON output."""
        result = service.analyze_profile({
            "education": 'School "with quotes"',
            "skills": 'Python, <HTML>, {JSON}, [arrays]',
            "interests": "Testing: special\\chars"
        })
        assert result is not None
        # Verify result is valid JSON
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        assert parsed is not None
    
    def test_unicode_characters(self, service):
        """Unicode characters should be handled safely."""
        result = service.analyze_profile({
            "education": "Université de Paris",
            "skills": "Python, 机器学习, প্রোগ্রামিং",
            "interests": "AI, データサイエンス"
        })
        assert result is not None
        json_str = json.dumps(result)
        assert isinstance(json_str, str)
    
    def test_control_characters(self, service):
        """Null bytes and control chars should be handled."""
        result = service.analyze_profile({
            "education": "Test\x00School",
            "skills": "Python\x01C++\x02Java",
            "interests": ""
        })
        assert result is not None


class TestUnrelatedProfiles:
    """Test profiles with skills unrelated to tech careers."""
    
    def test_purely_unrelated_skills(self, service):
        """Profile with zero tech skills should have low scores."""
        result = service.analyze_profile({
            "education": "Art School, Music Conservatory",
            "skills": "Painting, Sculpture, Drawing, Music Composition",
            "interests": "Fine Arts, Performance"
        })
        assert result is not None
        # All career scores should be low (< 30)
        assert all(score["score"] < 30 for score in result["career_scores"])
    
    def test_cooking_and_music_profile(self, service):
        """Non-technical background should not match tech careers well."""
        result = service.analyze_profile({
            "education": "Culinary Arts Diploma",
            "skills": "Cooking, Baking, Menu Planning, Food Styling",
            "interests": "Cooking shows, Music"
        })
        assert result is not None
        # Top career should have low confidence
        assert result["career_scores"][0]["score"] < 40


class TestSelectedCareersValidation:
    """Test handling of selected_careers parameter."""
    
    def test_empty_selected_careers_list(self, service):
        """Empty selected_careers should fallback to defaults."""
        result = service.analyze_profile({
            "education": "",
            "skills": "Python, SQL",
            "interests": "",
            "selected_careers": []
        })
        assert result is not None
        # Should still include the top absolute career
        assert len(result["career_scores"]) >= 1
    
    def test_invalid_selected_careers_type(self, service):
        """Non-list selected_careers should be ignored."""
        result = service.analyze_profile({
            "education": "",
            "skills": "Python",
            "interests": "",
            "selected_careers": "Backend Developer"  # String instead of list
        })
        assert result is not None


class TestResponseIntegrity:
    """Test that response structure is always valid."""
    
    def test_response_has_required_fields(self, service):
        """Response should always have required top-level fields."""
        result = service.analyze_profile({
            "education": "BSc Computer Science",
            "skills": "Python, SQL, React",
            "interests": "Web Development"
        })
        required_fields = [
            "top_career", "career_scores", "reasoning", "roadmap",
            "strengths", "gaps", "normalization", "final_explanation"
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
    
    def test_career_scores_structure(self, service):
        """Each career score should have complete structure."""
        result = service.analyze_profile({
            "education": "",
            "skills": "Python, Docker",
            "interests": ""
        })
        for score in result["career_scores"]:
            required = [
                "career", "score", "top_positive_factors",
                "supporting_factors", "missing_critical_skills",
                "reasoning_summary"
            ]
            for field in required:
                assert field in score, f"Career score missing field: {field}"
            assert isinstance(score["score"], int)
            assert 0 <= score["score"] <= 100
    
    def test_response_json_serializable(self, service):
        """Response must be JSON-serializable."""
        result = service.analyze_profile({
            "education": "Any education",
            "skills": "Any skills",
            "interests": "Any interests"
        })
        # This should not raise
        json_str = json.dumps(result)
        reparsed = json.loads(json_str)
        assert reparsed is not None


class TestDeterminism:
    """Test that same input produces same output (determinism)."""
    
    def test_same_input_same_output(self, service):
        """Identical inputs should produce identical scores."""
        input_data = {
            "education": "BSc Computer Science",
            "skills": "Python, SQL, Docker, Kubernetes",
            "interests": "Cloud, DevOps"
        }
        
        result1 = service.analyze_profile(input_data.copy())
        result2 = service.analyze_profile(input_data.copy())
        
        # Top careers should match
        assert result1["top_career"] == result2["top_career"]
        
        # Scores should be identical
        scores1 = {s["career"]: s["score"] for s in result1["career_scores"]}
        scores2 = {s["career"]: s["score"] for s in result2["career_scores"]}
        assert scores1 == scores2
