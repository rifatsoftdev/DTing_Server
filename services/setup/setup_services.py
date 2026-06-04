from datetime import timedelta

from fastapi import BackgroundTasks, HTTPException, Request
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.constants import AnsiColor, String, ENV
from app.enums import NotificationType, ActivityStatus
from app.model import SessionTable, SettingsTable, AdminTable, CountryTable, UserTable, AppConfigTable, ServicesTable
from app.schema import GlobalResponse, CancelDeleteAccountRequest
from app.utils import Generators, Hashing

from services.auth.signup_service import RegistrationService

from app.model.admin_table import AdminRole



class SetupServices(RegistrationService):
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

        super().__init__(
            db=db,
            background_tasks=background_tasks,
            request=request,
            authorization=authorization
        )

        self.create_default_admin()
        self.add_default_countries()
        self.create_default_user()
        self.create_settings()
        self.create_services()
    
    def create_default_admin(self) -> None:
        """
        Create default admin automatically when new DC/server is created.
        """

        existing_admin = self.db.query(AdminTable).first()

        if existing_admin:
            return existing_admin

        admin = AdminTable(
            admin_id=Generators.generate_id("admin"),
            email=ENV.DEFAULT_ADMIN_EMAIL,
            password_hash=Hashing.create_hash(ENV.DEFAULT_ADMIN_PASSWORD),

            full_name=ENV.DEFAULT_ADMIN_NAME,
            profile_image_url=None,

            totp_enabled=False,
            totp_secret=None,

            role=AdminRole.SUPER_ADMIN,
            permissions='["ALL"]',

            is_active=True,
            is_super_admin=True,

            last_login_at=None,
            last_ip_address=None
        )

        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)

        return admin

    def create_default_user(self) -> None:
        """
        Create default user automatically when new DC/server is created.
        """
        email_address: str = ENV.DEFAULT_USER_EMAIL
        full_name: str = ENV.DEFAULT_USER_NAME
        password: str = ENV.DEFAULT_USER_PASSWORD

        if not all([email_address, password, full_name]):
            print(f"{AnsiColor.RED}Default user skipped: DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD, or DEFAULT_USER_NAME is missing.{AnsiColor.RESET}")
            return None

        country = self.db.query(CountryTable).filter(
            CountryTable.country_code == "+88"
        ).first()

        if not country:
            country = CountryTable(
                country_id=Generators.generate_id("country"),
                country_name="Bangladesh",
                country_code="+88",
                flag_emoji="🇧🇩",
                currency="BDT",
                currency_symbol="৳",
                status=ActivityStatus.ACTIVE,
                country_iso="BD"
            )
            self.db.add(country)
            self.db.flush()

        existing_user = self.db.query(UserTable).filter(
            or_(
                UserTable.user_id == String.SYSTEM_USER_ID,
                UserTable.email_address == email_address
            )
        ).first()

        if not existing_user:
            user: UserTable = self._create_new_user(
                full_name=full_name,
                email_address=email_address,
                phone_number=ENV.DEFAULT_USER_PHONE,
                country=country,
                user_password=password,
                device_id="server",
                device_uuid="server"
            )

            user.email_verified = True
            user.phone_verified = True

            self.db.commit()
            self.db.refresh(user)
        
    def add_default_countries(self) -> None:
        """
        Add default countries to the database when new DC/server is created.
        """
        existing_countries = self.db.query(CountryTable).first()

        if existing_countries:
            return existing_countries

        default_countries = [
            {
                "country_id": Generators.generate_id("country"),
                "country_name": "India",
                "country_code": "+91",
                "flag_emoji": "🇮🇳",
                "currency": "Indian Rupee",
                "currency_symbol": "₹",
                "status": ActivityStatus.ACTIVE,
                "country_iso": "IN"
            },
            {
                "country_id": Generators.generate_id("country"),
                "country_name": "Bangladesh",
                "country_code": "+88",
                "flag_emoji": "🇧🇩",
                "currency": "BDT",
                "currency_symbol": "৳",
                "status": ActivityStatus.ACTIVE,
                "country_iso": "BD"
            },
            {
                "country_id": Generators.generate_id("country"),
                "country_name": "United States",
                "country_code": "+1",
                "flag_emoji": "🇺🇸",
                "currency": "US Dollar",
                "currency_symbol": "$",
                "status": ActivityStatus.ACTIVE,
                "country_iso": "US"
            },
            {
                "country_id": Generators.generate_id("country"),
                "country_name": "United Kingdom",
                "country_code": "+44",
                "flag_emoji": "🇬🇧",
                "currency": "British Pound Sterling",
                "currency_symbol": "£",
                "status": ActivityStatus.ACTIVE,
                "country_iso": "GB"
            }
        ]

        for country in default_countries:
            country_entry = CountryTable(
                country_id=country["country_id"],
                country_name=country["country_name"],
                country_code=country["country_code"],
                flag_emoji=country["flag_emoji"],
                currency=country["currency"],
                currency_symbol=country["currency_symbol"],
                status=country["status"],
                country_iso=country["country_iso"]
            )
            self.db.add(country_entry)

        self.db.commit()

    def create_settings(self) -> None:
        settings = {
            "email_settings": {
                "enabled": True
            },
            "push_settings": {
                "enabled": True
            },
            "sms_settings": {
                "enabled": False
            },
            "signup_settings": {
                "google_signup": True
            },
            "signin_settings": {
                "enabled": True
            },
            "recharge_settings": {
                "min": 10,
                "max": 1000
            }
        }

        # Get all existing keys in one query to avoid N+1 overhead
        existing_keys = {c.key for c in self.db.query(AppConfigTable.key).all()}

        # check existing keys individually
        for key, val in settings.items():
            if key not in existing_keys:
                config_entry = AppConfigTable(key=key, value=val)
                self.db.add(config_entry)

        self.db.commit()

        return True

    def create_services(self) -> None:
        pass





# ==============================================================================
# ==============================================================================
