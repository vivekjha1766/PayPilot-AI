"""AI Service interface and implementations."""
from app.services.ai.base import AIService
from app.services.ai.mock import MockAIService

__all__ = ["AIService", "MockAIService"]
