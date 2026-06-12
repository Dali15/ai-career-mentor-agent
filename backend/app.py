from flask import Flask, jsonify, request
from flask_cors import CORS

from ai_engine import generate_career_plan

app = Flask(__name__)
CORS(app)


@app.post("/api/career")
def career_route():
    payload = request.get_json(silent=True) or {}
    user_data = payload.get("user_data") if isinstance(payload.get("user_data"), dict) else payload
    if not isinstance(user_data, dict):
        user_data = {}

    print("🔥 USER DATA:", user_data)

    education = str(user_data.get("education", "")).strip()
    skills = str(user_data.get("skills", "")).strip()
    interests = str(user_data.get("interests", "")).strip()

    if not any([education, skills, interests]):
        legacy_message = str(payload.get("message", "")).strip()
        if not legacy_message:
            return jsonify({"error": "education, skills, or interests is required"}), 400
        user_data = {
            "education": "Not provided",
            "skills": legacy_message,
            "interests": legacy_message,
        }

    response = generate_career_plan(user_data)
    print("🔥 AI RESPONSE TYPE:", type(response))
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
