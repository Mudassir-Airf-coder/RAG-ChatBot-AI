from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "rag_chatbot"
    sqlite_path: str = "./data/chatbot.db"
    upload_dir: str = "./uploads"
    opencode_zen_base_url: str = ""
    log_level: str = "INFO"


settings = Settings()
