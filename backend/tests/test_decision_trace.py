"""Quick smoke-test of decision_trace output from the live backend."""
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
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


TEST_CASES = [
    {"label": "Data profile",  "skills": "python, sql, data analysis", "education": "CS Degree"},
    {"label": "Web developer", "skills": "react, node, apis",           "education": "none"},
    {"label": "Empty profile", "skills": "",                            "education": "none"},
]

def test_decision_trace_output():
    for tc in TEST_CASES:
        data = _post({
            "user_data": {
                "education": tc["education"],
                "skills": tc["skills"],
                "interests": "",
            }
        })

        dt = data.get("decision_trace", {})
        assert isinstance(dt, dict)
        assert data.get("top_career")
        assert isinstance(dt.get("summary", ""), str)
        assert isinstance(dt.get("why_top_career_won", ""), str)
        assert isinstance(dt.get("key_drivers", []), list)
