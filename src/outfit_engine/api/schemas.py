from pydantic import BaseModel
from typing import List, Optional

class GarmentMetadata(BaseModel):
    category: str
    style: str
    weather: str
    gender: str

class UploadResponse(BaseModel):
    status: str
    item_id: str
    metadata: GarmentMetadata

class UploadBatchResponse(BaseModel):
    status: str
    message: str
    item_ids: List[str]

class RecommendationItem(BaseModel):
    item_id: str
    category: str
    compatibility_score: float

class RecommendationResponse(BaseModel):
    status: str
    anchor_item_id: str
    outfit: List[RecommendationItem]