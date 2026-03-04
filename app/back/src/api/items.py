import io, os
import uuid
import aiofiles
import random
import logging
from typing import Annotated, List, Dict, Any
from PIL import Image, UnidentifiedImageError
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends, Request, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..db.database import get_db, SessionLocal
from ..db.models import ItemDB, UserDB
from .schemas import (
    ItemsConfirm,
    UploadResponse,
    UploadBatchResponse,
    GarmentMetadata,
    RecommendationResponse,
    ItemResponse,
    ItemUpdate,
    ItemUpdateResponse,
    GenericMessageResponse,
)
from ..core.security import get_current_user

logger = logging.getLogger(__name__)

items_router = APIRouter(prefix="/items", tags=["Wardrobe Integration"])


def process_upload_task(item_id: str, image_bytes: bytes, services: Dict[str, Any]) -> None:
    """Background task requires its own dedicated database session."""
    db = SessionLocal()
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        if not services or "inference" not in services or services.get("inference") is None:
            logger.error("Inference service not available for background task")
            return
        extracted_data = services["inference"].process_image(image)

        item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
        if item:
            item.category = extracted_data["category"]
            item.style = extracted_data["style"]
            item.weather = extracted_data["weather"]
            item.gender = extracted_data["gender"]
            item.compat_embedding = extracted_data.get("compat_embedding")
            try:
                db.commit()
            except SQLAlchemyError:
                db.rollback()
                logger.exception("DB commit failed in background task for %s", item_id)
    except UnidentifiedImageError as img_err:
        logger.exception("Invalid image for %s: %s", item_id, img_err)
    except IOError as io_err:
        logger.exception("I/O error processing %s: %s", item_id, io_err)
    except Exception:
        logger.exception("Unexpected error processing %s", item_id)
    finally:
        db.close()


@items_router.post("", response_model=UploadResponse)
async def upload_garment(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    nombre: str = Form("Nombre por defecto"),
    current_user: UserDB = Depends(get_current_user),
) -> UploadResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    item_id = f"item_{uuid.uuid4().hex[:8]}"
    try:
        image_bytes = await file.read()
    except IOError as io_err:
        logger.exception("Failed to read uploaded file: %s", io_err)
        raise HTTPException(status_code=400, detail="Failed to read uploaded file")

    UPLOAD_DIR = "/app/uploads"
    filename = f"{current_user.id}_{file.filename}"
    file_location = f"{UPLOAD_DIR}/{filename}"
    try:
        async with aiofiles.open(file_location, "wb") as f:
            await f.write(image_bytes)
    except IOError as io_err:
        logger.exception("Failed to save uploaded file: %s", io_err)
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except UnidentifiedImageError as img_err:
        logger.exception("Uploaded file is not a valid image: %s", img_err)
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")

    services = getattr(request.app.state, "services", None)
    if not services or services.get("inference") is None:
        logger.error("Inference service unavailable on upload")
        raise HTTPException(status_code=503, detail="Inference service not available")

    try:
        extracted_data = services["inference"].process_image(image)
    except Exception:
        logger.exception("Inference processing failed for upload %s", item_id)
        raise HTTPException(status_code=503, detail="Failed to process image for features")

    new_item = ItemDB(
        id=item_id,
        image_path=f"/uploads/{filename}",
        name=nombre,
        user_id=current_user.id,
        category=extracted_data.get("category"),
        style=extracted_data.get("style"),
        weather=extracted_data.get("weather"),
        gender=extracted_data.get("gender"),
        compat_embedding=extracted_data.get("compat_embedding"),
    )
    db.add(new_item)
    try:
        db.commit()
    except SQLAlchemyError as db_err:
        db.rollback()
        logger.exception("DB commit failed for new item %s: %s", item_id, db_err)
        raise HTTPException(status_code=500, detail="Failed to save item to database")

    return UploadResponse(
        status="success",
        item_id=item_id,
        metadata=GarmentMetadata(**extracted_data)
    )


