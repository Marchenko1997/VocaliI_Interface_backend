# Vocali Backend

REST API for the Vocali audio platform -- handles user authentication, audio file management, and Spotify track search. Built with FastAPI and PostgreSQL.

## Features

- **Authentication** -- signup, signin, logout, JWT access/refresh tokens
- **Email verification** -- 6-digit confirmation codes with 10-minute expiry via Brevo (Sendinblue)
- **Password reset** -- forgot/confirm password flow with email codes
- **Audio management** -- upload, list (paginated), delete audio files per user
- **Spotify integration** -- search tracks via Spotify Web API (client credentials)
- **AI playlist generation** -- natural language prompt to curated Spotify track list via OpenRouter
- **Async everywhere** -- async database access with SQLAlchemy + asyncpg

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Language | Python 3.12+ |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2 (async) |
| Migrations | Alembic |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Validation | Pydantic v2 |
| Email | Brevo API (sib-api-v3-sdk) + Jinja2 templates |
| Spotify | httpx (async HTTP client) |
| AI | OpenRouter API (openai/gpt-oss-120b) |
| Containerization | Docker + Docker Compose |

## Project Structure

```
vocali_backend/
  main.py              # FastAPI app, middleware, router registration
  models.py            # SQLAlchemy models (User, AudioFile)
  schemas.py           # Pydantic request/response schemas
  database.py          # Async engine and session factory
  auth_utils.py        # Password hashing, JWT creation, user helpers
  security.py          # HTTPBearer dependency
  routes/
    auth.py            # Auth endpoints (signup, signin, confirm, reset)
    audio.py           # Audio file endpoints (upload, list, delete)
    spotify.py         # Spotify search endpoint
    ai.py              # AI playlist generation endpoint
  services/
    email_service.py   # Brevo transactional email sender
    spotify_serv.py    # Spotify token caching and track search
    ai_service.py      # OpenRouter AI intent parsing
  templates/
    confirmation.html  # Email verification template
    reset_password.html# Password reset template
alembic/               # Database migration scripts
Dockerfile             # Python 3.12-slim container
docker.compose.yaml    # Backend + PostgreSQL services
```

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 16
- [Poetry](https://python-poetry.org/) (or [uv](https://docs.astral.sh/uv/))

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd VocaliI_Interface_backend
poetry install
```

### 2. Configure environment variables

Copy the example and fill in your values:

```bash
cp .env.example .env
```

### 3. Run database migrations

```bash
alembic upgrade head
```

### 4. Start the server

```bash
poetry run uvicorn vocali_backend.main:app --reload
```

The API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Docker

```bash
docker compose -f docker.compose.yaml up --build
```

This starts the backend on port `8000` and PostgreSQL on the default port.

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (async, e.g. `postgresql+asyncpg://user:pass@host/db`) |
| `SECRET_KEY` | JWT signing secret |
| `ALGORITHM` | JWT algorithm (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL in minutes (default: `15`) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL in days (default: `7`) |
| `BREVO_API_KEY` | Brevo (Sendinblue) API key for transactional emails |
| `BREVO_SENDER_EMAIL` | Sender email address for outgoing emails |
| `SPOTIFY_CLIENT_ID` | Spotify app client ID |
| `SPOTIFY_CLIENT_SECRET` | Spotify app client secret |
| `OPENROUTER_API_KEY` | OpenRouter API key for AI playlist generation |

## API Endpoints

### Auth (`/auth`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/signup` | Register a new user |
| POST | `/auth/signin` | Sign in, returns JWT tokens |
| POST | `/auth/confirm-signup` | Verify email with 6-digit code |
| POST | `/auth/resend-confirmation-code` | Resend verification code |
| POST | `/auth/forgot-password` | Request password reset code |
| POST | `/auth/confirm-forgot-password` | Reset password with code |
| POST | `/auth/logout` | Logout (bearer token required) |
| GET | `/auth/me` | Get current user profile |

### Audio (`/audio`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/audio/upload` | Upload an audio file |
| GET | `/audio/files` | List user's audio files (paginated) |
| DELETE | `/audio/files` | Delete an audio file by `fileKey` |

### Spotify (`/spotify`)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/spotify/search` | Search Spotify tracks by query |

### AI Playlist (`/ai`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ai/playlist` | Generate a playlist from a natural language prompt |

Accepts `{ "prompt": "2 hours of chill lo-fi beats" }` (bearer token required). The request flows through two services:

1. **`ai_service.py`** -- sends the prompt to OpenRouter (`openai/gpt-oss-120b`) which extracts `genre`, `bpm_hint`, `duration_minutes`, `tracks_needed`, and a `search_query`. The AI response is parsed as JSON.
2. **`spotify_serv.py`** -- uses the extracted `search_query` to fetch tracks from Spotify in batches (token caching with auto-refresh, graceful handling of 401 and empty responses).

Returns `{ "ai_params": { ... }, "tracks": [ ... ] }` with the requested number of tracks.
