from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional, Annotated

class ItemResponse(BaseModel):
    id: str
    user_id: int
    name: Optional[str] = None
    clean: bool
    image_path: str

    category: str
    style: str
    weather: str
    gender: str

    model_config = ConfigDict(from_attributes=True)

class ItemUpdate(BaseModel):
    nombre: Optional[str] = None
    limpio: Optional[bool] = None

class ItemUpdateResponse(BaseModel):
    message: str
    item: ItemResponse

class GenericMessageResponse(BaseModel):
    message: str

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
    item_id: Optional[str] = None      
    category: str
    compatibility_score: float
    match_quality: str                 
    image_path: Optional[str] = None

class RecommendationResponse(BaseModel):
    status: str
    anchor_item_id: str
    anchor_category: str
    anchor_image_path: Optional[str] = None
    outfit: List[RecommendationItem]

class UserCreate(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_\-]+$")]
    password: Annotated[str, Field(min_length=8, max_length=72)]

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        # simple complexity check: must contain letters and digits
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one letter and one digit")
        return v

    @field_validator("username")
    @classmethod
    def normalize_username(cls, v: str) -> str:
        return v.strip()

class ItemsConfirm(BaseModel):
    ids: List[int]

class OutfitSlotSnapshot(BaseModel):
    slot_id: str
    item_id: Optional[str] = None
    category: str
    image_path: Optional[str] = None
    compatibility_score: float
    match_quality: str

class OutfitSaveRequest(BaseModel):
    style: str
    weather: str
    gender: str
    items_snapshot: List[OutfitSlotSnapshot]
    item_ids_to_dirty: List[str]  #\

class OutfitSaveResponse(BaseModel):
    id: int
    style: str
    weather: str
    gender: str
    items_snapshot: List[dict]
    worn_at: str

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str