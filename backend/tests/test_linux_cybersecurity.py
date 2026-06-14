import sys
from services.mock_career_service import MockCareerService

service = MockCareerService()
response = service.analyze_profile({
    "skills": "LINUX",
    "interests": "CYBERSECURITY",
    "selected_careers": ["DevOps Engineer", "Data Analyst", "Backend Developer", "Cloud Engineer"]
})

print(f"Top Career: {response['top_career']}")
for score in response['career_scores']:
    print(f"  {score['career']}: {score['score']}%")
