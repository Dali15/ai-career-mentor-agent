import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.intent_normalizer import normalize_user_profile


cases = [
    ('', 'i like ai and web apps', ''),
    ('', 'sql python maybe data stuff', ''),
    ('', 'je fais du dev web', ''),
    ('CS Degree', 'ai stuff, automation, cloud', 'building apps'),
    ('', 'React, Docker, AI, Excel', ''),
    ('', 'web dev, idk stuff etc', ''),
    ('', 'Painting, Music, Cooking', ''),
    ('', 'mobile dev, flutter', 'mobile'),
    ('', 'analyse de donnees', ''),
]

print("Intent Normalizer — Real-World Validation\n" + "="*50)
for edu, skills, interests in cases:
    r = normalize_user_profile(edu, skills, interests)
    conf = {k: round(v, 2) for k, v in r['confidence_map'].items()}
    print(f"\nIN  : {skills!r}")
    print(f"  clean_skills     : {r['clean_skills']}")
    print(f"  detected_intents : {r['detected_intents']}")
    print(f"  confidence_map   : {conf}")
