from __future__ import annotations

import json
import logging
import os
from typing import Any

from groq import Groq

from .mock_career_service import MockCareerService

logger = logging.getLogger(__name__)


class GroqCareerService(MockCareerService):
    """Groq-backed career mentor service that preserves the existing contract."""

    def __init__(self, client: Any | None = None, model: str | None = None) -> None:
        self.client = client or self._build_client()
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

    def _build_response(self, user_data: dict[str, Any], profile_analysis: dict[str, Any]) -> dict[str, Any]:
        fallback_response = super()._build_response(user_data, profile_analysis)
        if self.client is None:
            return fallback_response

        try:
            # Sanitize user data for LLM prompt injection prevention
            sanitized_user_data = self._sanitize_for_llm(user_data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior career strategy analyst for an AI career mentor. "
                            "Produce practical, high-confidence guidance that is specific, structured, and realistic. "
                            "Return valid JSON only. Do not include markdown, commentary, code fences, or extra keys. "
                            "The JSON must represent the exact career mentor contract and must be directly usable by a frontend. "
                            "Keep the selected career path aligned with the supplied analysis and avoid contradicting the scored evidence. "
                            "Write concise but useful rationale, a focused 3-month roadmap, and actionable next steps."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "user_data": sanitized_user_data,
                                "structured_analysis": profile_analysis,
                                "required_output": {
                                    "ai_source": "groq",
                                    "top_career": "string",
                                    "career_scores": [
                                        {
                                            "career": "string",
                                            "score": "integer",
                                            "top_positive_factors": ["string"],
                                            "supporting_factors": ["string"],
                                            "missing_critical_skills": ["string"],
                                            "reasoning_summary": "string"
                                        }
                                    ],
                                    "reasoning": ["string"],
                                    "strengths": ["string"],
                                    "gaps": ["string"],
                                    "roadmap": {
                                        "month_1": ["string"],
                                        "month_2": ["string"],
                                        "month_3": ["string"],
                                    },
                                    "certifications": ["string"],
                                    "learning_resources": [
                                        {
                                            "title": "string",
                                            "type": "string",
                                            "url": "string",
                                        }
                                    ]
                                },
                            }
                        ),
                    },
                ],
            )

            raw_text = self._extract_output_text(response)
            if not raw_text:
                logger.warning("Groq returned empty response text")
                return fallback_response
            
            try:
                parsed = json.loads(raw_text)
            except json.JSONDecodeError as e:
                logger.warning(f"Groq returned invalid JSON: {e}. Falling back to mock response.")
                return fallback_response
            
            normalized = self._normalize_response(parsed, fallback_response)
            normalized["ai_source"] = "groq"
            return normalized
        except Exception as e:
            logger.warning(f"Groq service error: {e}. Falling back to mock response.")
            return fallback_response

    @staticmethod
    def _sanitize_for_llm(user_data: dict[str, Any]) -> dict[str, Any]:
        """Sanitize user data to prevent prompt injection."""
        sanitized = {}
        for key, value in user_data.items():
            if isinstance(value, str):
                # Remove null bytes and control characters, limit length
                clean = ''.join(c for c in value if ord(c) >= 32 or c in '\n\t')[:5000]
                sanitized[key] = clean
            elif isinstance(value, list):
                sanitized[key] = [str(item)[:1000] for item in value if item]
            else:
                sanitized[key] = value
        return sanitized

    @staticmethod
    def _build_client() -> Any | None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return None
        return Groq(api_key=api_key)

    @staticmethod
    def _extract_output_text(response: Any) -> str:
        """Extract text from Groq response with validation."""
        try:
            choices = getattr(response, "choices", None) or []
            if not choices:
                logger.debug("No choices in Groq response")
                return ""
            
            message = getattr(choices[0], "message", None)
            if not message:
                logger.debug("No message in first choice")
                return ""
            
            content = getattr(message, "content", None)
            if not content:
                logger.debug("No content in message")
                return ""
            
            return str(content).strip()
        except (AttributeError, IndexError, ValueError) as e:
            logger.warning(f"Error extracting response text: {e}")
            return ""

    @staticmethod
    def _ensure_string_list(value: Any, fallback: list[str]) -> list[str]:
        if isinstance(value, list):
            cleaned = [str(item).strip() for item in value if str(item).strip()]
            if cleaned:
                return cleaned
        return fallback

    @staticmethod
    def _ensure_learning_resources(value: Any, fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if isinstance(value, list):
            cleaned: list[dict[str, Any]] = []
            for item in value:
                if not isinstance(item, dict):
                    continue
                title = str(item.get("title", "")).strip()
                resource_type = str(item.get("type", "")).strip()
                url = str(item.get("url", "")).strip()
                if title and resource_type and url:
                    cleaned.append({"title": title, "type": resource_type, "url": url})
            if cleaned:
                return cleaned
        return fallback

    @staticmethod
    def _ensure_comparison_list(value: Any, fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if isinstance(value, list):
            cleaned: list[dict[str, Any]] = []
            for item in value:
                if not isinstance(item, dict):
                    continue
                career = str(item.get("career", "")).strip()
                reason = str(item.get("reason", "")).strip()
                strong_hits = item.get("strong_hits", [])
                partial_hits = item.get("partial_hits", [])
                try:
                    score = int(item.get("score", 0))
                except (TypeError, ValueError):
                    score = 0
                if career:
                    cleaned.append(
                        {
                            "career": career,
                            "score": max(0, min(100, score)),
                            "reason": reason or (fallback[0]["reason"] if fallback else ""),
                            "strong_hits": strong_hits if isinstance(strong_hits, list) else [],
                            "partial_hits": partial_hits if isinstance(partial_hits, list) else [],
                        }
                    )
            if cleaned:
                return cleaned
        return fallback

    def _normalize_response(self, value: Any, fallback: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(value, dict):
            return fallback

        roadmap = value.get("roadmap")
        if not isinstance(roadmap, dict):
            roadmap = fallback["roadmap"]

        normalized = dict(fallback)
        normalized.update(
            {
                "reasoning": self._ensure_string_list(value.get("reasoning"), fallback["reasoning"]),
                "strengths": self._ensure_string_list(value.get("strengths"), fallback.get("strengths", [])),
                "gaps": self._ensure_string_list(value.get("gaps", value.get("missing_skills")), fallback.get("gaps", [])),
                "roadmap": {
                    "month_1": self._ensure_string_list(roadmap.get("month_1"), fallback["roadmap"]["month_1"]),
                    "month_2": self._ensure_string_list(roadmap.get("month_2"), fallback["roadmap"]["month_2"]),
                    "month_3": self._ensure_string_list(roadmap.get("month_3"), fallback["roadmap"]["month_3"]),
                },
                "certifications": self._ensure_string_list(value.get("certifications"), fallback["certifications"]),
                "learning_resources": self._ensure_learning_resources(value.get("learning_resources"), fallback["learning_resources"]),
                "final_explanation": str(value.get("final_explanation", fallback.get("final_explanation", ""))).strip() or fallback.get("final_explanation", ""),
                "career_specific_explanations": value.get("career_specific_explanations", fallback.get("career_specific_explanations", {}))
            }
        )

        return normalized

    @staticmethod
    def _safe_int(value: Any, fallback: int) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return fallback
        return max(0, min(100, parsed))