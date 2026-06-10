# d3jusdevspace

My personal AI-powered blog and knowledge hub. A full-stack application featuring a Next.js frontend and a FastAPI backend.

## Project Structure

This repository is organized as a monorepo containing two main parts:

- **[`/frontend`](./frontend/)**: Next.js 17 application with Tailwind CSS v4, React Query, and BlockNote. It serves both the public-facing blog and the admin CMS dashboard, including agent settings, run log, and draft review pages.
- **[`/backend`](./backend/)**: FastAPI application with SQLAlchemy 2.0 and PostgreSQL (Neon), providing REST APIs for content management, taxonomy, search, an autonomous AI agent pipeline (LangGraph), and Cloudinary image uploads.

## Key Features

- **Hybrid Search** — Semantic (pgvector cosine similarity) combined with PostgreSQL full-text search, ranked and merged with aggregated scoring. Highlighted snippets with `<mark>` tags.
- **Rich Markdown Editing** — Block-based editor (BlockNote) with seamless Cloudinary image uploads and code block support.
- **Taxonomy & Series Management** — Group posts by categories, tags, and series with full CRUD.
- **Admin Authentication** — JWT-based authentication via NextAuth.js.
- **AI Agent Pipeline** — 5-node LangGraph pipeline that autonomously generates blog post drafts: topic selection via Groq LLM, web research (Tavily), semantic context retrieval (pgvector), writing tone analysis from published corpus, and markdown draft generation — all instrumented end-to-end with LangFuse observability.
- **APScheduler Cron Scheduling** — Schedule automatic agent runs with configurable cron expressions (daily, weekly, bi-weekly, or custom).
- **Agent Settings & Run Log** — Admin UI for schedule management, manual pipeline triggers, and full run history with status, duration, and LangFuse trace links.
- **Agent Draft Review** — Review, edit, publish, or delete agent-generated drafts from a dedicated admin page.
- **Context Embeddings** — User context (bio, interests, learning focus) is automatically embedded and stored in pgvector for semantically relevant topic selection.
- **Cyber-Luxury Aesthetic** — Custom design tokens, dark mode default, and smooth transitions.

## Getting Started

To run the project locally, you will need to set up both the backend and frontend.

### 1. Backend Setup

See the [Backend README](./backend/README.md) for detailed instructions.

```bash
cd backend
uv sync
cp .env.example .env
# Configure your .env variables (Database, NextAuth, Cloudinary, Groq, Tavily, LangFuse)
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

## Agent Pipeline Environment Variables

The agent pipeline requires the following additional environment variables in `backend/.env`:

| Variable              | Required | Default                      | Description                                            |
| --------------------- | -------- | ---------------------------- | ------------------------------------------------------ |
| `GROQ_API_KEY`        | Yes      | —                            | API key for Groq LLM (llama-3.3-70b-versatile)         |
| `TAVILY_API_KEY`      | No       | —                            | API key for Tavily web search (skipped if empty)       |
| `LANGFUSE_PUBLIC_KEY` | No       | —                            | LangFuse public key for observability (no-op if empty) |
| `LANGFUSE_SECRET_KEY` | No       | —                            | LangFuse secret key                                    |
| `LANGFUSE_HOST`       | No       | `https://cloud.langfuse.com` | LangFuse host URL                                      |

The pipeline runs without Tavily or LangFuse keys — research is skipped and tracing is a no-op. Only `GROQ_API_KEY` is required.
