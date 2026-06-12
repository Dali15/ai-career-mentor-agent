from __future__ import annotations

import json
import os
from typing import Any

from groq import Groq

from .mock_career_service import MockCareerService


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
                                "user_data": user_data,
                                "structured_analysis": profile_analysis,
                                "required_output": {
                                    "ai_source": "groq",
                                    "career_match_score": "integer",
                                    "confidence_score": "integer",
                                    "career_match_explanation": "string",
                                    "analysis_summary": "string",
                                    "career_path": "string",
                                    "recommended_paths": ["string"],
                                    "career_comparison": [
                                        {
                                            "career": "string",
                                            "score": "integer",
                                            "reason": "string",
                                            "strong_hits": ["string"],
                                            "partial_hits": ["string"],
                                        }
                                    ],
                                    "reasoning": ["string"],
                                    "strengths": ["string"],
                                    "missing_skills": ["string"],
                                    "roadmap": {
                                        "month_1": ["string"],
                                        "month_2": ["string"],
                                        "month_3": ["string"],
                                    },
                                    "reasoning_trace": ["string"],
                                    "market_demand": "string",
                                    "job_ready_time": "string",
                                    "learning_resources": [
                                        {
                                            "title": "string",
                                            "type": "string",
                                            "url": "string",
                                        }
                                    ],
                                    "certifications": ["string"],
                                    "final_advice": "string",
                                },
                            }
                        ),
                    },
                ],
            )

            raw_text = self._extract_output_text(response)
            parsed = json.loads(raw_text)
            normalized = self._normalize_response(parsed, fallback_response)
            normalized["ai_source"] = "groq"
            return normalized
        except Exception:
            return fallback_response

    @staticmethod
    def _build_client() -> Any | None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return None
        return Groq(api_key=api_key)

    @staticmethod
    def _extract_output_text(response: Any) -> str:
        choices = getattr(response, "choices", None) or []
        if choices:
            message = getattr(choices[0], "message", None)
            content = getattr(message, "content", None)
            if content:
                return str(content).strip()

        output = getattr(response, "output", None) or []
        parts: list[str] = []
        for item in output:
            content = getattr(item, "content", None) or []
            for part in content:
                text = getattr(part, "text", None)
                if text:
                    parts.append(text)
        return "".join(parts).strip()

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
                "career_match_score": self._safe_int(value.get("career_match_score"), fallback["career_match_score"]),
                "confidence_score": self._safe_int(value.get("confidence_score"), fallback["confidence_score"]),
                "career_match_explanation": str(value.get("career_match_explanation", fallback["career_match_explanation"])).strip() or fallback["career_match_explanation"],
                "analysis_summary": str(value.get("analysis_summary", fallback.get("analysis_summary", ""))).strip() or fallback.get("analysis_summary", ""),
                "career_path": str(value.get("career_path", fallback["career_path"])).strip() or fallback["career_path"],
                "recommended_paths": self._ensure_string_list(value.get("recommended_paths"), fallback.get("recommended_paths", [])),
                "career_comparison": self._ensure_comparison_list(value.get("career_comparison"), fallback["career_comparison"]),
                "reasoning": self._ensure_string_list(value.get("reasoning"), fallback["reasoning"]),
                "strengths": self._ensure_string_list(value.get("strengths"), fallback["strengths"]),
                "missing_skills": self._ensure_string_list(value.get("missing_skills"), fallback["missing_skills"]),
                "roadmap": {
                    "month_1": self._ensure_string_list(roadmap.get("month_1"), fallback["roadmap"]["month_1"]),
                    "month_2": self._ensure_string_list(roadmap.get("month_2"), fallback["roadmap"]["month_2"]),
                    "month_3": self._ensure_string_list(roadmap.get("month_3"), fallback["roadmap"]["month_3"]),
                },
                "reasoning_trace": self._ensure_string_list(value.get("reasoning_trace"), fallback["reasoning_trace"]),
                "market_demand": str(value.get("market_demand", fallback.get("market_demand", ""))).strip() or fallback.get("market_demand", ""),
                "job_ready_time": str(value.get("job_ready_time", fallback.get("job_ready_time", ""))).strip() or fallback.get("job_ready_time", ""),
                "learning_resources": self._ensure_learning_resources(value.get("learning_resources"), fallback["learning_resources"]),
                "certifications": self._ensure_string_list(value.get("certifications"), fallback["certifications"]),
                "final_advice": str(value.get("final_advice", fallback["final_advice"])).strip() or fallback["final_advice"],
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