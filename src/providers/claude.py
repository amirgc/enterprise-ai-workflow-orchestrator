from anthropic import Anthropic

from src.config import settings
from src.providers.base import BaseLLMProvider, LLMResponse


class ClaudeProvider(BaseLLMProvider):
    """LLM provider that calls the Anthropic Claude API.

    Inherits from BaseLLMProvider, so it MUST implement generate().
    Think of it like implementing an interface in C#.
    """

    def __init__(self):
        """Create the Anthropic client using the API key from settings."""
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model

    def generate(self, prompt: str, system_prompt: str = "") -> LLMResponse:
        """Send a prompt to Claude and return a standardized LLMResponse.

        The Anthropic SDK uses 'messages' format:
        - system prompt goes in the 'system' parameter (shapes behavior)
        - user prompt goes in the 'messages' list (the actual request)
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        return LLMResponse(
            content=message.content[0].text,
            model=message.model,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )
