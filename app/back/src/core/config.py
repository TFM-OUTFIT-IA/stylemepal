from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Outfit Engine API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str 
    ALGORITHM: str = "HS256" 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720

    # DB
    DATABASE_URL: str

    # Model Paths
    PROBE_WEIGHTS_PATH: str = "/app/data/weights/fashion_classifier_fashionclip_polyvore.pth"
    LABEL_ENCODER_PATH: str = "/app/data/weights/label_encoder.pkl"
    RGCN_WEIGHTS_PATH: str = "/app/data/weights/rgcn_weights.pth"

    CLIP_MODEL_NAME: str = "patrickjohncyh/fashion-clip"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()