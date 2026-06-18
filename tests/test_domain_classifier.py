import os
import sys
import pytest

# Ensure backend package is importable when running tests from repository root
ROOT = os.path.dirname(os.path.dirname(__file__))
BACKEND = os.path.join(ROOT, "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

from services.intent_normalizer import normalize_user_profile


@pytest.mark.parametrize(
    "input_text, must_include, must_exclude",
    [
        ("security cybersecurity pentesting ethical hacking", {"penetration_testing", "cybersecurity_analyst", "security_engineering"}, {"backend_engineering"}),
        ("AI machine learning neural networks", {"ai_engineering", "machine_learning_engineering"}, set()),
        ("docker kubernetes aws terraform linux", {"devops_engineering", "platform_engineering"}, set()),
        ("react node sql api", {"full_stack_engineering"}, set()),
        ("python sql react docker", {"software_engineering_general", "full_stack_engineering"}, set()),
    ],
)
def test_domain_classification_deterministic(input_text, must_include, must_exclude):
    """Deterministic domain classification tests for v1.2 taxonomy."""
    # Use intents field empty and education empty for focused test
    out = normalize_user_profile("", input_text, "")
    assert "domains" in out, "normalize_user_profile must include 'domains' field"
    domains = out["domains"]
    # deterministic: same input should yield same domains when called repeatedly
    out2 = normalize_user_profile("", input_text, "")
    assert out2["domains"] == domains

    # must include at least one of the expected domains
    assert any(d in must_include for d in domains), f"Expected one of {must_include} in {domains}"

    # must not include excluded domains
    for bad in must_exclude:
        assert bad not in domains, f"Domain '{bad}' must not be present for input '{input_text}'"
