from datetime import timedelta

from fastapi import BackgroundTasks, HTTPException, Request
from sqlalchemy.orm import Session

from app.constants import AnsiColor, String
from app.enums import NotificationType, ActivityStatus
from app.model import SessionTable, SettingsTable, AdminTable, CountryTable, UserTable, AppConfigTable
from app.schema import GlobalResponse, CancelDeleteAccountRequest
from app.utils import Generators, Hashing

from app.model.admin_table import AdminRole


class SetupServices:
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
    
    def create_default_admin(
        self,
        email: str,
        password: str,
        full_name: str
    ):
        """
        Create default admin automatically when new DC/server is created.
        """

        existing_admin = self.db.query(AdminTable).first()

        if existing_admin:
            return existing_admin

        admin = AdminTable(
            admin_id=Generators.generate_id("admin"),
            email=email,
            password_hash=Hashing.create_hash(password),

            full_name=full_name,
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

    def create_default_user(
        self,
        email: str,
        password: str,
        full_name: str
    ):
        """
        Create default user automatically when new DC/server is created.
        """
        if not all([email, password, full_name]):
            print("Default user skipped: DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD, or DEFAULT_USER_NAME is missing.")
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
            UserTable.user_id == String.SYSTEM_USER_ID
        ).first()

        if not existing_user:
            existing_user = UserTable(
                user_id=String.SYSTEM_USER_ID,
                full_name=full_name,
                email_address=email,
                country_code=country.country_code,
                phone_number="01234567890",
                password_hash=Hashing.create_hash(password),
                profile_image_url=String.DEMO_PROFILE_IMAGE_URL,
                phone_verified=True,
                email_verified=True
            )
            self.db.add(existing_user)
            self.db.flush()

        settings = self.db.query(SettingsTable).filter(
            SettingsTable.user_id == existing_user.user_id
        ).first()

        if not settings:
            self.db.add(SettingsTable(
                user_id=existing_user.user_id,
                allow_notifications=True,
                dark_mode=False,
                country=country.country_iso,
                language="en",
                account_locked=False,
                
            ))

        session = self.db.query(SessionTable).filter(
            SessionTable.user_id == existing_user.user_id
        ).first()

        if not session:
            self.db.add(SessionTable(
                user_id=existing_user.user_id,
                session_id=Generators.generate_id("session"),
                device_id="system",
                device_uuid="system",
                last_ip_address="127.0.0.1"
            ))

        self.db.commit()
        self.db.refresh(existing_user)

        return existing_user

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

    def create_settings(self):
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



