from fastapi import HTTPException, Request, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.constants import AnsiColor, String
from app.model import CountryTable, AdminTable, SessionTable
from app.enums import ActivityStatus, NotificationType
from app.schema import CountryOut, NewCountryRequest, GlobalResponse, DisableCountryRequest
from app.utils import Generators, Hashing

from services.auth.token_service import TokenGenerators
from services.auth.user_verification import UserVerificationService
from services.notification.notification_services import NotificationData, NotificationServices, NotificationEvent


class CountryService(TokenGenerators):
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
        super().__init__()


    # get active country to get a list of active country
    def get_active_countries(self) -> GlobalResponse:
        """
        Fetch all countries with ACTIVE status.
        """
        try:
            # print(self.request.state.current_user)
            country: List[CountryTable] = self.db.query(CountryTable).filter(
                CountryTable.status == ActivityStatus.ACTIVE
            ).all()

            countrys = [CountryOut.model_validate(p) for p in country]

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="get_active_countries",
                message="Supported Countries",
                data={
                    "countries": countrys
                }
            )

        except HTTPException:
            raise
        
        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


    # get all country admin only
    def get_all_countries(self) -> GlobalResponse:
        """
        Fetch all countries regardless of status.
        """
        try:
            userVerificationService = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )
            
            admin: AdminTable = userVerificationService.verify_admin_authorization()

            countries: List[CountryTable] = self.db.query(CountryTable).all()
            country_list = [CountryOut.model_validate(c) for c in countries]

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="get_all_countries",
                message="All Countries",
                data={
                    "countries": country_list
                }
            )

        except HTTPException:
            raise
        
        except Exception as e:
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)
            

    # Add new country available for only admin
    def add_new_country(
        self,
        payload: NewCountryRequest
    ) -> GlobalResponse:
        """
        Logic to validate and create a new country record.
        """
        try:
            userVerificationService = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )
            
            admin: AdminTable = userVerificationService.verify_admin_authorization()
            
            country_id = Generators.generate_id("country")

            # check existin
            country = self.db.query(CountryTable).filter(
                or_(
                    CountryTable.country_name == payload.country_name,
                    CountryTable.country_code == payload.country_code,
                    CountryTable.currency == payload.currency_symbol
                )
            ).first()

            if country:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=String.COUNTRIES_ALREADY_EXISTS
                )
            
            # create new country
            country = CountryTable(
                counrty_id=country_id,
                counrty_name=payload.country_name,
                counrty_code=payload.country_code,
                flag_emoji=payload.flag_emoji,
                currency=payload.currency,
                currency_symbol=payload.currency,
                meta_data= {
                    "admin_id": admin.admin_id
                }
            )
            self.db.add(country)
            self.db.flush()


            
            # Step 8: Send notification alerts
            notification_services = NotificationServices(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )

            notification_services.send_notification(
                data=NotificationData(
                    user_id=admin.admin_id,
                    email_address=admin.email,
                    event=NotificationEvent.GENERAL_NOTIFICATION,
                    context={
                        "name": admin.full_name,
                        "title": "New Country Added Request Received",
                        "message": f"You have requested to become a New Country. The request was successful. Wait for your Country ID {country.country_id} account to be activated."
                    },
                    push=True,
                    email=True
                )
            )
            

            self.db.commit()
            self.db.refresh(country)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="add_new_country",
                message="Country Added Successfully",
                data={
                    "country_id": country.country_id,
                    "country_name": country.country_name,
                    "country_code": country.country_code,
                    "flag_emoji": country.flag_emoji,
                    "currency": country.currency,
                    "currency_symbol": country.currency_symbol
                },
                next_step={
                    "action": "wait_for_activation",
                    "message": "Wait for your Country ID account to be activated by the admin. You will receive a notification once it's activated."
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


    # Inactive country available for only admin
    def inactive_country(
        self,
        payload: DisableCountryRequest
    ) -> GlobalResponse:
        """
        Logic to validate and create a new country record.
        """
        try:
            userVerificationService = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )
            
            admin: AdminTable = userVerificationService.verify_admin_authorization()

            # check existin
            country = self.db.query(CountryTable).filter(
                CountryTable.country_id == payload.counrty_id
            ).first()

            if not country:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.NO_COUNTRY_FOUND
                )
            
            if (country.status == ActivityStatus.INACTIVE):
                raise HTTPException(
                    status_code=409,
                    detail="Country Alrady Inactive"
                )
            
            country.status = ActivityStatus.INACTIVE
            
            self.db.commit()
            self.db.refresh(country)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="inactive_country",
                message="Country INACTIVE Successfully",
                data={},
                next_step={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


    # Active country available for only admin
    def active_country(
        self,
        payload: DisableCountryRequest
    ) -> GlobalResponse:
        """
        Logic to validate and create a new country record.
        """
        try:
            userVerificationService = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )
            
            admin: AdminTable = userVerificationService.verify_admin_authorization()

            # check existin
            country = self.db.query(CountryTable).filter(
                CountryTable.country_id == payload.counrty_id
            ).first()

            if not country:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.NO_COUNTRY_FOUND
                )
            
            if (country.status == ActivityStatus.ACTIVE):
                raise HTTPException(
                    status_code=409,
                    detail="Country Alrady Active"
                )
            
            country.status = ActivityStatus.ACTIVE
            
            self.db.commit()
            self.db.refresh(country)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="active_country",
                message="Country ACTIVE Successfully",
                data={},
                next_step={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)


    # Edit country available for only admin
    def edit_country(
        self,
        country_id: str,
        payload: NewCountryRequest
    ) -> GlobalResponse:
        try:
            userVerificationService = UserVerificationService(
                db=self.db,
                background_tasks=self.background_tasks,
                request=self.request,
                authorization=self.authorization
            )
            
            admin: AdminTable = userVerificationService.verify_admin_authorization()

            country = self.db.query(CountryTable).filter(
                CountryTable.country_id == country_id
            ).first()

            if not country:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.NO_COUNTRY_FOUND
                )

            existing_country = self.db.query(CountryTable).filter(
                CountryTable.country_id != country_id,
                CountryTable.country_name == payload.country_name
            ).first()

            if existing_country:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=String.COUNTRIES_ALREADY_EXISTS
                )

            country.country_name = payload.country_name
            country.country_code = payload.country_code
            country.flag_emoji = payload.flag_emoji
            country.currency = payload.currency
            country.currency_symbol = payload.currency_symbol

            self.db.commit()
            self.db.refresh(country)

            return GlobalResponse(
                status_code=status.HTTP_200_OK,
                success=True,
                action="edit_country",
                message="Country Updated Successfully",
                data={
                    "country_id": country.country_id,
                    "country_name": country.country_name,
                    "country_code": country.country_code,
                    "flag_emoji": country.flag_emoji,
                    "currency": country.currency,
                    "currency_symbol": country.currency_symbol
                },
                next_step={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)






# ==============================================================================
# ==============================================================================
