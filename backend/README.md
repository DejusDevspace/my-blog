# d3jusdevspace — Backend

FastAPI backend for my personal AI-powered blog and knowledge hub. Handles content management, admin auth, and public APIs for posts, categories, tags, and comments.

## Tech Stack

| Technology            | Purpose                                                  |
| --------------------- | -------------------------------------------------------- |
| **FastAPI**           | Async API framework                                      |
| **SQLAlchemy 2.0**    | Async ORM (`Mapped`, `mapped_column`, `DeclarativeBase`) |
| **Alembic**           | Database migrations                                      |
| **PostgreSQL + Neon** | Managed Postgres with pgvector support                   |
| **PyJWT**             | JWT decoding for NextAuth.js admin auth                  |
| **Pydantic v2**       | Request/response validation and settings                 |
| **uv**                | Python package manager                                   |

## Architecture

The backend follows a **layered architecture** — routers handle HTTP, services contain business logic, and models define the schema. Auth is enforced via FastAPI dependencies.

```
Request → Router → Service → Model/DB
                      ↑
                  Auth Dependency (admin routes only)
```

- **Routers** — thin HTTP handlers, no business logic
- **Services** — slug generation, reading time calculation, spam filtering, status transitions
- **Models** — SQLAlchemy 2.0 ORM with async support
- **Schemas** — separate Pydantic models for create/update/response per resource

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Public (no auth)

| Method | Path                     | Description                                             |
| ------ | ------------------------ | ------------------------------------------------------- |
| `GET`  | `/posts`                 | Paginated published posts (filter by `category`, `tag`) |
| `GET`  | `/posts/{slug}`          | Single published post                                   |
| `POST` | `/comments`              | Submit a comment (rate limited, honeypot protected)     |
| `GET`  | `/posts/{slug}/comments` | Approved comments for a post                            |

### Admin (JWT required)

| Method   | Path                     | Description                                 |
| -------- | ------------------------ | ------------------------------------------- |
| `GET`    | `/admin/posts`           | All posts, all statuses                     |
| `POST`   | `/admin/posts`           | Create post                                 |
| `PATCH`  | `/admin/posts/{id}`      | Update post                                 |
| `DELETE` | `/admin/posts/{id}`      | Soft delete post                            |
| `GET`    | `/admin/categories`      | List categories                             |
| `POST`   | `/admin/categories`      | Create category                             |
| `PATCH`  | `/admin/categories/{id}` | Update category                             |
| `DELETE` | `/admin/categories/{id}` | Delete category (blocked if posts assigned) |
| `DELETE` | `/admin/comments/{id}`   | Delete comment                              |

### Utility

| Method | Path      | Description  |
| ------ | --------- | ------------ |
| `GET`  | `/health` | Health check |

## Prerequisites

- **Python 3.14+**
- **[uv](https://docs.astral.sh/uv/)** — Python package manager
- **PostgreSQL** — [Neon](https://neon.tech) (recommended) or local instance

## Setup

**1. Install dependencies**

```bash
cd backend
uv sync
```

**2. Configure environment**

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname
NEXTAUTH_SECRET=your-secret-here
```

> Generate a secret with: `openssl rand -base64 32`

**3. Run migrations**

```bash
uv run alembic upgrade head
```

**4. Seed the admin owner**

```bash
uv run python scripts/seed_owner.py
```

## Running

```bash
uv run uvicorn main:app --reload
```

- **Swagger UI** — [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** — [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health check** — [http://localhost:8000/health](http://localhost:8000/health)

## Admin Auth

Admin endpoints are protected by JWT tokens issued by NextAuth.js on the frontend. The backend validates them using the shared `NEXTAUTH_SECRET` (HS256).

**Testing without a frontend:**

```bash
uv run python scripts/generate_token.py
```

This outputs a valid JWT you can use with curl or the Swagger UI "Authorize" button:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/admin/categories
```

## Project Structure

```
backend/
├── main.py                             # FastAPI app, CORS, router registration
├── alembic.ini                         # Alembic config
├── pyproject.toml                      # Dependencies (managed by uv)
├── .env.example                        # Required environment variables
├── scripts/
│   ├── generate_token.py               # Generate test JWTs
│   └── seed_owner.py                   # Seed admin owner row
└── app/
    ├── config.py                       # Pydantic Settings (loads from .env)
    ├── auth/
    │   └── deps.py                     # get_current_admin JWT dependency
    ├── db/
    │   ├── base.py                     # Async engine, session factory, Base class
    │   └── migrations/                 # Alembic migrations
    ├── models/                         # SQLAlchemy ORM models
    │   ├── owner.py                    # owners table
    │   ├── category.py                 # categories table
    │   ├── post.py                     # posts, tags, post_tags tables
    │   ├── comment.py                  # comments table
    │   ├── user_context.py             # user_context table
    │   └── agent.py                    # agent_runs, agent_schedule, embeddings, feedback
    ├── schemas/                        # Pydantic request/response models
    │   ├── common.py                   # PaginatedResponse[T], MessageResponse
    │   ├── post.py                     # PostCreate, PostUpdate, PostResponse
    │   ├── category.py                 # CategoryCreate, CategoryUpdate, CategoryResponse
    │   ├── tag.py                      # TagCreate, TagResponse
    │   └── comment.py                  # CommentCreate, CommentResponse
    ├── services/                       # Business logic
    │   ├── post_service.py             # CRUD, auto-slug, excerpt, reading time
    │   ├── category_service.py         # CRUD, deletion protection
    │   ├── tag_service.py              # Get-or-create pattern
    │   └── comment_service.py          # Spam filtering, post validation
    ├── routers/                        # API route handlers
    │   ├── public_posts.py             # GET /posts, GET /posts/{slug}
    │   ├── public_comments.py          # POST /comments, GET /posts/{slug}/comments
    │   ├── admin_posts.py              # Admin post CRUD
    │   ├── admin_categories.py         # Admin category CRUD
    │   └── admin_comments.py           # Admin comment deletion
    └── middleware/
        └── rate_limit.py               # IP-based rate limiting (3 comments/hr)
```

## Database

12 tables total — 7 active in Phase 1, 5 reserved for future phases (agents, embeddings, feedback).

**Generating a new migration after model changes:**

```bash
uv run alembic revision --autogenerate -m "describe your change"
uv run alembic upgrade head
```
