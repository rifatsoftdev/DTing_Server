import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.constants import AnsiColor, String
from app.core.database import get_db
from app.enums import ReadStatus
from app.model import AdminTable, FeedbackTable, UserTable
from app.schema.global_schema import GlobalResponse
from services.auth.user_verification import UserVerificationService


feedback_router = APIRouter()


class FeedbackCreateRequest(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    subject: Optional[str] = Field(default=None, max_length=255)
    message: str
    app_version: Optional[str] = Field(default=None, max_length=50)
    platform: Optional[str] = Field(default=None, max_length=20)
    device_info: Optional[str] = None


def _format_datetime(value):
    return value.strftime("%Y:%m:%d %I:%M:%S %p") if value else None


def _feedback_data(feedback: FeedbackTable) -> dict:
    user = feedback.user

    return {
        "id": feedback.id,
        "user_id": feedback.user_id,
        "user": {
            "full_name": user.full_name if user else None,
            "email_address": user.email_address if user else None,
            "phone_number": f"{user.country_code or ''}{user.phone_number or ''}" if user and user.phone_number else None,
        },
        "rating": feedback.rating,
        "subject": feedback.subject,
        "message": feedback.message,
        "app_version": feedback.app_version,
        "platform": feedback.platform,
        "device_info": feedback.device_info,
        "status": feedback.status.value if feedback.status else None,
        "admin_reply": feedback.admin_reply,
        "created_at": _format_datetime(feedback.created_at),
        "updated_at": _format_datetime(feedback.updated_at),
    }


def _verify_user(db: Session, request: Request, background_tasks: BackgroundTasks, authorization: str) -> UserTable:
    verifier = UserVerificationService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )
    user_id = verifier.verify_authorization(authorization=authorization)

    user = db.query(UserTable).filter(UserTable.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only users can submit feedback"
        )

    return user


def _verify_admin(db: Session, request: Request, background_tasks: BackgroundTasks, authorization: str) -> AdminTable:
    verifier = UserVerificationService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )
    admin_id = verifier.verify_authorization(authorization=authorization)

    admin = db.query(AdminTable).filter(AdminTable.admin_id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only admins can view feedback"
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )

    return admin


def _list_feedbacks(db: Session, read_status: ReadStatus | None = None, limit: int = 50, offset: int = 0) -> GlobalResponse:
    query = db.query(FeedbackTable)

    if read_status:
        query = query.filter(FeedbackTable.status == read_status)

    total = query.count()
    feedbacks = query.order_by(FeedbackTable.created_at.desc()).offset(offset).limit(limit).all()

    return GlobalResponse(
        status_code=status.HTTP_200_OK,
        success=True,
        action="fetch_feedbacks",
        message="Feedbacks fetched successfully",
        data={
            "status": read_status.value if read_status else "all",
            "feedbacks": [_feedback_data(feedback) for feedback in feedbacks],
        },
        pagination={
            "total": total,
            "limit": limit,
            "offset": offset,
        },
        next_step={}
    )


@feedback_router.post("/submit", response_model=GlobalResponse)
async def submit_feedback(
    payload: FeedbackCreateRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    try:
        user = _verify_user(
            db=db,
            request=request,
            background_tasks=background_tasks,
            authorization=authorization
        )

        feedback = FeedbackTable(
            id=str(uuid.uuid4()),
            user_id=user.user_id,
            rating=payload.rating,
            subject=payload.subject,
            message=payload.message,
            app_version=payload.app_version,
            platform=payload.platform,
            device_info=payload.device_info,
            status=ReadStatus.UNREAD
        )

        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        return GlobalResponse(
            status_code=status.HTTP_201_CREATED,
            success=True,
            action="submit_feedback",
            message="Feedback submitted successfully",
            data={
                "feedback": _feedback_data(feedback)
            },
            next_step={}
        )

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
        raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


@feedback_router.get("/admin/all", response_model=GlobalResponse)
async def admin_all_feedbacks(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    _verify_admin(
        db=db,
        request=request,
        background_tasks=background_tasks,
        authorization=authorization
    )

    return _list_feedbacks(
        db=db,
        limit=limit,
        offset=offset
    )


@feedback_router.get("/admin/read", response_model=GlobalResponse)
async def admin_read_feedbacks(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    _verify_admin(
        db=db,
        request=request,
        background_tasks=background_tasks,
        authorization=authorization
    )

    return _list_feedbacks(
        db=db,
        read_status=ReadStatus.READ,
        limit=limit,
        offset=offset
    )


@feedback_router.get("/admin/unread", response_model=GlobalResponse)
async def admin_unread_feedbacks(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    _verify_admin(
        db=db,
        request=request,
        background_tasks=background_tasks,
        authorization=authorization
    )

    return _list_feedbacks(
        db=db,
        read_status=ReadStatus.UNREAD,
        limit=limit,
        offset=offset
    )


@feedback_router.post("/admin/{feedback_id}/read", response_model=GlobalResponse)
async def admin_mark_feedback_read(
    feedback_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    try:
        _verify_admin(
            db=db,
            request=request,
            background_tasks=background_tasks,
            authorization=authorization
        )

        feedback = db.query(FeedbackTable).filter(
            FeedbackTable.id == feedback_id
        ).first()

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )

        feedback.status = ReadStatus.READ
        db.commit()
        db.refresh(feedback)

        return GlobalResponse(
            status_code=status.HTTP_200_OK,
            success=True,
            action="mark_feedback_read",
            message="Feedback marked as read successfully",
            data={
                "feedback": _feedback_data(feedback)
            },
            next_step={}
        )

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:     {e}")
        raise HTTPException(status_code=500, detail=String.SERVER_ERROR)
