# d3jusdevspace — Backend

FastAPI backend for my personal AI-powered blog and knowledge hub. Handles content management, admin auth, hybrid search, agent infrastructure, and public APIs.

## Tech Stack

| Technology            | Purpose                                                  |
| --------------------- | -------------------------------------------------------- |
| **FastAPI**           | Async API framework                                      |
| **SQLAlchemy 2.0**    | Async ORM (`Mapped`, `mapped_column`, `DeclarativeBase`) |
| **Alembic**           | Database migrations                                      |
| **PostgreSQL + Neon** | Managed Postgres with pgvector support                   |
| **pgvector**          | 384-dim cosine similarity for semantic search            |
| **sentence-transformers** | All-MiniLM-L6-v2 model for on-the-fly embedding     |
| **PyJWT**             | JWT decoding for NextAuth.js admin auth                  |
| **Pydantic v2**       | Request/response validation and settings                 |
| **uv**                | Python package manager                                   |
| **Cloudinary**        | Image hosting for blog posts                             |

## Architecture

The backend follows a **layered architecture** — routers handle HTTP, services contain business logic, and models define the schema. Auth is enforced via FastAPI dependencies.

```
Request → Router → Service → Model/DB
                      ↑
                  Auth Dependency (admin routes only)
```

- **Routers** — thin HTTP handlers, no business logic
- **Services** — slug generation, reading time calculation, spam filtering, status transitions, embedding generation, hybrid search
- **Models** — SQLAlchemy 2.0 ORM with async support
- **Schemas** — separate Pydantic models for create/update/response per resource

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Public (no auth)

| Method | Path                       | Description                                              |
| ------ | -------------------------- | -------------------------------------------------------- |
| `GET`  | `/posts`                   | Paginated published posts (filter by `category`, `tag`, `series`) |
| `GET`  | `/posts/{slug}`            | Single published post                                    |
| `POST` | `/comments`                | Submit a comment (rate limited, honeypot protected)      |
| `GET`  | `/posts/{slug}/comments`   | Approved comments for a post                             |
| `GET`  | `/search/semantic`         | Hybrid search (vector + FTS) with aggregated scoring     |
| `GET`  | `/debug`                   | Diagnostic stats (post count, FTS, embeddings)           |

### Admin (JWT required)

| Method   | Path                       | Description                                 |
| -------- | -------------------------- | ------------------------------------------- |
| `GET`    | `/admin/posts`             | All posts, all statuses                     |
| `POST`   | `/admin/posts`             | Create post (triggers background embedding) |
| `PATCH`  | `/admin/posts/{id}`        | Update post                                 |
| `DELETE` | `/admin/posts/{id}`        | Soft delete post                            |
| `GET`    | `/admin/categories`        | List categories                             |
| `POST`   | `/admin/categories`        | Create category                             |
| `PATCH`  | `/admin/categories/{id}`   | Update category                             |
| `DELETE` | `/admin/categories/{id}`   | Delete category (blocked if posts assigned) |
| `DELETE` | `/admin/comments/{id}`     | Delete comment                              |
| `GET`    | `/admin/context`           | Get current user context                    |
| `PUT`    | `/admin/context`           | Upsert user context                         |

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
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
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

**5. (Optional) Backfill embeddings for existing posts**

```bash
uv run python scripts/backfill_embeddings.py
```

**6. (Optional) Backfill FTS vector for existing posts**

```bash
uv run python scripts/backfill_fts.py
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
│   ├── seed_owner.py                   # Seed admin owner row
│   ├── backfill_embeddings.py          # Generate embeddings for existing posts
│   └── backfill_fts.py                 # Populate search_vector for existing posts
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
    │   └── agent.py                    # agent_runs, agent_schedule, post/context embeddings, feedback
    ├── schemas/                        # Pydantic request/response models
    │   ├── common.py                   # PaginatedResponse[T], MessageResponse
    │   ├── post.py                     # PostCreate, PostUpdate, PostResponse
    │   ├── category.py                 # CategoryCreate, CategoryUpdate, CategoryResponse
    │   ├── tag.py                      # TagCreate, TagResponse
    │   ├── comment.py                  # CommentCreate, CommentResponse
    │   ├── search.py                   # SearchResult with aggregated scoring + snippets
    │   └── user_context.py             # UserContextCreate, UserContextUpdate, UserContextResponse
    ├── services/                       # Business logic
    │   ├── post_service.py             # CRUD, auto-slug, excerpt, reading time
    │   ├── category_service.py         # CRUD, deletion protection
    │   ├── tag_service.py              # Get-or-create pattern
    │   ├── comment_service.py          # Spam filtering, post validation
    │   ├── embedding_service.py        # Post/context chunking, vector generation, storage
    │   ├── search_service.py           # Hybrid search (vector cosine + FTS), merge, aggregation
    │   └── user_context_service.py     # Get/upsert user context
    ├── routers/                        # API route handlers
    │   ├── public_posts.py             # GET /posts, GET /posts/{slug}
    │   ├── public_comments.py          # POST /comments, GET /posts/{slug}/comments
    │   ├── public_search.py            # GET /search/semantic
    │   ├── debug.py                    # GET /debug diagnostics
    │   ├── admin_posts.py              # Admin post CRUD
    │   ├── admin_categories.py         # Admin category CRUD
    │   ├── admin_uploads.py            # Admin Cloudinary uploads
    │   ├── admin_comments.py           # Admin comment deletion
    │   └── admin_context.py            # Admin context get/upsert
    └── middleware/
        └── rate_limit.py               # IP-based rate limiting (3 comments/hr)
```

## Database

The database has the following tables:

- **Active**: `owners`, `posts`, `categories`, `tags`, `post_tags`, `series`, `comments`, `user_context`, `post_embeddings`
- **Infrastructure**: `post_embeddings` (pgvector), `search_vector` column on `posts` (FTS)
- **Reserved (future)**: `context_embeddings`, `agent_runs`, `agent_schedule`, `post_feedback`

**Generating a new migration after model changes:**

```bash
uv run alembic revision --autogenerate -m "describe your change"
uv run alembic upgrade head
```
