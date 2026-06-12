from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from services import AzureOpenAIService, CareerMentorService, FoundryIQService, GroqCareerService, MockCareerService, OpenAIService


load_dotenv(dotenv_path=Path(__file__).resolve().with_name(".env"))


def generate_career_plan(user_data: dict[str, Any]) -> dict[str, Any]:
    service = build_career_mentor_service()
    response = service.generate_career_plan(user_data)
    if isinstance(response, dict) and not response.get("ai_source"):
        response["ai_source"] = _infer_ai_source(service)

    print("🔥 ACTIVE PROVIDER:", type(service).__name__)
    return response


def build_career_mentor_service() -> CareerMentorService:
    if os.getenv("GROQ_API_KEY"):
        return GroqCareerService()
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIService()
    if _has_azure_credentials():
        return AzureOpenAIService()
    return MockCareerService()


def _has_azure_credentials() -> bool:
    return any(
        os.getenv(name)
        for name in (
            "AZURE_API_KEY",
        )
    )


def _infer_ai_source(service: CareerMentorService) -> str:
    if isinstance(service, GroqCareerService):
        return "groq"
    if isinstance(service, OpenAIService):
        return "openai"
    if isinstance(service, AzureOpenAIService):
        return "azure"
    if isinstance(service, FoundryIQService):
        return "foundry_placeholder"
    return "mock"
