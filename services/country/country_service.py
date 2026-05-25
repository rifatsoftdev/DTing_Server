from fastapi import HTTPException, Request, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.constants import AnsiColor, String
from app.model import CountryTable, AdminTable, SessionTable
from app.enums import ActivityStatus, NotificationType
from app.schema import CountryOut, NewCountryRequest, GlobalResponse, DisableCountryRequest
from app.utils import Generators, Hashing

from services.auth.user_verification import UserVerificationService


class CountryService:
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

    def _verify_requester(self, payload):
        access_token = payload.access_token
        token_payload = Token().decode_token(access_token)

        if not token_payload or token_payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=String.INVALID_TOKEN
            )

        admin_id = token_payload.get("admin_id")
        if admin_id:
            if payload.user_id != admin_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=String.INVALID_TOKEN
                )

            admin = self.db.query(AdminTable).filter(
                AdminTable.admin_id == admin_id
            ).first()

            if not admin or not admin.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Admin not found or inactive"
                )

            session_query = self.db.query(SessionTable).filter(
                SessionTable.admin_id == admin_id,
                SessionTable.is_login == True
            )

            device_id = getattr(payload, "device_id", None) or getattr(payload, "android_id", None)
            device_uuid = getattr(payload, "device_uuid", None) or getattr(payload, "android_uuid", None)

            if device_id:
                session_query = session_query.filter(SessionTable.device_id == device_id)
            if device_uuid:
                session_query = session_query.filter(SessionTable.device_uuid == device_uuid)

            sessions = session_query.all()
            valid_session = any(
                session.access_token_hash and Hashing.verify_hash(access_token, session.access_token_hash)
                for session in sessions
            )

            if not valid_session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Admin session not found"
                )

            return {
                "user": None,
                "meta": {
                    "admin_id": admin.admin_id,
                    "email": admin.email,
                    "name": admin.full_name
                }
            }

        user_verification_service = UserVerificationService(
            db=self.db,
            background_tasks=self.background_tasks,
            request=self.request,
            authorization=self.authorization
        )

        user = user_verification_service.verify_user(
            db=self.db,
            user_id=payload.user_id,
            access_token=payload.access_token,
            android_id=getattr(payload, "android_id", None) or getattr(payload, "device_id", None),
            android_uuid=getattr(payload, "android_uuid", None) or getattr(payload, "device_uuid", None),
            password=getattr(payload, "user_password", None) or None
        )

        return {
            "user": user,
            "meta": {
                "user_id": user.user_id,
                "phone": user.phone_number,
                "email": user.email_address,
                "name": user.full_name
            }
        }

    def get_active_countries(self) -> GlobalResponse:
        """
        Fetch all countries with ACTIVE status.
        """
        try:
            country = self.db.query(CountryTable).filter(
                CountryTable.status == ActivityStatus.ACTIVE
            ).all()

            countrys = [CountryOut.model_validate(p) for p in country]

            return GlobalResponse(
                success=True,
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

    def add_new_country(
        self,
        payload: NewCountryRequest
    ) -> GlobalResponse:
        """
        Logic to validate and create a new country record.
        """
        try:
            requester = self._verify_requester(payload)
            user = requester["user"]

            # print(user)

            name: str = payload.counrty_name
            code: str = payload.counrty_code
            flag_emoji: str = payload.flag_emoji
            currency: str = payload.currency
            currency_symbol: str = payload.currency_symbol
            
            country_id = Generators.generate_id("country")

            # check existin
            country = self.db.query(CountryTable).filter(
                CountryTable.counrty_name == name,
                CountryTable.counrty_code == code,
                CountryTable.currency == currency
            ).first()

            if country:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=String.COUNTRIES_ALREADY_EXISTS
                )
            
            # create new country
            country = CountryTable(
                counrty_id=country_id,
                counrty_name=name,
                counrty_code=code,
                flag_emoji=flag_emoji,
                currency=currency,
                currency_symbol=currency_symbol,
                meta_data= {
                    "request_user": requester["meta"]
                }
            )
            self.db.add(country)
            self.db.flush()

            # real time notification
            if user:
                notifier = NotificationManager(self.db)

                notifier.send_user_notification(
                    background_tasks=self.background_tasks,
                    user_id=user.user_id,
                    title="New Country Added Request Received",
                    short_body=f"You have requested to become a New Country. The request was successful. Wait for your Country ID {country.counrty_id} account to be activated.",
                    long_body=None,
                    noty_type=NotificationType.REQUEST,
                    image_url=None,
                    push=True,
                    sms=False,
                    email=False
                )

            self.db.commit()
            self.db.refresh(country)

            return GlobalResponse(
                success=True,
                message="Country Added Successfully",
                data={
                    "country_id": country.counrty_id,
                    "country_name": country.counrty_name,
                    "country_code": country.counrty_code,
                    "flag_emoji": country.flag_emoji,
                    "currency": country.currency,
                    "currency_symbol": country.currency_symbol
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def inactive_country(
        self,
        payload: DisableCountryRequest
    ) -> GlobalResponse:
        """
        Logic to validate and create a new country record.
        """
        try:
            self._verify_requester(payload)

            # check existin
            country = self.db.query(CountryTable).filter(
                CountryTable.counrty_id == payload.counrty_id
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
                success=True,
                message="Country INACTIVE Successfully",
                data={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def active_country(
        self,
        payload: DisableCountryRequest
    ) -> GlobalResponse:
        """
        Logic to validate and create a new country record.
        """
        try:
            self._verify_requester(payload)

            # check existin
            country = self.db.query(CountryTable).filter(
                CountryTable.counrty_id == payload.counrty_id
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
                success=True,
                message="Country ACTIVE Successfully",
                data={}
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)

    def edit_country(
        self,
        country_id: str,
        payload: NewCountryRequest
    ) -> GlobalResponse:
        try:
            self._verify_requester(payload)

            country = self.db.query(CountryTable).filter(
                CountryTable.counrty_id == country_id
            ).first()

            if not country:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=String.NO_COUNTRY_FOUND
                )

            existing_country = self.db.query(CountryTable).filter(
                CountryTable.counrty_id != country_id,
                CountryTable.counrty_name == payload.counrty_name
            ).first()

            if existing_country:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=String.COUNTRIES_ALREADY_EXISTS
                )

            country.counrty_name = payload.counrty_name
            country.counrty_code = payload.counrty_code
            country.flag_emoji = payload.flag_emoji
            country.currency = payload.currency
            country.currency_symbol = payload.currency_symbol

            self.db.commit()
            self.db.refresh(country)

            return GlobalResponse(
                success=True,
                message="Country Updated Successfully",
                data={
                    "country_id": country.counrty_id,
                    "country_name": country.counrty_name,
                    "country_code": country.counrty_code,
                    "flag_emoji": country.flag_emoji,
                    "currency": country.currency,
                    "currency_symbol": country.currency_symbol
                }
            )

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            print(f"{AnsiColor.RED}INFO{AnsiColor.RESET}:    {e}")
            raise HTTPException(status_code=500, detail=String.SERVER_ERROR)




