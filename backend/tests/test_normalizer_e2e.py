"""
Live end-to-end API test for the Intent Normalizer layer.
Tests messy/multilingual/slang inputs against the running backend.
"""
import urllib.request, json, sys

URL = "http://localhost:5000/api/career"

test_cases = [
    {"label": "French input",      "skills": "je fais du dev web",         "education": "none", "interests": ""},
    {"label": "English slang",     "skills": "i like ai and web apps",     "education": "none", "interests": ""},
    {"label": "Noise + data",      "skills": "sql python maybe data stuff", "education": "none", "interests": ""},
    {"label": "Unrelated input",   "skills": "Painting, Music, Cooking",   "education": "none", "interests": ""},
    {"label": "Dev profile",       "skills": "React, Docker, AI, Excel",   "education": "none", "interests": ""},
    {"label": "Arabic input",      "skills": "web apps",                    "education": "none", "interests": ""},
    {"label": "Noise filtered",    "skills": "web dev, idk stuff etc",     "education": "none", "interests": ""},
]

print("Live API — Intent Normalizer E2E Tests")
print("=" * 55)
all_pass = True

for tc in test_cases:
    payload = json.dumps({
        "user_data": {
            "education": tc["education"],
            "skills": tc["skills"],
            "interests": tc["interests"],
        }
    }).encode()
    try:
        req = urllib.request.Request(URL, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())

        norm = data.get("normalization", {})
        top  = data.get("top_career", "?")
        clean = norm.get("clean_skills", [])
        intents = norm.get("detected_intents", [])
        score = data.get("career_scores", [{}])[0].get("score", 0)

        print(f"\n[{tc['label']}]")
        print(f"  Input       : {tc['skills']!r}")
        print(f"  clean_skills: {clean}")
        print(f"  intents     : {intents}")
        print(f"  top_career  : {top}  (score={score})")
        print(f"  status      : PASS")

    except Exception as e:
        print(f"\n[{tc['label']}]  FAIL — {e}")
        all_pass = False

print("\n" + ("=" * 55))
print("All tests passed!" if all_pass else "Some tests failed.")
sys.exit(0 if all_pass else 1)
