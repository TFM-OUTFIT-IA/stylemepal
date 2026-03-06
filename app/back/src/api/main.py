from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
import logging

from ..db.database import engine, Base
from .auth import auth_router
from .items import items_router
from .outfits import outfits_router
from .agent import agent_router
from ..services.inference import InferenceEngine
from ..services.recommender import OutfitRecommender

logger = logging.getLogger(__name__)

try:
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
except Exception as e:
    logger.exception("FATAL: Could not create 'vector' extension.")
    raise

try:
    Base.metadata.create_all(bind=engine)
except Exception:
    logger.exception("Failed to create DB metadata")

services = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Lifespan startup: loading AI models into memory...")
    try:
        services["inference"] = InferenceEngine()
        services["recommender"] = OutfitRecommender()
        logger.info("Inference engine and recommender loaded successfully")
    except Exception:
        services["inference"] = None
        services["recommender"] = None
        logger.exception("Failed to initialize InferenceEngine or OutfitRecommender; service set to None")

    app.state.services = services
    yield

    try:
        services.clear()
    except Exception:
        logger.exception("Error clearing services on shutdown")

UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Outfit Engine API", lifespan=lifespan, redirect_slashes=False)
app.state.services = services

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(items_router, prefix="/api/v1")
app.include_router(outfits_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")