from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Outfit Engine API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Model Paths
    PROBE_WEIGHTS_PATH: str = "models/fashion_classifier_fashionclip_polyvore.pth"
    LABEL_ENCODER_PATH: str = "models/label_encoder.pkl"
    RGCN_WEIGHTS_PATH: str = "models/rgcn_weights.pth"

    CLIP_MODEL_NAME: str = "patrickjohncyh/fashion-clip"
    
    class Config:
        case_sensitive = True

settings = Settings()