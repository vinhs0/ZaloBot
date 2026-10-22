import json

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Zalo
    zalo_phone: str = ""
    zalo_password: str = ""
    zalo_imei: str = ""
    zalo_cookies_json: str = "{}"

    # LLM
    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-latest"

    # Bot behavior
    bot_system_prompt: str = (
        "You are a helpful Vietnamese-speaking assistant chatting on Zalo. "
        "Keep replies concise and friendly."
    )
    bot_history_max_turns: int = 10

    # App
    log_level: str = "INFO"

    @property
    def zalo_cookies(self) -> dict:
        try:
            return json.loads(self.zalo_cookies_json)
        except (json.JSONDecodeError, TypeError):
            return {}


settings = Settings()
