from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider.

    No matter which provider we use, the rest of the app gets the same shape of data.
    """
    content: str
    model: str
    input_tokens: int
    output_tokens: int


class BaseLLMProvider(ABC):
    """Contract that every LLM provider must follow.

    ABC = Abstract Base Class. You can't create an instance of this directly.
    Subclasses MUST implement the generate() method or Python raises an error.
    """

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> LLMResponse:
        """Send a prompt to the LLM and get a standardized response.

        Args:
            prompt: The user's message / input text.
            system_prompt: Optional instructions that shape the LLM's behavior.

        Returns:
            LLMResponse with the text, model name, and token counts.
        """
        ...
