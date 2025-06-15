from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # API Settings
    APP_ENV: str
    APP_DEBUG: bool
    APP_STR: str = "/api/v1"
    APP_NAME: str = "{name} API"
    APP_VERSION: str = "v1"

    # POSTGRES
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PORT: int

    # RabbitMQ
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int

    SESSION_TTL_SECOND: int = 30 * 24 * 60 * 60

    # origins
    STAGING_ORIGIN: list = []
    PRODUCTION_ORIGIN: list = []

    # QUEUE NAME
    QUEUE_NAME: str

    # Rate Limiter Settings
    RATE_LIMIT_TIMES: int = 100  # Number of requests allowed
    RATE_LIMIT_SECONDS: int = 60  # Time window in seconds

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis
    REDIS_URL: str
    REDIS_PREFIX: str = "chat_assistant"

    # API Key
    API_KEY: str

    # MongoDB
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_DB: str

    # TODO: should be added to the config after the elasticsearch is implemented
    # # ELASTIC
    # ELASTIC_APM_SERVER_URL: str
    # ELASTICSEARCH_HOST: str
    # ELASTIC_BROKER_URL: str
    # ELASTIC_INDEX_NAME: str

    # # APM
    # APP_APM_NAME: str
    # CELERY_APM_NAME: str

    # Gemini API Key
    GEMINI_API_KEY: str
    GEMINI_BASE_URL: str
    GEMINI_ENDPOINT: str

    @property
    def ORIGIN(self):
        if self.APP_ENV == "PRODUCTION":
            return self.PRODUCTION_ORIGIN
        else:
            return self.STAGING_ORIGIN

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


config = Config()
