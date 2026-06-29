from openai import OpenAI

from src.config import settings
from src.providers.base import BaseLLMProvider, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """LLM provider that calls the OpenAI GPT API."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def generate(self, prompt: str, system_prompt: str = "") -> LLMResponse:
        """Send a prompt to GPT and return a standardized LLMResponse.

        OpenAI's API differs from Anthropic's:
        - System prompt goes as a message with role "system" (not a separate param)
        - Response text is at choices[0].message.content (not content[0].text)
        - Token counts are under usage.prompt_tokens (not usage.input_tokens)
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1024,
            messages=messages,
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
        )
