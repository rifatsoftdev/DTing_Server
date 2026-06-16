import json

from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, Header, Request, UploadFile, status
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional,List
from datetime import date

from app.core.database import get_db
from app.core.rate_limit import settings_rate_limit

from app.model import UserTable, UserServicesTable
from app.schema import GlobalResponse
from app.schema import ServiceAddRequest, ServiceUpdateRequest, ServiceDeleteRequest
from services import UserServices
from services.auth.user_verification import UserVerificationService




service_router =  APIRouter()



import json

with open("app/json/services.json", "r") as f:
    services_data = json.load(f)

services = services_data["services"]


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

    user_id: str = user_verification_service.verify_authorization(authorization)

    user: UserTable = db.query(UserTable).filter(
        UserTable.user_id == user_id
    ).first()

    user_services: List[UserServicesTable] = user.user_services

    active_services = []
    available_services = []

    # active services (user DB)
    for service in user_services:
        active_services.append({
            "service_name": service.service_name,
            "service_slug": service.service_slug,
            "logo_url": service.logo_url
        })

    # available services (JSON)
    for key, service in services.items():
        if not any(s["service_slug"] == service["service_slug"] for s in active_services):
            available_services.append(service)

    return GlobalResponse(
        status_code=status.HTTP_200_OK,
        success=True,
        action="get_services",
        message="User services retrieved successfully",
        data={
            "active_services": active_services,
            "available_service": available_services
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
        return GlobalResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="User ID is required in header",
            data={}
        )

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
        return GlobalResponse(
            success=False,
            message="User ID is required in header",
            data={}
        )

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
