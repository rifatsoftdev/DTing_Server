from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, Header, Request, UploadFile, status
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional
from datetime import date

from app.core.database import get_db
from app.core.rate_limit import settings_rate_limit

from app.schema import GlobalResponse
from app.schema import ServiceAddRequest, ServiceUpdateRequest, ServiceDeleteRequest
from services import UserServices
from services.auth.user_verification import UserVerificationService




service_router =  APIRouter()


services: list = [
    {"service_name": "DTing", "service_slug": "dting"},
    {"service_name": "DTube", "service_slug": "dtube"},
    {"service_name": "PocketPay", "service_slug": "pocketpay"},
    {"service_name": "DTing Cloud", "service_slug": "dting-cloud"},
]


@service_router.get("/get-services", response_model=GlobalResponse)
def get_services(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> GlobalResponse:
    """
    Get all services for an authorized user.
    """
    settings_rate_limit(request)

    user_verification_service = UserVerificationService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    user_id = user_verification_service.verify_authorization(authorization)

    available_service_slugs = [service["service_slug"] for service in services]
    current_services = UserServices.get_user_services(db, user_id)
    current_by_slug = {item["service_slug"]: item for item in current_services}

    service_list = []
    for service in services:
        existing = current_by_slug.get(service["service_slug"])
        service_list.append({
            "service_name": service["service_name"],
            "service_slug": service["service_slug"],
            "enabled": existing is not None,
            "status": existing["status"] if existing else None,
            "service_details": existing["service_details"] if existing else None,
            "id": existing["id"] if existing else None,
            "user_id": user_id,
        })

    extra_services = [
        item for slug, item in current_by_slug.items()
        if slug not in available_service_slugs
    ]
    service_list.extend(extra_services)

    active_services = [item for item in service_list if item.get("enabled")]

    return GlobalResponse(
        status_code=status.HTTP_200_OK,
        success=True,
        action="get_services",
        message="User services retrieved successfully",
        data={
            "active_services": active_services,
            "included_services": available_service_slugs
        },
        next_step={}
    )


@service_router.post("/add-service", response_model=GlobalResponse)
def add_service(
    payload: ServiceAddRequest,
    request: Request,
    db: Session = Depends(get_db),
    user_id: Optional[str] = Header(None)
) -> GlobalResponse:
    settings_rate_limit(request)

    if not user_id:
        return GlobalResponse(success=False, message="User ID is required in header", data={})

    service_slug = payload.service_slug.strip()
    service_name = payload.service_name or next(
        (service["service_name"] for service in services if service["service_slug"] == service_slug),
        " ".join(part.capitalize() for part in service_slug.split("-"))
    )
    created = UserServices.add_user_service(
        db=db,
        user_id=user_id,
        service_slug=service_slug,
        service_name=service_name,
        service_details=payload.service_details,
        service_status=payload.status,
    )

    return GlobalResponse(
        status_code=200,
        success=True,
        action="add_service",
        message="Service added successfully",
        data={"service": created},
        next_step={}
    )


@service_router.put("/update-service", response_model=GlobalResponse)
def update_service(
    payload: ServiceUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    user_id: Optional[str] = Header(None)
) -> GlobalResponse:
    settings_rate_limit(request)

    if not user_id:
        return GlobalResponse(success=False, message="User ID is required in header", data={})

    updated = UserServices.update_user_service(
        db=db,
        user_id=user_id,
        service_slug=payload.service_slug.strip(),
        service_name=payload.service_name,
        service_details=payload.service_details,
        service_status=payload.status,
    )

    return GlobalResponse(
        status_code=200,
        success=True,
        action="update_service",
        message="Service updated successfully",
        data={"service": updated},
        next_step={}
    )


@service_router.delete("/delete-service", response_model=GlobalResponse)
def delete_service(
    payload: ServiceDeleteRequest,
    request: Request,
    db: Session = Depends(get_db),
    user_id: Optional[str] = Header(None)
) -> GlobalResponse:
    settings_rate_limit(request)

    if not user_id:
        return GlobalResponse(success=False, message="User ID is required in header", data={})

    UserServices.delete_user_service(
        db=db,
        user_id=user_id,
        service_slug=payload.service_slug.strip(),
    )

    return GlobalResponse(
        status_code=200,
        success=True,
        action="delete_service",
        message="Service deleted successfully",
        data={"service_slug": payload.service_slug.strip()},
        next_step={}
    )