"""Live end-to-end API test for the Intent Normalizer layer."""
import json
import urllib.request

URL = "http://localhost:5000/api/career"


def _post(payload: dict) -> dict:
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


TEST_CASES = [
    {"label": "French input",      "skills": "je fais du dev web",         "education": "none", "interests": ""},
    {"label": "English slang",     "skills": "i like ai and web apps",     "education": "none", "interests": ""},
    {"label": "Noise + data",      "skills": "sql python maybe data stuff", "education": "none", "interests": ""},
    {"label": "Unrelated input",   "skills": "Painting, Music, Cooking",   "education": "none", "interests": ""},
    {"label": "Dev profile",       "skills": "React, Docker, AI, Excel",   "education": "none", "interests": ""},
    {"label": "Arabic input",      "skills": "web apps",                    "education": "none", "interests": ""},
    {"label": "Noise filtered",    "skills": "web dev, idk stuff etc",     "education": "none", "interests": ""},
]

def test_live_normalizer_e2e():
    for tc in TEST_CASES:
        data = _post({
            "user_data": {
                "education": tc["education"],
                "skills": tc["skills"],
                "interests": tc["interests"],
            }
        })

        norm = data.get("normalization", {})
        assert isinstance(norm.get("clean_skills", []), list)
        assert isinstance(norm.get("detected_intents", []), list)
        assert data.get("top_career")
        assert isinstance(data.get("career_scores", []), list)
