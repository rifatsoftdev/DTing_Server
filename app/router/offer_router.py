from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Header, Query, Request, status
from sqlalchemy.orm import Session

from app.constants import AnsiColor, String
from app.core.database import get_db
from app.model import OfferTable
from app.schema import GlobalResponse, OfferCreateRequest, OfferUpdateRequest
from app.utils.helpers import utc6dhaka
from services.offer.offer_services import OfferServices


offer_router = APIRouter()



# ==============================================================================

@offer_router.get("/offers")
async def get_offers(
    background_tasks: BackgroundTasks,
    request: Request,
    include_expired: bool = Query(False),
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    offerServices = OfferServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return offerServices.list_offers(include_expired=include_expired)




# ==============================================================================

@offer_router.get("/offers/{offer_id}")
async def get_offer(
    offer_id: int,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    offerServices = OfferServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return offerServices.get_offer(offer_id=offer_id)




# ==============================================================================

@offer_router.post("/add-offer")
async def add_offer(
    payload: OfferCreateRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    offerServices = OfferServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return offerServices.create_offer(payload=payload)




# ==============================================================================

@offer_router.put("/edit-offer")
async def edit_offer(
    payload: OfferUpdateRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    offerServices = OfferServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return offerServices.update_offer(payload=payload)




# ==============================================================================

@offer_router.delete("/delete-offer/{offer_id}")
async def delete_offer(
    offer_id: int,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    offerServices = OfferServices(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return offerServices.delete_offer(offer_id=offer_id)




# ==============================================================================
# ==============================================================================
