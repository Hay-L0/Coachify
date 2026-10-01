import os

from interview.llm import (
    GeminiProvider,
    LLMProvider,
    LLMProviderError,
)


class MockProvider(LLMProvider):
    """
    Deterministic fallback provider used for development
    and provider-failure testing.

    This provider is intentionally independent of Gemini
    and follows the same response contract as the real
    LLM provider.
    """

    def __init__(self):
        self.provider_name = "mock"

    def generate_response(
        self,
        state,
        retrieved_context=None,
    ):
        question_number = (
            state.questions_asked + 1
        )

        if question_number == 1:
            response = (
                "Tell me about a technical project "
                "you have worked on recently. What was "
                "your role and what challenges did you face?"
            )

        elif question_number == 2:
            response = (
                "Describe a difficult technical problem "
                "you encountered and how you approached "
                "solving it."
            )

        else:
            response = (
                "Can you explain one technical decision "
                "you made in that project and why you "
                "chose that approach?"
            )

        return {
            "response": response,
            "action": "NEXT_TOPIC",
            "currentTopic": "Technical Skills",
            "topicsCovered": [
                "Technical Skills"
            ],
            "strengths": [],
            "weaknesses": [],
            "followUpNeeded": False,
        }


class ProviderRouter:
    """
    Routes interview generation through the configured
    primary provider and optionally falls back to another
    provider when the primary provider fails.
    """

    def __init__(self):
        self.primary_provider = os.getenv(
            "PRIMARY_LLM_PROVIDER",
            "gemini",
        ).strip().lower()

        self.fallback_enabled = (
            os.getenv(
                "LLM_FALLBACK_ENABLED",
                "true",
            )
            .strip()
            .lower()
            == "true"
        )

        self._providers = {}

    def generate_response(
        self,
        state,
        retrieved_context=None,
    ):
        provider = self._get_provider(
            self.primary_provider
        )

        try:
            return provider.generate_response(
                state,
                retrieved_context=retrieved_context,
            )

        except LLMProviderError as error:
            if not self._should_fallback(error):
                raise

            fallback = self._get_fallback_provider(
                error.provider
            )

            if fallback is None:
                raise

            return fallback.generate_response(
                state,
                retrieved_context=retrieved_context,
            )

    def _get_provider(self, provider_name):
        if provider_name in self._providers:
            return self._providers[provider_name]

        if provider_name == "gemini":
            provider = GeminiProvider()

        elif provider_name == "mock":
            provider = MockProvider()

        else:
            raise RuntimeError(
                f"Unknown LLM provider: {provider_name}"
            )

        self._providers[provider_name] = provider

        return provider

    def _should_fallback(
        self,
        error: LLMProviderError,
    ):
        if not self.fallback_enabled:
            return False

        return error.error_type in {
            "quota_exceeded",
            "temporary_failure",
        }

    def _get_fallback_provider(
        self,
        failed_provider,
    ):
        if failed_provider == "gemini":
            return self._get_provider("mock")

        return None