@items_router.post("/batch", response_model=UploadBatchResponse)
async def upload_garments_batch(
    request: Request,
    background_tasks: BackgroundTasks,
    files: Annotated[List[UploadFile], File(description="Upload multiple images")],
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UploadBatchResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    accepted_items = []
    rejected_files = []

    for i, file in enumerate(files):
        if not file.content_type or not file.content_type.startswith("image/"):
            rejected_files.append(file.filename)
            continue

        item_id = f"item_{uuid.uuid4().hex[:8]}"

        try:
            image_bytes = await file.read()
        except IOError:
            logger.exception("Failed to read file %s in batch", file.filename)
            rejected_files.append(file.filename)
            continue

        UPLOAD_DIR = "/app/uploads"
        filename = f"{current_user.id}_{file.filename}"
        file_location = f"{UPLOAD_DIR}/{filename}"

        try:
            async with aiofiles.open(file_location, "wb") as f:
                await f.write(image_bytes)
        except IOError:
            logger.exception("Failed to save file %s in batch", file.filename)
            rejected_files.append(file.filename)
            continue

        item_name = file.filename.rsplit(".", 1)[0] if file.filename else f"Item {i + 1}"

        new_item = ItemDB(
            id=item_id,
            image_path=f"/uploads/{filename}",
            name=item_name,
            user_id=current_user.id,
        )
        db.add(new_item)
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            logger.exception("Failed to commit item %s in batch", item_id)
            rejected_files.append(file.filename)
            continue

        background_tasks.add_task(
            process_upload_task, item_id, image_bytes,
            getattr(request.app.state, "services", None)
        )
        accepted_items.append(item_id)

    msg = f"Accepted {len(accepted_items)} images for processing."
    if rejected_files:
        msg += f" Rejected {len(rejected_files)}: {', '.join(rejected_files)}"

    return UploadBatchResponse(
        status="processing",
        message=msg,
        item_ids=accepted_items
    )

@items_router.get("", response_model=List[ItemResponse])
def get_items(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ItemResponse]:
    return db.query(ItemDB).filter(ItemDB.user_id == current_user.id).all()

@items_router.put("/bulk/clean-all", response_model=GenericMessageResponse)
def clean_all_items(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> GenericMessageResponse:
    db.query(ItemDB).filter(ItemDB.user_id == current_user.id).update({ItemDB.clean: True})
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to mark all items clean for user %s", current_user.id)
        raise HTTPException(status_code=500, detail="Failed to update items")
    return GenericMessageResponse(message="Toda la ropa está limpia")


@items_router.put("/bulk/dirty", response_model=GenericMessageResponse)
def mark_items_dirty(
    data: ItemsConfirm,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> GenericMessageResponse:
    db.query(ItemDB).filter(
        ItemDB.id.in_(data.ids),
        ItemDB.user_id == current_user.id
    ).update({ItemDB.clean: False}, synchronize_session=False)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to mark items dirty for user %s", current_user.id)
        raise HTTPException(status_code=500, detail="Failed to update items")
    return GenericMessageResponse(message="Items marcados como sucios")

@items_router.get("/recommend", response_model=RecommendationResponse)
async def get_recommendation(
    style: str,
    weather: str,
    gender: str,
    request: Request,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> RecommendationResponse:

    WEATHER_FB = {
        "Summer":       ["Transitional", "Winter"],
        "Winter":       ["Transitional", "Summer"],
        "Transitional": ["Summer", "Winter"],
    }
    STYLE_FB = {
        "Casual":      ["Minimalist", "Streetwear", "Sporty"],
        "Formal":      ["Elegant", "Minimalist"],
        "Streetwear":  ["Casual", "Sporty"],
        "Bohemian":    ["Vintage", "Casual"],
        "Sporty":      ["Casual", "Streetwear"],
        "Elegant":     ["Formal", "Minimalist"],
        "Vintage":     ["Bohemian", "Casual"],
        "Minimalist":  ["Casual", "Elegant", "Formal"],
    }
    GENDER_FB = ["Unisex"] if gender != "Unisex" else []

    all_styles   = [style]   + STYLE_FB.get(style, [])
    all_weathers = [weather] + WEATHER_FB.get(weather, [])
    all_genders  = [gender]  + GENDER_FB

    # Same priority order as the recommender: style first, weather second, gender last
    anchors = []
    for s in all_styles:
        for w in all_weathers:
            for g in all_genders:
                anchors = db.query(ItemDB).filter(
                    ItemDB.user_id == current_user.id,
                    ItemDB.compat_embedding.is_not(None),
                    ItemDB.clean == True,
                    ItemDB.style == s,
                    ItemDB.weather == w,
                    ItemDB.gender == g,
                ).all()
                if anchors:
                    break
            if anchors:
                break
        if anchors:
            break

    if not anchors:
        raise HTTPException(
            status_code=404,
            detail=f"No clean items found matching style '{style}' and gender '{gender}'. Try different filters or add more items."
        )

    anchor = random.choice(anchors)

    recommender = getattr(request.app.state, "services", {}).get("recommender")
    if recommender is None:
        logger.error("Recommender service unavailable")
        raise HTTPException(status_code=503, detail="Recommender service not available")

    try:
        outfit = recommender.generate_outfit(
            db=db,
            anchor_item=anchor,
            filters={"style": style, "weather": weather, "gender": gender},
            user_id=current_user.id,
        )
    except Exception:
        logger.exception("Recommender failed")
        raise HTTPException(status_code=500, detail="Failed to generate outfit")

    return RecommendationResponse(
        status="success",
        anchor_item_id=anchor.id,
        anchor_category=anchor.category,
        anchor_image_path=anchor.image_path,
        outfit=outfit
    )

@items_router.put("/{item_id}", response_model=ItemUpdateResponse)
def update_item(
    item_id: str,
    data: ItemUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ItemUpdateResponse:
    item = db.query(ItemDB).filter(
        ItemDB.id == item_id,
        ItemDB.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    if data.nombre is not None:
        item.name = data.nombre
    if data.limpio is not None:
        item.clean = data.limpio

    try:
        db.commit()
        db.refresh(item)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to commit update for item %s", item_id)
        raise HTTPException(status_code=500, detail="Failed to update item")

    return ItemUpdateResponse(message="Actualizado correctamente", item=item)

@items_router.delete("/{item_id}", response_model=GenericMessageResponse)
def delete_item(
    item_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> GenericMessageResponse:
    item = db.query(ItemDB).filter(
        ItemDB.id == item_id,
        ItemDB.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    file_path = item.image_path
    db.delete(item)
    try:
        db.commit()
        fs_path = file_path.lstrip("/")
        if fs_path and os.path.exists(fs_path):
            os.remove(fs_path)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to commit delete for item %s", item_id)
        raise HTTPException(status_code=500, detail="Failed to delete item")

    return GenericMessageResponse(message="Eliminado correctamente")