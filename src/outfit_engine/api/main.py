from fastapi import FastAPI, APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from contextlib import asynccontextmanager
from typing import Annotated, List
from PIL import Image
import io
import uuid

from ..core.config import settings
from .schemas import UploadResponse, UploadBatchResponse, GarmentMetadata, RecommendationResponse
from ..services.inference import InferenceEngine
from ..services.recommender import OutfitRecommender
from ..services.storage import StorageService

services = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading AI Models into memory...")
    services["inference"] = InferenceEngine()
    services["recommender"] = OutfitRecommender()
    services["storage"] = StorageService()
    yield
    services.clear()

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)
api_router = APIRouter(prefix=settings.API_V1_STR)

def process_upload_task(item_id: str, image_bytes: bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        metadata = services["inference"].process_image(image)
        services["storage"].save_garment(item_id, metadata)
    except Exception as e:
        print(f"Error processing {item_id}: {e}")

@api_router.post("/upload", response_model=UploadResponse)
async def upload_garment(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    item_id = f"item_{uuid.uuid4().hex[:8]}"
    image_bytes = await file.read()
    
    # For high load, shift to background_tasks.add_task()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    extracted_data = services["inference"].process_image(image)
    
    # Store in DB asynchronously
    services["storage"].save_garment(item_id, extracted_data)
    
    return UploadResponse(
        status="success",
        item_id=item_id,
        metadata=GarmentMetadata(
            category=extracted_data["category"],
            style=extracted_data["style"],
            weather=extracted_data["weather"],
            gender=extracted_data["gender"]
        )
    )

@api_router.post("/upload/batch")
async def upload_garments_batch(background_tasks: BackgroundTasks, files: Annotated[List[UploadFile], File(description="Upload multiple images")]):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
        
    accepted_items = []
    
    for file in files:
        if not file.content_type.startswith("image/"):
            continue 
            
        item_id = f"item_{uuid.uuid4().hex[:8]}"
        image_bytes = await file.read() 
        
        background_tasks.add_task(process_upload_task, item_id, image_bytes)
        accepted_items.append(item_id)
      
    return UploadBatchResponse(
        status= "processing",
        message= f"Accepted {len(accepted_items)} images for extraction.",
        item_ids= accepted_items
    )

@api_router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendation(style: str, weather: str, gender: str):
    closet_items_filtered = services["storage"].get_filtered_garments(style, weather, gender)
    outfit = services["recommender"].generate_outfit(closet_items_filtered, "tops")

    if isinstance(outfit, dict) and "error" in outfit:
        raise HTTPException(status_code=400, detail=outfit["error"])
    
    return RecommendationResponse(
        status="success",
        anchor_item_id=closet_items_filtered[0]["item_id"] if closet_items_filtered else None,
        outfit=outfit
    )

app.include_router(api_router)