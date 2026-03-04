import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..db.database import get_db
from ..db.models import OutfitDB, ItemDB, UserDB
from ..core.security import get_current_user
from .schemas import OutfitSaveRequest, OutfitSaveResponse

logger = logging.getLogger(__name__)

outfits_router = APIRouter(prefix="/outfits", tags=["Outfit History"], redirect_slashes=False)


@outfits_router.post("", response_model=OutfitSaveResponse)
def save_outfit(
    data: OutfitSaveRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OutfitSaveResponse:
    """Save a confirmed outfit and mark its items as dirty (worn)."""

    # Save the outfit snapshot
    new_outfit = OutfitDB(
        user_id=current_user.id,
        style=data.style,
        weather=data.weather,
        gender=data.gender,
        items_snapshot=[slot.model_dump() for slot in data.items_snapshot],
    )
    db.add(new_outfit)

    # Mark worn items as dirty
    if data.item_ids_to_dirty:
        db.query(ItemDB).filter(
            ItemDB.id.in_(data.item_ids_to_dirty),
            ItemDB.user_id == current_user.id,
        ).update({ItemDB.clean: False}, synchronize_session=False)

    try:
        db.commit()
        db.refresh(new_outfit)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to save outfit for user %s", current_user.id)
        raise HTTPException(status_code=500, detail="Failed to save outfit")

    return OutfitSaveResponse(
        id=new_outfit.id,
        style=new_outfit.style,
        weather=new_outfit.weather,
        gender=new_outfit.gender,
        items_snapshot=new_outfit.items_snapshot,
        worn_at=new_outfit.worn_at.isoformat(),
    )


@outfits_router.get("", response_model=List[OutfitSaveResponse])
def get_outfits(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[OutfitSaveResponse]:
    """Return all saved outfits for the current user, newest first."""
    outfits = (
        db.query(OutfitDB)
        .filter(OutfitDB.user_id == current_user.id)
        .order_by(OutfitDB.worn_at.desc())
        .all()
    )
    return [
        OutfitSaveResponse(
            id=o.id,
            style=o.style,
            weather=o.weather,
            gender=o.gender,
            items_snapshot=o.items_snapshot,
            worn_at=o.worn_at.isoformat(),
        )
        for o in outfits
    ]


@outfits_router.delete("/{outfit_id}", response_model=dict)
def delete_outfit(
    outfit_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    outfit = db.query(OutfitDB).filter(
        OutfitDB.id == outfit_id,
        OutfitDB.user_id == current_user.id,
    ).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    db.delete(outfit)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete outfit")
    return {"message": "Outfit deleted"}