from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "rag_chatbot"
    sqlite_path: str = "./data/chatbot.db"
    upload_dir: str = "./uploads"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    opencode_zen_base_url: str = "https://opencode.ai/zen/v1"
    max_upload_mb: int = 2048
    max_chunks_per_doc: int = 2000
    chunk_size: int = 800
    chunk_overlap: int = 100
    retrieval_top_k: int = 10
    max_context_chunks: int = 6
    max_tokens_concise: int = 400
    max_tokens_verbose: int = 1500
    default_temperature: float = 0.2
    log_level: str = "INFO"


settings = Settings()
