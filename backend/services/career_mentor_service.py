from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CareerMentorService(ABC):
    def generate_career_plan(self, user_data: dict[str, Any]) -> dict[str, Any]:
        normalized_user_data = self._normalize_user_data(user_data)
        profile_analysis = self.analyze_profile(normalized_user_data)
        return self._build_response(normalized_user_data, profile_analysis)

    @abstractmethod
    def analyze_profile(self, user_data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def _build_response(self, user_data: dict[str, Any], profile_analysis: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @staticmethod
    def _normalize_user_data(user_data: dict[str, Any]) -> dict[str, Any]:
        selected_careers = user_data.get("selected_careers", [])
        if isinstance(selected_careers, list):
            normalized_selected_careers = [str(item).strip() for item in selected_careers if str(item).strip()]
        else:
            normalized_selected_careers = []

        return {
            "education": str(user_data.get("education", "")).strip(),
            "skills": str(user_data.get("skills", "")).strip(),
            "interests": str(user_data.get("interests", "")).strip(),
            "selected_careers": normalized_selected_careers,
        }
