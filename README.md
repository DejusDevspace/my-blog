# d3jusdevspace

My personal AI-powered blog and knowledge hub. A full-stack application featuring a Next.js frontend and a FastAPI backend.

## Project Structure

This repository is organized as a monorepo containing two main parts:

- **[`/frontend`](./frontend/)**: Next.js 16 application with Tailwind CSS v4, React Query, and BlockNote. It serves both the public-facing blog and the admin CMS dashboard.
- **[`/backend`](./backend/)**: FastAPI application with SQLAlchemy 2.0 and PostgreSQL (Neon), providing REST APIs for content management, taxonomy, search, agent infrastructure, and Cloudinary image uploads.

## Key Features

- **Hybrid Search** — Semantic (pgvector cosine similarity) combined with PostgreSQL full-text search, ranked and merged with aggregated scoring. Highlighted snippets with `<mark>` tags.
- **Rich Markdown Editing** — Block-based editor (BlockNote) with seamless Cloudinary image uploads and code block support.
- **Taxonomy & Series Management** — Group posts by categories, tags, and series with full CRUD.
- **Admin Authentication** — JWT-based authentication via NextAuth.js.
- **Admin Settings** — Manage user context (bio, interests, learning focus, lifestyle) to personalize AI agent behavior.
- **Agent Infrastructure** — Pre-built database models and scaffolding for agentic content generation (post embeddings, agent runs, scheduling, feedback loops).
- **Cyber-Luxury Aesthetic** — Custom design tokens, dark mode default, and smooth transitions.

## Getting Started

To run the project locally, you will need to set up both the backend and frontend.

### 1. Backend Setup

See the [Backend README](./backend/README.md) for detailed instructions.

```bash
cd backend
uv sync
cp .env.example .env
# Configure your .env variables (Database, NextAuth, Cloudinary)
uv run alembic upgrade head
uv run python scripts/seed_owner.py
uv run uvicorn main:app --reload
```

### 2. Frontend Setup

See the [Frontend README](./frontend/README.md) for detailed instructions.

```bash
cd frontend
npm install
cp .env.example .env.local
# Configure your .env.local variables
npm run dev
```

Both servers must be running for the application to function correctly, as the frontend proxies API requests to the backend.
