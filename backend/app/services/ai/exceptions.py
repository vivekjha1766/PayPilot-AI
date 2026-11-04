from typing import Optional


class AIProviderError(Exception):
    """Base exception for AI provider operations."""
    def __init__(self, message: str, sanitized_message: Optional[str] = None, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.sanitized_message = sanitized_message or message
        self.status_code = status_code


class AIUnconfiguredError(AIProviderError):
    """Raised when live AI generation is requested but no API key is configured."""
    def __init__(self, message: str = "Gemini AI provider is not configured."):
        super().__init__(message, status_code=503)


class AITimeoutError(AIProviderError):
    """Raised when AI provider generation times out."""
    def __init__(self, message: str = "AI purchasing assistant timed out while generating recommendations. Please try again."):
        super().__init__(message, status_code=504)


class AIModelNotFoundError(AIProviderError):
    """Raised when the specified Gemini model is not found or unsupported."""
    def __init__(self, message: str = "Configured AI model was not found upstream or is unavailable."):
        super().__init__(message, status_code=502)


class AIPermissionError(AIProviderError):
    """Raised when authentication or permissions fail on the upstream AI provider."""
    def __init__(self, message: str = "AI provider authentication or permission failed."):
        super().__init__(message, status_code=502)


class AIQuotaExceededError(AIProviderError):
    """Raised when rate limits or quotas are exceeded."""
    def __init__(self, message: str = "AI provider rate limit or quota exceeded. Please try again later."):
        super().__init__(message, status_code=429)


class AIMalformedOutputError(AIProviderError):
    """Raised when the model output cannot be parsed into a valid purchasing plan."""
    def __init__(self, message: str = "AI model returned malformed or unparseable output."):
        super().__init__(message, status_code=502)


class AIProviderUnavailableError(AIProviderError):
    """Raised when upstream Gemini API reports 503 / high demand or temporary outage."""
    def __init__(self, message: str = "Gemini AI service is temporarily experiencing high demand upstream. Please retry or use Test Mode."):
        super().__init__(message, status_code=503)
