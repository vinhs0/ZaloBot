from abc import ABC, abstractmethod

from app.config import settings


class LLMProvider(ABC):
    @abstractmethod
    async def reply(self, system_prompt: str, history: list[dict], user_message: str) -> str:
        """Generate a reply given conversation history and the latest user message."""


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def reply(self, system_prompt: str, history: list[dict], user_message: str) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )
        return response.choices[0].message.content or ""


class AnthropicProvider(LLMProvider):
    def __init__(self) -> None:
        from anthropic import AsyncAnthropic

        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model

    async def reply(self, system_prompt: str, history: list[dict], user_message: str) -> str:
        messages = list(history)
        messages.append({"role": "user", "content": user_message})

        response = await self._client.messages.create(
            model=self._model,
            system=system_prompt,
            messages=messages,
            max_tokens=1024,
        )
        return "".join(block.text for block in response.content if block.type == "text")


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "anthropic":
        return AnthropicProvider()
    return OpenAIProvider()
