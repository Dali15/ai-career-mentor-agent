from __future__ import annotations

from typing import Any

from .mock_career_service import MockCareerService


class AzureOpenAIService(MockCareerService):
    """Placeholder Azure OpenAI service that preserves the same contract as the mock service."""

    def __init__(self, client: Any | None = None, deployment: str | None = None) -> None:
        self.client = client
        self.deployment = deployment

    def _build_response(self, user_data: dict[str, Any], profile_analysis: dict[str, Any]) -> dict[str, Any]:
        response = super()._build_response(user_data, profile_analysis)
        response["ai_source"] = "azure"
        return response
