from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PromptEnvelope:
    system_instructions: str
    application_context: str
    user_message: str


class LLMProvider(Protocol):
    async def generate(self, prompt: PromptEnvelope) -> str: ...


class MockLLMProvider:
    """Deterministic provider. It never executes or follows text as a tool command."""

    async def generate(self, prompt: PromptEnvelope) -> str:
        return f"Mock assistant received: {prompt.user_message}"
