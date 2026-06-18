import logging
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ai_engine import generate_career_plan

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Configure rate limiting. Tests and local runs can disable it via RATELIMIT_ENABLED=false.
app.config['RATELIMIT_ENABLED'] = os.getenv('RATELIMIT_ENABLED', 'false').lower() in ('1', 'true', 'yes')
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"] if app.config['RATELIMIT_ENABLED'] else None,
    storage_uri="memory://"
)

# Configure security
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB max request size
CORS(
    app,
    origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    supports_credentials=False
)


career_route_decorator = limiter.limit("100 per minute") if app.config['RATELIMIT_ENABLED'] else (lambda fn: fn)


@app.post("/api/career")
@career_route_decorator
def career_route():
    """Generate a career plan based on user profile."""
    # Parse JSON request
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        logger.warning(f"JSON parse error: {e}")
        return jsonify({"error": "Invalid JSON in request body"}), 400
    
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400
    
    user_data = payload.get("user_data", {})
    if not isinstance(user_data, dict):
        user_data = {}

    # Validate and sanitize input fields
    MAX_FIELD_LENGTH = 5000
    education = str(user_data.get("education", "")).strip()[:MAX_FIELD_LENGTH]
    skills = str(user_data.get("skills", "")).strip()[:MAX_FIELD_LENGTH]
    interests = str(user_data.get("interests", "")).strip()[:MAX_FIELD_LENGTH]

    if not any([education, skills, interests]):
        legacy_message = str(payload.get("message", "")).strip()[:MAX_FIELD_LENGTH]
        if not legacy_message:
            return jsonify({"error": "At least one of education, skills, or interests is required"}), 400
        logger.info("Processing legacy 'message' field")
        user_data = {
            "education": "Not provided",
            "skills": legacy_message,
            "interests": legacy_message,
        }
    
    logger.debug(f"Processing profile: education={len(education)}c, skills={len(skills)}c, interests={len(interests)}c")

    response = generate_career_plan(user_data)

    # Optional: include deterministic pipeline steps for UI "thinking" simulation
    include_pipeline = str(payload.get("include_pipeline", "false")).lower() in ("true", "1", "yes")
    if include_pipeline:
        response["pipeline_steps"] = [
            "Analyzing profile",
            "Extracting skill vectors",
            "Computing vector space",
            "Scoring careers",
            "Generating explanation",
        ]

    logger.debug(f"Career plan generated: top_career={response.get('top_career')}, ai_source={response.get('ai_source')}")
    return jsonify(response)




@app.after_request
def set_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self' http://localhost:* http://127.0.0.1:*; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    return response


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5000))
    
    if debug_mode:
        logger.warning("⚠️  Flask debug mode is ENABLED. Disable in production!")
    
    app.run(host=host, port=port, debug=debug_mode)

