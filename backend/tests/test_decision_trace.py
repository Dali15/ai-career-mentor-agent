"""Quick smoke-test of decision_trace output from live backend."""
import urllib.request, json

URL = "http://localhost:5000/api/career"

tests = [
    {"label": "Data profile",  "skills": "python, sql, data analysis", "education": "CS Degree"},
    {"label": "Web developer", "skills": "react, node, apis",           "education": "none"},
    {"label": "Empty profile", "skills": "",                            "education": "none"},
]

for tc in tests:
    payload = json.dumps({"user_data": {
        "education": tc["education"], "skills": tc["skills"], "interests": ""
    }}).encode()
    req = urllib.request.Request(URL, data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.loads(r.read())

    dt = data.get("decision_trace", {})
    print(f"\n[{tc['label']}]  top_career={data.get('top_career')}")
    print(f"  summary     : {dt.get('summary', '')[:120]}")
    print(f"  why_won     : {dt.get('why_top_career_won', '')[:120]}")
    print(f"  key_drivers : {dt.get('key_drivers', [])}")
    wof = dt.get('why_others_failed', {})
    for career, reason in list(wof.items())[:2]:
        print(f"  [{career}]: {reason[:100]}")
print("\nDone.")
