"""d3jusdevspace — FastAPI application entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.base import engine
from app.routers import (
    admin_categories,
    admin_comments,
    admin_context,
    admin_posts,
    admin_series,
    admin_tags,
    admin_uploads,
    debug,
    public_comments,
    public_posts,
    public_search,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Manage application startup and shutdown.

    - Startup: verify database connectivity.
    - Shutdown: dispose of the connection pool cleanly.
    """
    # Startup — verify the database is reachable.
    async with engine.connect() as conn:
        await conn.execute(
            __import__("sqlalchemy").text("SELECT 1")
        )
    yield
    # Shutdown — close all pooled connections.
    await engine.dispose()


app = FastAPI(
    title="d3jusdevspace API",
    description="Personal AI knowledge hub and blog backend.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers — all prefixed under /api/v1
# ---------------------------------------------------------------------------

API_V1 = "/api/v1"

app.include_router(public_posts.router, prefix=API_V1)
app.include_router(public_comments.router, prefix=API_V1)
app.include_router(public_search.router, prefix=API_V1)
app.include_router(admin_posts.router, prefix=API_V1)
app.include_router(admin_categories.router, prefix=API_V1)
app.include_router(admin_series.router, prefix=API_V1)
app.include_router(admin_tags.router, prefix=API_V1)
app.include_router(admin_uploads.router, prefix=API_V1)
app.include_router(admin_comments.router, prefix=API_V1)
app.include_router(admin_context.router, prefix=API_V1)
app.include_router(debug.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}
