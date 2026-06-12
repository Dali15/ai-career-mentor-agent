from __future__ import annotations

from .mock_career_service import MockCareerService


class FoundryIQService(MockCareerService):
    """Placeholder for Microsoft Foundry IQ integration."""

    def __init__(self) -> None:
        pass

    def _build_response(self, user_data: dict[str, Any], profile_analysis: dict[str, Any]) -> dict[str, Any]:
        response = super()._build_response(user_data, profile_analysis)
        response["ai_source"] = "foundry_placeholder"
        return response
