# DTing Authentication Server

**DTing** stands for **Dreme Tech in Next Generation**. This repository is the main authentication and user-management server for DTing services. It is designed as the central backend where users can register, log in, manage their profile, verify their account, upload profile/KYC images, enable two-factor authentication, receive notifications, request developer access, and buy or access company services.

<!-- This project is also part of the DTing portfolio, showing a production-minded backend built with FastAPI, SQLAlchemy, JWT authentication, OTP workflows, cloud image storage, email/SMS integrations, Firebase notifications, Redis-backed rate limiting, and Docker support. -->

## Project Highlights

- User registration, login, logout, and multi-device session handling
- JWT access and refresh token based authentication
- Google login and Google account linking
- OTP send and verify workflow
- Password reset, change password, delete account, and cancel delete request
- User profile view, edit, update, and profile image upload
- KYC submission with front, back, and face image upload
- Two-factor authentication through TOTP, email, and SMS flows
- Developer access request, cancellation, API key workflow, and payment endpoint
- Offers and service-purchase related modules
- Country management and default country setup
- User notification history and WebSocket notification support
- Admin settings pages and template-based UI routes
- Cloudinary integration for media storage
- Firebase Cloud Messaging support
- Redis and SlowAPI based rate limiting
- Docker-ready deployment

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend Framework | FastAPI |
| ASGI Server | Uvicorn |
| Database ORM | SQLAlchemy |
| Default Database | SQLite |
| Production Database Support | PostgreSQL via `psycopg2-binary` |
| Auth | JWT, password hashing, sessions |
| Two-Factor Auth | PyOTP, email OTP, SMS OTP |
| File Storage | Cloudinary |
| Notification | Firebase Admin SDK, WebSocket |
| Email/SMS | SMTP, Twilio/SMS server integration |
| Rate Limiting | SlowAPI + Redis |
| Templates | Jinja2 |
| Container | Docker |

## Repository Structure

```text
Authentication_Server/
├── app/
│   ├── core/              # Database connection and base setup
│   ├── constants/         # Environment and shared constants
│   ├── middleware/        # Authentication middleware
│   ├── model/             # SQLAlchemy database models
│   ├── router/            # FastAPI route groups
│   ├── schema/            # Pydantic request/response schemas
│   ├── templates/         # Notification templates
│   └── utils/             # Hashing, token, validation, upload helpers
├── services/              # Business logic layer
├── templates/             # HTML pages for auth and account flows
├── static/                # Static assets, Bootstrap, images, favicon
├── json/                  # Default config/service JSON files
├── test/                  # API test utilities
├── Dockerfile             # Docker image definition
├── requirements.txt       # Python dependencies
└── run.py                 # Local development runner
```

## Main API Groups

| Prefix | Purpose |
| --- | --- |
| `/auth` | Register, login, logout, OTP, password reset, token refresh, account delete |
| `/user` | Profile, profile update, image upload, KYC submission |
| `/tfa` | TOTP, email 2FA, and SMS 2FA setup/confirm/disable |
| `/dev` | Developer request, cancel request, payment, WebSocket connection |
| `/offer` | Offer list, details, add, edit, delete |
| `/history` | Notification and transaction history related endpoints |
| `/country` | Country list and country management |
| `/ws` | WebSocket notifications |
| `/admin/settings` | Admin settings pages |
| `/login`, `/signup`, `/terms`, `/privacy` | Template-rendered UI pages |

Interactive API documentation is available after running the server:

```text
http://localhost:8000/docs
http://localhost:8000/redoc
```

## Requirements

- Python 3.10+
- Redis server for rate limiting
- SQLite for local development or PostgreSQL for production
- Cloudinary account for image upload
- SMTP email account for email verification/password reset
- Firebase service account JSON for push notifications
- Twilio or compatible SMS server for SMS OTP

## Local Setup

Clone the repository and enter the project directory:

```bash
git clone <your-repository-url>
cd Authentication_Server
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```bash
cp .env.example .env
```

If `.env.example` is not available yet, create `.env` manually using the template below.

## Environment Variables

Use strong private values in production. Never commit real secrets to Git.

```env
# App
VERSION=2.0.8
DEBUG=True
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Database
DATABASE_URL=sqlite:///./database.db

# JWT
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_EXPIRE=10
REFRESH_EXPIRE=1440
OTP_TOKEN_EXPIRE_MIN=5
PASS_RST_TOKEN_EXPIRE_MIN=15
SALT=replace-with-random-salt

# Redis
REDIS_URL=redis://localhost:6379/0
EMAIL_QUEUE_NAME=email_queue
EMAIL_FAILED_QUEUE_NAME=email_failed_queue
SMS_QUEUE_NAME=sms_queue
SMS_FAILED_QUEUE_NAME=sms_failed_queue

# Email
EMAIL_ADDRESS=your-email@example.com
EMAIL_PASSWORD=your-email-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False

# SMS
ACCOUNT_SID=your-twilio-account-sid
AUTH_TOKEN=your-twilio-auth-token
SMS_SERVER=http://localhost:8001

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Firebase
POCKETPAY_ADMINSDK={}
GOOGLE_CLIENT_ID=your-google-client-id

# Rewards and charges
NEW_USER_REWARD_WITH_REFERRAL=100
NEW_USER_REWARD_WITH_NO_REFERRAL=50
USER_REFERRAL_REWARD=20
SERVICE_CHARGE=1.0

# Default startup accounts
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PHONE=01700000000
DEFAULT_ADMIN_PASSWORD=change-this-password
DEFAULT_ADMIN_NAME=Admin DTing
DEFAULT_USER_EMAIL=user@example.com
DEFAULT_USER_PHONE=01700000001
DEFAULT_USER_PASSWORD=change-this-password
DEFAULT_USER_NAME=DTing User
```

## Run Locally

Start Redis first if your environment uses the default rate limiter configuration:

```bash
redis-server
```

Run the FastAPI server:

```bash
python run.py
```

Or run with Uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at:

```text
http://localhost:8000
```

## Docker Run

Build the Docker image:

```bash
docker build -t dting-authentication-server .
```

Run the container:

```bash
docker run --env-file .env -p 8000:8000 dting-authentication-server
```

## Security Notes

- Replace all default passwords before production deployment.
- Keep `.env`, database files, certificates, and service-account JSON files private.
- Use HTTPS in production.
- Restrict CORS origins to trusted frontend domains.
- Use a production database such as PostgreSQL for public deployment.
- Rotate JWT secrets and third-party API keys if they were ever exposed.
- Keep Redis private and reachable only by trusted application servers.
- Review admin and default-user creation logic before going live.

## Development Notes

- Database tables are created automatically from SQLAlchemy models on startup.
- Local development uses `database.db` by default.
- Startup setup creates default countries, app settings, and optional default accounts.
- API response format uses shared schema models from `app/schema`.
- Business logic is separated into the `services/` layer.

## Brand

**Company:** DTing  
**Full Name:** Dreme Tech in Next Generation  
**Purpose:** Building next-generation digital services with secure authentication, user identity, profile management, developer access, and service-purchase infrastructure.

## License

This project includes a `LICENSE` file. Review it before public or commercial distribution.

---

Built by DTing as the main authentication and service-access server for the company ecosystem.
