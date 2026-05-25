from fastapi import BackgroundTasks, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.constants import AnsiColor, String
from app.model import OfferTable
from app.schema import GlobalResponse, OfferCreateRequest, OfferUpdateRequest
from app.utils.helpers import utc6dhaka


class OfferServices:
    def __init__(
        self,
        db: Session,
        background_tasks: BackgroundTasks,
        request: Request,
        authorization: str
    ):
        self.db = db
        self.background_tasks = background_tasks
        self.request = request
        self.authorization = authorization

    def _offer_to_dict(self, offer: OfferTable) -> dict:
        return {
            "id": offer.id,
            "image_url": offer.image_url,
            "title": offer.title,
            "description": offer.description,
            "target_user": offer.target_user,
            "meta_data": offer.meta_data,
            "created_at": offer.created_at.isoformat() if offer.created_at else None,
            "expires_at": offer.expires_at.isoformat() if offer.expires_at else None,
        }
    
    def create_offer(self, payload: OfferCreateRequest) -> GlobalResponse:
        try:
            offer = OfferTable(
                image_url=payload.image_url,
                title=payload.title,
                description=payload.description,
                target_user=payload.target_user,
                meta_data=payload.meta_data,
                expires_at=payload.expires_at
            )

            self.db.add(offer)
            self.db.commit()
            self.db.refresh(offer)

            return GlobalResponse(
                success=True,
                message="Offer added successfully",
                data={
                    "offer": self._offer_to_dict(offer)
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def update_offer(self, payload: OfferUpdateRequest) -> GlobalResponse:
        try:
            offer = self.db.query(OfferTable).filter(OfferTable.id == payload.offer_id).first()

            if not offer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Offer not found"
                )

            update_data = payload.model_dump(exclude_unset=True, exclude={"offer_id"})
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No update data provided"
                )

            for field, value in update_data.items():
                setattr(offer, field, value)

            self.db.commit()
            self.db.refresh(offer)

            return GlobalResponse(
                success=True,
                message="Offer updated successfully",
                data={
                    "offer": self._offer_to_dict(offer)
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def delete_offer(self, offer_id) -> GlobalResponse:
        try:
            offer = self.db.query(OfferTable).filter(OfferTable.id == offer_id).first()

            if not offer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Offer not found"
                )

            self.db.delete(offer)
            self.db.commit()

            return GlobalResponse(
                success=True,
                message="Offer deleted successfully",
                data={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def get_offer(self, offer_id) -> GlobalResponse:
        try:
            offer = self.db.query(OfferTable).filter(OfferTable.id == offer_id).first()

            if not offer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Offer not found"
                )

            return GlobalResponse(
                success=True,
                message="Offer fetched successfully",
                data={
                    "offer": self._offer_to_dict(offer)
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def list_offers(self, include_expired: bool) -> GlobalResponse:
        # Logic to list all offers
        try:
            query = self.db.query(OfferTable)

            if not include_expired:
                query = query.filter(OfferTable.expires_at >= utc6dhaka())

            offers = query.order_by(OfferTable.created_at.desc()).all()

            return GlobalResponse(
                success=True,
                message="Offers fetched successfully",
                data={
                    "offers": [self._offer_to_dict(offer) for offer in offers]
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)
