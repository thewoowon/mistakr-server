# MovieAndMe Backend Server

FastAPI backend server for the MovieAndMe React Native mobile application.

## Features

- 🔐 Google OAuth authentication
- 🎫 JWT-based access & refresh token management
- 👤 User profile management
- 📱 Mobile-optimized API responses

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy (async)
- **Authentication**: JWT + Google OAuth
- **Python**: 3.11+

## Setup

### 1. Install Dependencies

```bash
poetry install
```

Or with pip:
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `JWT_SECRET_KEY`: Your secret key for JWT token generation
- `JWT_ALGORITHM`: HS256 (recommended)
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret

### 3. Initialize Database

```bash
# Create database tables
python -c "from app.db.session import sync_engine; from app.db.base import Base; from app.models import User, Token; Base.metadata.create_all(bind=sync_engine)"
```

### 4. Run Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation available at:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

## API Endpoints

### Authentication

#### Google Login
```http
POST /api/v1/auth/google
Content-Type: application/json

{
  "id_token": "google_id_token_here",
  "is_selected": true
}
```

**Response Headers:**
- `Authorization: Bearer {access_token}`
- `RefreshToken: RefreshToken {refresh_token}`

**Response Body:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "profile_pic": "https://...",
    "provider": "google"
  }
}
```

#### Refresh Token
```http
POST /api/v1/auth/token/reissue
Content-Type: application/json

{
  "refreshToken": "your_refresh_token"
}
```

**Response Headers:**
- `Authorization: Bearer {new_access_token}`
- `RefreshToken: RefreshToken {new_refresh_token}`

#### Logout
```http
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

### User

#### Get Current User
```http
GET /api/v1/users/me
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "profile_pic": "https://...",
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00",
  "provider": "google"
}
```

## Project Structure

```
MovieAndMe-server/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py       # Authentication endpoints
│   │       │   └── user.py       # User endpoints
│   │       └── api.py            # API router aggregation
│   ├── core/
│   │   ├── config.py             # Configuration settings
│   │   └── security.py           # JWT token handling
│   ├── db/
│   │   ├── base.py               # SQLAlchemy base
│   │   └── session.py            # Database session management
│   ├── models/
│   │   ├── user.py               # User model
│   │   └── token.py              # Token model
│   ├── schemas/
│   │   └── user.py               # Pydantic schemas
│   ├── services/
│   │   ├── auth_service.py       # Authentication business logic
│   │   └── user_service.py       # User business logic
│   ├── dependencies.py           # FastAPI dependencies
│   └── main.py                   # FastAPI app initialization
├── .env.example                  # Environment variables template
├── pyproject.toml                # Poetry dependencies
└── settings.py                   # Global settings

```

## Token Management

### Access Token
- **Lifespan**: 30 minutes
- **Usage**: Include in `Authorization: Bearer {token}` header for all authenticated requests
- **Payload**: `{"sub": "user@email.com", "user_id": 1, "exp": timestamp}`

### Refresh Token
- **Lifespan**: 7 days
- **Storage**: Database with `is_active` flag
- **Usage**: Send to `/api/v1/auth/token/reissue` to get new access token
- **Rotation**: New refresh token issued on each refresh

## Error Codes

The API returns structured error responses compatible with the React Native app:

### JWT_VERIFY_EXPIRED
```json
{
  "code": "JWT_VERIFY_EXPIRED",
  "message": "인증정보가 만료 됐습니다.",
  "name": "TokenExpiredException"
}
```

### JWT_VALIDATE_ERROR
```json
{
  "code": "JWT_VALIDATE_ERROR",
  "message": "인증정보가 유효하지 않습니다.",
  "name": "TokenValidationException"
}
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
```

### Linting
```bash
flake8 app/
```

## Deployment

### Docker
```bash
docker build -t movieandme-server .
docker run -p 8000:8000 movieandme-server
```

### Environment
Make sure to set production-ready values in `.env`:
- Use a strong `JWT_SECRET_KEY`
- Set `DEBUG=False`
- Configure proper CORS origins in `app/main.py`

## License

MIT
