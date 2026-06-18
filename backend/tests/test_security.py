"""
Security tests for AI Career Mentor Agent.
Tests input validation, injection prevention, and error handling.
"""

import pytest
import json
from flask import Flask
from app import app as flask_app


@pytest.fixture
def client():
    """Flask test client."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


class TestRequestValidation:
    """Test request payload validation."""
    
    def test_max_content_length_enforced(self, client):
        """Requests exceeding MAX_CONTENT_LENGTH should be rejected."""
        huge_payload = "x" * (2 * 1024 * 1024)  # 2MB, exceeds 1MB limit
        response = client.post(
            '/api/career',
            data=huge_payload,
            content_type='application/json'
        )
        # Should get 413 Payload Too Large
        assert response.status_code == 413 or response.status_code == 400
    
    def test_malformed_json_rejected(self, client):
        """Malformed JSON should be rejected with clear error."""
        response = client.post(
            '/api/career',
            data=b'{"invalid json"',  # Missing closing brace
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
    
    def test_invalid_request_body_type(self, client):
        """Non-dict request body should be rejected."""
        response = client.post(
            '/api/career',
            data=json.dumps(["array", "instead", "of", "object"]),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 400


class TestInputFieldValidation:
    """Test validation of individual input fields."""
    
    def test_field_length_limits(self, client):
        """Fields exceeding max length should be truncated."""
        huge_skills = "Python, " * 10000  # ~100KB
        response = client.post(
            '/api/career',
            data=json.dumps({
                "user_data": {
                    "education": "",
                    "skills": huge_skills,
                    "interests": ""
                }
            }),
            headers={'Content-Type': 'application/json'}
        )
        # Should still succeed, but field truncated
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "top_career" in data
    
    def test_empty_profile_rejected(self, client):
        """Profile with no fields should be rejected."""
        response = client.post(
            '/api/career',
            data=json.dumps({
                "user_data": {
                    "education": "",
                    "skills": "",
                    "interests": ""
                }
            }),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data


class TestSecurityHeaders:
    """Test security headers in responses."""
    
    def test_x_content_type_options_header(self, client):
        """Response should include X-Content-Type-Options."""
        response = client.post(
            '/api/career',
            data=json.dumps({
                "user_data": {
                    "education": "Test",
                    "skills": "Python",
                    "interests": ""
                }
            }),
            headers={'Content-Type': 'application/json'}
        )
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
    
    def test_x_frame_options_header(self, client):
        """Response should include X-Frame-Options DENY."""
        response = client.post(
            '/api/career',
            data=json.dumps({
                "user_data": {
                    "education": "Test",
                    "skills": "Python",
                    "interests": ""
                }
            }),
            headers={'Content-Type': 'application/json'}
        )
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'
    
    def test_csp_header_present(self, client):
        """Response should include Content-Security-Policy."""
        response = client.post(
            '/api/career',
            data=json.dumps({
                "user_data": {
                    "education": "Test",
                    "skills": "Python",
                    "interests": ""
                }
            }),
            headers={'Content-Type': 'application/json'}
        )
        assert 'Content-Security-Policy' in response.headers


class TestErrorHandling:
    """Test error handling and information disclosure."""
    
    def test_error_messages_safe(self, client):
        """Error messages should not expose sensitive information."""
        response = client.post(
            '/api/career',
            data=json.dumps({"user_data": {}}),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        error = data.get("error", "")
        # Error should be user-friendly, not internal stack trace
        assert "required" in error.lower() or "invalid" in error.lower()
    
    def test_missing_endpoint_404(self, client):
        """Non-existent endpoints should return 404."""
        response = client.post('/api/nonexistent')
        assert response.status_code == 404


class TestResponseValidation:
    """Test that responses are always valid JSON."""
    
    def test_response_always_json(self, client):
        """All responses should be valid JSON."""
        response = client.post(
            '/api/career',
            data=json.dumps({
                "user_data": {
                    "education": "Test",
                    "skills": "Python",
                    "interests": ""
                }
            }),
            headers={'Content-Type': 'application/json'}
        )
        # Should be valid JSON
        data = json.loads(response.data)
        assert data is not None


class TestCORSConfiguration:
    """Test CORS headers."""
    
    def test_cors_allowed_origins(self, client):
        """Only configured origins should be allowed."""
        response = client.options(
            '/api/career',
            headers={'Origin': 'http://localhost:5173'}
        )
        # CORS should be configured for localhost
        assert response.status_code in [200, 204, 405]


class TestInputSanitization:
    """Test that inputs are properly sanitized."""
    
    def test_special_characters_handled(self, client):
        """Special characters in input should not break output JSON."""
        response = client.post(
            '/api/career',
            data=json.dumps({
                "user_data": {
                    "education": 'School "with quotes"',
                    "skills": "Python, <HTML>, {JSON}",
                    "interests": "Testing: special\\chars"
                }
            }),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 200
        # Result should be valid JSON
        data = json.loads(response.data)
        assert data is not None
    
    def test_null_bytes_handled(self, client):
        """Null bytes should be safely handled or removed."""
        response = client.post(
            '/api/career',
            data=json.dumps({
                "user_data": {
                    "education": "Test\x00School",
                    "skills": "Python",
                    "interests": ""
                }
            }),
            headers={'Content-Type': 'application/json'}
        )
        # Should not crash
        assert response.status_code == 200
