from collections import defaultdict, deque

from app.config import settings


class ConversationHistory:
    """In-memory per-thread chat history. Swap for Redis/DB for production/multi-instance use."""

    def __init__(self, max_turns: int | None = None) -> None:
        self._max_turns = max_turns or settings.bot_history_max_turns
        self._threads: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=self._max_turns * 2)
        )

    def get(self, thread_id: str) -> list[dict]:
        return list(self._threads[thread_id])

    def add_user_message(self, thread_id: str, text: str) -> None:
        self._threads[thread_id].append({"role": "user", "content": text})

    def add_assistant_message(self, thread_id: str, text: str) -> None:
        self._threads[thread_id].append({"role": "assistant", "content": text})

    def clear(self, thread_id: str) -> None:
        self._threads.pop(thread_id, None)


history_store = ConversationHistory()
