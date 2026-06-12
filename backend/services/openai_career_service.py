from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from .mock_career_service import MockCareerService


class OpenAIService(MockCareerService):
    """OpenAI-backed career mentor service that falls back to the mock contract on failure."""

    def __init__(self, client: Any | None = None, model: str | None = None) -> None:
        self.client = client or self._build_client()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def _build_response(self, user_data: dict[str, Any], profile_analysis: dict[str, Any]) -> dict[str, Any]:
        fallback_response = super()._build_response(user_data, profile_analysis)
        if self.client is None:
            return fallback_response

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a production career mentor agent. Return JSON only with explanation fields. "
                            "Do not change the career path, scores, comparison ranking, or market timing because those are already computed. "
                            "Explain the structured analysis in a clear, helpful, and deterministic way."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "user_data": user_data,
                                "structured_analysis": profile_analysis,
                                "locked_fields": {
                                    "career_path": profile_analysis.get("career_path"),
                                    "career_match_score": profile_analysis.get("career_match_score"),
                                    "confidence_score": profile_analysis.get("confidence_score"),
                                    "career_comparison": profile_analysis.get("career_comparison"),
                                    "recommended_paths": profile_analysis.get("recommended_paths"),
                                    "market_demand": profile_analysis.get("market_demand"),
                                    "job_ready_time": profile_analysis.get("job_ready_time"),
                                },
                                "required_output": {
                                    "analysis_summary": "string",
                                    "career_match_explanation": "string",
                                    "reasoning": ["string"],
                                    "strengths": ["string"],
                                    "missing_skills": ["string"],
                                    "roadmap": {"month_1": ["string"], "month_2": ["string"], "month_3": ["string"]},
                                    "reasoning_trace": ["string"],
                                    "final_advice": "string",
                                    "learning_resources": [{"title": "string", "type": "string", "url": "string"}],
                                    "certifications": ["string"],
                                },
                            }
                        ),
                    },
                ],
            )

            raw_text = self._extract_output_text(response)
            parsed = json.loads(raw_text)
            normalized = self._normalize_response(parsed, fallback_response)
            normalized["ai_source"] = "openai"
            return normalized
        except Exception:
            return fallback_response

    @staticmethod
    def _build_client() -> Any | None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        return OpenAI(api_key=api_key)

    @staticmethod
    def _extract_output_text(response: Any) -> str:
        message = None
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
    def _ensure_comparison_list(value: Any, fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if isinstance(value, list):
            cleaned: list[dict[str, Any]] = []
            for item in value:
                if isinstance(item, dict):
                    career = str(item.get("career", "")).strip()
                    reason = str(item.get("reason", "")).strip()
                    try:
                        score = int(item.get("score", 0))
                    except (TypeError, ValueError):
                        score = 0
                    if career:
                        cleaned.append({"career": career, "score": max(0, min(100, score)), "reason": reason or fallback[0]["reason"] if fallback else ""})
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
                "strengths": self._ensure_string_list(value.get("strengths"), fallback["strengths"]),
                "missing_skills": self._ensure_string_list(value.get("missing_skills"), fallback["missing_skills"]),
                "roadmap": {
                    "month_1": self._ensure_string_list(roadmap.get("month_1"), fallback["roadmap"]["month_1"]),
                    "month_2": self._ensure_string_list(roadmap.get("month_2"), fallback["roadmap"]["month_2"]),
                    "month_3": self._ensure_string_list(roadmap.get("month_3"), fallback["roadmap"]["month_3"]),
                },
                "analysis_summary": str(value.get("analysis_summary", fallback.get("analysis_summary", ""))).strip() or fallback.get("analysis_summary", ""),
                "career_match_explanation": str(value.get("career_match_explanation", fallback.get("career_match_explanation", ""))).strip() or fallback.get("career_match_explanation", ""),
                "reasoning_trace": self._ensure_string_list(value.get("reasoning_trace"), fallback["reasoning_trace"]),
                "final_advice": str(value.get("final_advice", fallback["final_advice"])).strip() or fallback["final_advice"],
            }
        )

        return normalized
