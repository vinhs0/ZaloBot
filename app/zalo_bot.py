import logging

from zlapi.Async import ZaloAPI
from zlapi.models import Message, ThreadType

from app.config import settings
from app.history import history_store
from app.llm import get_llm_provider

logger = logging.getLogger(__name__)


class ChatBot(ZaloAPI):
    """Zalo client that forwards incoming messages to the configured LLM provider."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._llm = get_llm_provider()

    async def onMessage(
        self, mid, author_id, message, message_object: Message, thread_id, thread_type: ThreadType
    ) -> None:
        if not message:
            return

        logger.info("Received message from %s in thread %s: %s", author_id, thread_id, message)

        history = history_store.get(thread_id)
        try:
            reply_text = await self._llm.reply(settings.bot_system_prompt, history, message)
        except Exception:
            logger.exception("LLM provider failed to generate a reply")
            reply_text = "Xin lỗi, hiện tại mình không thể trả lời. Vui lòng thử lại sau."

        history_store.add_user_message(thread_id, message)
        history_store.add_assistant_message(thread_id, reply_text)

        await self.send(Message(text=reply_text), thread_id, thread_type)

    async def onListening(self) -> None:
        logger.info("Zalo bot is now listening for messages")


def build_bot() -> ChatBot:
    return ChatBot(
        settings.zalo_phone,
        settings.zalo_password,
        imei=settings.zalo_imei,
        session_cookies=settings.zalo_cookies,
    )
