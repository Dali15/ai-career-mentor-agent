from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from services import AzureOpenAIService, CareerMentorService, GroqCareerService, MockCareerService, OpenAIService


load_dotenv(dotenv_path=Path(__file__).resolve().with_name(".env"))
logger = logging.getLogger(__name__)


def generate_career_plan(user_data: dict[str, Any]) -> dict[str, Any]:
    service = build_career_mentor_service()
    response = service.generate_career_plan(user_data)
    if isinstance(response, dict) and not response.get("ai_source"):
        response["ai_source"] = _infer_ai_source(service)

    logger.info(f"Career plan generated using provider: {type(service).__name__}")
    return response


def build_career_mentor_service() -> CareerMentorService:
    # Try Groq
    if os.getenv("GROQ_API_KEY"):
        try:
            service = GroqCareerService()
            if service.client is None:
                logger.warning("GROQ_API_KEY set but Groq client initialization failed. Falling back to mock.")
            else:
                logger.info("Using Groq AI provider")
                return service
        except Exception as e:
            logger.warning(f"Groq initialization failed: {e}. Falling back to mock.")
    
    # Try OpenAI
    if os.getenv("OPENAI_API_KEY"):
        try:
            service = OpenAIService()
            if service.client is None:
                logger.warning("OPENAI_API_KEY set but OpenAI client initialization failed. Falling back to mock.")
            else:
                logger.info("Using OpenAI AI provider")
                return service
        except Exception as e:
            logger.warning(f"OpenAI initialization failed: {e}. Falling back to mock.")
    
    # Try Azure
    if _has_azure_credentials():
        try:
            service = AzureOpenAIService()
            logger.info("Using Azure OpenAI provider")
            return service
        except Exception as e:
            logger.warning(f"Azure OpenAI initialization failed: {e}. Falling back to mock.")
    
    logger.info("No API keys configured. Using mock career mentor service.")
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
    return "mock"
