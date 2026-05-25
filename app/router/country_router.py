from fastapi import APIRouter, Depends, BackgroundTasks, Request, Header
from sqlalchemy.orm import Session

from app.core.database import get_db

# from app.enums import NotificationType
from app.schema import GlobalResponse, NewCountryRequest, DisableCountryRequest
from services import CountryService


country_router = APIRouter()



# ==============================================================================

@country_router.get("/counties")
async def get_counties(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    countryService = CountryService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return countryService.get_active_countries()




# ==============================================================================

@country_router.post("/add-new-country")
async def new_country(
    request: Request,
    payload: NewCountryRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    countryService = CountryService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return countryService.add_new_country(payload=payload)


@country_router.put("/country-edit/{country_id}")
async def edit_country(
    country_id: str,
    request: Request,
    payload: NewCountryRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    countryService = CountryService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return countryService.edit_country(country_id=country_id, payload=payload)




# ==============================================================================

@country_router.post("/inactive-country")
async def inactive_country(
    request: Request,
    payload: DisableCountryRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    countryService = CountryService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return countryService.inactive_country(payload=payload)




# ==============================================================================

@country_router.post("/active-country")
async def active_country(
    request: Request,
    payload: DisableCountryRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    countryService = CountryService(
        db=db,
        background_tasks=background_tasks,
        request=request,
        authorization=authorization
    )

    return countryService.active_country(payload=payload)




# ==============================================================================
# ==============================================================================
