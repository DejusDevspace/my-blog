# Product Requirements Document
## d3jusdevspace — Personal AI Knowledge Hub with Multi-Agent Content System

**Version:** 2.0  
**Status:** Draft  
**Author:** Consultation output — Senior Engineering Review  
**Date:** April 2026  
**Previous version:** PRD v1.0

---

## Changelog (v1 → v2)

| # | Change | Reason |
|---|--------|--------|
| 1 | SaaS/multi-tenant UI removed from all sections | Not a v1 goal; focus is personal use and portfolio |
| 2 | `owner_id` retained silently in schema | Zero-cost future-proofing; no logic or UI required |
| 3 | Langfuse scoped to Phase 3 with defined trace targets | Prevents ambiguity during agent development |
| 4 | BlockNote output format locked to markdown | Day-one schema decision; must align with agent output format |
| 5 | Embedding model explicitly named (text-embedding-3-small, 1536d) | Required before pgvector column can be defined |
| 6 | Diff visualisation scoped to Phase 4 | Depends on post_feedback table; prevents premature build |
| 7 | OpenAI as sole LLM provider | Reduces complexity; single API key, single SDK |
| 8 | Portfolio value section added | Explicit articulation of what this project demonstrates |

---

## Table of Contents

1. [Purpose & Philosophy](#1-purpose--philosophy)
2. [Goals & Success Metrics](#2-goals--success-metrics)
3. [Users & Roles](#3-users--roles)
4. [System Architecture Summary](#4-system-architecture-summary)
5. [Repository Structure](#5-repository-structure)
6. [Feature Specifications](#6-feature-specifications)
7. [Data Models](#7-data-models)
8. [API Contracts](#8-api-contracts)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Tech Stack](#10-tech-stack)
11. [Observability & Metrics](#11-observability--metrics)
12. [Development Phases & Timeline](#12-development-phases--timeline)
13. [Portfolio Value](#13-portfolio-value)
14. [Non-Goals (v1)](#14-non-goals-v1)
15. [Open Questions](#15-open-questions)

---

## 1. Purpose & Philosophy

**d3jusdevspace** is a personal knowledge hub and AI-powered content engine designed for a single author. It enables both manual writing and semi-autonomous AI-generated content that is aligned with the author's interests, tone, and writing style.

### Core Philosophy

- **Human-in-the-loop AI system** — AI generates drafts; the human approves and refines. Nothing publishes without author sign-off.
- **Built for real usage, not just demonstration** — the system must be something the author actively wants to use daily, not a demo that sits idle.
- **System improves over time** — author feedback on AI drafts is captured and fed back into the agent pipeline to improve alignment over time.
- **Explainability and portfolio value** — architecture decisions are deliberate and defensible; the codebase should be readable as a portfolio artifact.
- **Controlled complexity** — no over-engineering. The agent system is constrained to 3–4 nodes maximum. Every added component must earn its place.

### Primary Goals

1. A personal publishing space for technical documentation, project showcases, thoughts, and how-to articles.
2. A strong portfolio artifact demonstrating full-stack AI engineering across frontend, backend, and agent/ML layers.

---

## 2. Goals & Success Metrics

### Success Metrics (v1)

| Metric | Target |
|--------|--------|
| Agent draft quality | Fewer than 2 manual edits on average before approval |
| Semantic search latency | Results returned in under 500ms (p95) |
| Page load performance | Blog post LCP under 1.5s on standard broadband |
| Admin usability | Author can publish a post without touching any code |
| Agent alignment over time | Measurable reduction in edits-per-post across Phase 4 feedback cycles |
| Codebase quality | Clean, maintainable, well-documented — readable as a portfolio artifact |

---

## 3. Users & Roles

### v1 Roles

**Owner / Admin (author)**
- Full access to admin panel
- Can create, edit, publish, unpublish, and delete posts
- Can manage categories and tags
- Can configure and trigger the AI agent pipeline
- Can approve, edit, or reject agent-generated drafts
- Can update personal context (bio, interests, tone notes)
- Can delete comments

**Public Reader (unauthenticated)**
- Can browse and read all published posts
- Can filter by category and tag
- Can use global semantic search
- Can submit comments (anonymous or named)
- Cannot access any admin routes

> Note: `owner_id` is present on all relevant database tables as a single-column future-proofing measure. No multi-user UI, auth, or logic is built in v1. This column costs nothing now and avoids a painful schema migration if the project ever expands.

---

## 4. System Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│                 Next.js 14 (App Router)                  │
│  Public Blog │ Admin Panel │ Search UI │ Auth            │
└──────────────────────┬──────────────────────────────────┘
                       │ REST / SSE
┌──────────────────────▼──────────────────────────────────┐
│                    FastAPI (Python)                       │
│  Posts API │ Search API │ Agent API │ Context API        │
└────┬───────────────────────────────────────┬────────────┘
     │                                       │
┌────▼──────────────────┐   ┌───────────────▼────────────┐
│   LangGraph Agents     │   │       Data Layer            │
│  Orchestrator          │   │  PostgreSQL + pgvector      │
│  Research Agent        │◄──►  Posts, context, feedback  │
│  Tone/Feedback Agent   │   │  Embeddings (pgvector)      │
│  Writer Agent          │   └────────────────────────────┘
│  APScheduler           │
└───────────┬────────────┘
            │
┌───────────▼────────────────────────────────────────────┐
│              External Services                          │
│  OpenAI (LLM + Embeddings) │ Tavily Search             │
│  Cloudinary (Images) │ Resend (Email) │ Langfuse        │
└────────────────────────────────────────────────────────┘
```

**Deployment targets:**
- Frontend: Vercel
- Backend (FastAPI): Railway or Render
- Database: Supabase or Neon (managed Postgres + pgvector)
- Images: Cloudinary (free tier)
- Tracing: Langfuse (cloud, free tier)

---

## 5. Repository Structure

Single monorepo managed with **Turborepo**.

```
d3jusdevspace/
├── apps/
│   ├── web/                    # Next.js 14 frontend
│   │   ├── app/
│   │   │   ├── (public)/       # Blog feed, post detail, search
│   │   │   └── admin/          # Admin panel (auth-gated)
│   │   ├── components/
│   │   ├── lib/
│   │   └── ...
│   └── api/                    # FastAPI backend
│       ├── routers/            # posts, search, agent, context, comments
│       ├── agents/             # LangGraph graph definitions
│       │   ├── graph.py
│       │   ├── nodes/          # orchestrator, research, tone, writer
│       │   └── tools/          # tavily, pgvector queries
│       ├── models/             # SQLAlchemy ORM models
│       ├── schemas/            # Pydantic request/response schemas
│       ├── services/           # Business logic layer
│       └── ...
├── packages/
│   ├── types/                  # Shared TypeScript types
│   ├── ui/                     # Shared design system components
│   └── config/                 # Shared ESLint, Tailwind, TS configs
├── turbo.json
├── package.json
└── README.md
```

---

## 6. Feature Specifications

### 6.1 Public Blog (Reader-facing)

#### 6.1.1 Home / Feed Page

- Paginated list of published posts, sorted by `published_at` descending
- Each post card shows: title, excerpt (first 160 chars), category badge, tags, author label (Human or Agent), reading time estimate, published date
- Agent-authored posts display a distinct "✦ Agent" badge
- Filter bar for category and tag — URL-param driven for shareability
- No authentication required

#### 6.1.2 Post Detail Page

- Full markdown content rendered with `react-markdown` + `rehype-highlight` + `remark-gfm`
- Sticky right-side Table of Contents sidebar from `##` and `###` headings, with active section highlighting via `IntersectionObserver`
- TOC collapses into a floating drawer on mobile
- Reading progress bar at top of viewport
- Post metadata: published date, reading time, category, tags, author type badge
- Previous / Next post navigation at bottom
- Comments section below content

#### 6.1.3 Content Categories

| Category | Description |
|----------|-------------|
| `projects` | Builds, side projects, case studies |
| `thoughts` | Opinions, reflections, personal notes |
| `blog` | How-tos, technical breakdowns, knowledge sharing |
| `docs` | Technical documentation, references |

Tags are free-form and many-to-many.

#### 6.1.4 Global Semantic Search

- Persistent search bar in navigation header
- Natural language queries (e.g. "posts about building agents with LangGraph")
- FastAPI `/search` endpoint performs pgvector cosine similarity against post embeddings
- Results with similarity below 0.65 threshold are discarded
- Falls back to PostgreSQL full-text search (`tsvector`) if fewer than 3 semantic results qualify
- Frontend debounces input at 300ms before firing request

#### 6.1.5 Light / Dark Mode

- Toggle in navigation header, persisted to `localStorage`
- System preference respected on first visit via `next-themes`

---

### 6.2 Admin Panel

All admin routes are protected behind NextAuth.js. Single admin account provisioned via environment variable credentials. No public sign-up.

#### 6.2.1 Posts Management

- Table of all posts (all statuses) with status badges, last modified date, and quick actions
- Statuses: `draft`, `published`, `archived`, `agent_draft`
- New post / Edit post opens BlockNote editor
- Publish / Unpublish toggle without deletion
- Soft-delete (sets `deleted_at`); content is never permanently destroyed without explicit intent

#### 6.2.2 Rich Text Editor (BlockNote)

**Output format: Markdown.** BlockNote is configured to output clean markdown strings. This aligns human-written and agent-written content in a single, portable format stored in the `posts.content` TEXT column.

Supported block types:
- Headings (H1, H2, H3)
- Paragraph, blockquote, divider
- Bulleted list, numbered list
- Code block with language selector (Python, TypeScript, Bash, SQL, and others)
- Image (uploads to Cloudinary via backend pre-signed URL; markdown stores the CDN URL)
- Inline link, inline code

Additional behaviours:
- Slash command menu (`/`) for block insertion
- Autosave to `localStorage` every 30 seconds
- Manual "Save Draft" and "Publish" buttons in the editor toolbar

#### 6.2.3 Agent Draft Review

- Dedicated "Agent Drafts" tab in admin dashboard
- Each draft shows: title, full content preview, topic used, agent run metadata (timestamp, model, sources cited)
- Actions: **Approve & Publish**, **Approve as Draft** (move to regular drafts for editing), **Reject** (archive without publishing)
- `is_agent_authored: true` flag is permanent — preserved even if the author edits before approval
- Edit diffs between the original agent draft and the final approved content are captured and stored in `post_feedback` (see Section 6.5)

#### 6.2.4 Context Management

Admin settings page for the personal context fed to AI agents:

| Field | Description | Used by |
|-------|-------------|---------|
| Bio | Author background, profession, current focus (max 1000 chars) | Orchestrator, Writer |
| Interests | Tag-style list of topics (e.g. "LangGraph", "FastAPI", "career growth") | Orchestrator |
| Tone notes | Voice, humor style, things to avoid | Tone Agent |
| Writing samples | Text samples for style calibration | Context Agent |

On save, all fields are re-embedded using `text-embedding-3-small` and upserted into `context_embeddings`.

#### 6.2.5 Agent Configuration

- **Schedule:** Cron-style interval selector (e.g. every Monday at 9am). Saved to DB, loaded by APScheduler on startup.
- **Manual trigger:** "Run agent now" button with live log stream via Server-Sent Events (SSE).
- **Autonomy:** Locked to "Save as draft" in v1 — all agent output requires author approval before publishing.

#### 6.2.6 Observability Dashboard (Phase 4)

Lightweight internal metrics displayed in admin. See Section 11 for full detail.

---

### 6.3 AI Agent System

#### 6.3.1 LangGraph Workflow

The pipeline is a directed graph with typed `AgentState` passed between nodes. Maximum 4 nodes in v1.

**Orchestrator Node**
- Entry point for scheduled and manual runs
- Queries `user_context` interests list
- Queries pgvector for recent post topics to avoid repetition (last 30 days)
- Selects a topic: prioritises interests not covered recently; appends a trending angle via Tavily
- Passes topic + full author context to downstream nodes

**Research Agent Node**
- Runs 3–5 Tavily searches on the selected topic
- Summarises each source into structured findings (key points, relevance, URL)
- Deduplicates against previously cited sources in the DB

**Tone/Feedback Agent Node**
- Reads `post_feedback` for recent approval/rejection signals
- Reads tone notes and writing samples from `user_context`
- Reads semantically similar past posts via pgvector
- Produces a tone directive: specific instructions for the Writer Agent on voice, structure, and what to avoid
- Incorporates up to 5 recent feedback examples as few-shot guidance

**Writer Agent Node**
- Receives: topic, research findings, style context, tone directive
- Generates a full markdown blog post via OpenAI GPT-4o
- System prompt instructs the model to write as the author, not as an AI assistant
- Output: title, content (markdown), suggested tags, suggested category, sources list

**Review Router (final node)**
- Saves output as `status: agent_draft`, `is_agent_authored: true`
- Logs run to `agent_runs` table
- Sends email notification via Resend (configurable)

#### 6.3.2 Feedback & Learning Loop

| Event | Signal | What is stored |
|-------|--------|----------------|
| Approved, no edits | Positive | `rating: positive` |
| Approved, with edits | Mixed | `rating: mixed` + unified diff of changes |
| Rejected | Negative | `rating: negative` + optional rejection notes |

The Tone/Feedback Agent reads this history on each run and includes recent examples as few-shot prompt context. No fine-tuning is performed — the loop operates entirely at the prompt level.

#### 6.3.3 Embedding Pipeline

- All post content is embedded on save/publish using OpenAI `text-embedding-3-small` (1536 dimensions)
- Embeddings stored in `post_embeddings` (pgvector, `VECTOR(1536)`)
- User context fields embedded on save, stored in `context_embeddings`
- pgvector index type: `ivfflat` for approximate nearest-neighbour performance at scale

---

### 6.4 Semantic Search

- Query string is embedded using `text-embedding-3-small`
- pgvector cosine similarity: `ORDER BY embedding <=> query_embedding LIMIT 10`
- Results below 0.65 similarity threshold are discarded
- Fallback to PostgreSQL `tsvector` full-text search if fewer than 3 results qualify
- Response: post id, title, excerpt, category, tags, published_at (similarity score used for ranking only, not exposed to the reader)

---

### 6.5 Comments

**Schema fields:** `id`, `post_id`, `owner_id`, `display_name` (nullable = anonymous), `body` (plain text, max 1000 chars), `status`, `created_at`

**Spam filtering:**
- Honeypot hidden field — submissions that populate it are silently discarded
- Basic server-side keyword blocklist
- Rate limiting: max 3 comments per IP per hour (FastAPI middleware)
- Comments that pass checks are auto-approved and immediately visible

**Anonymous option:**
- Toggle on comment form — when on, `display_name` is null and displayed as "Anonymous"
- When off, a name field appears (required, max 50 chars)
- No email required; no reader accounts

---

### 6.6 Context Ingestion

Context is managed from the admin panel (Section 6.2.4) and stored in `user_context`. Agents pull from this table on every run.

---

## 7. Data Models

### `owners`
```sql
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
email         TEXT UNIQUE NOT NULL
created_at    TIMESTAMPTZ DEFAULT now()
```
*Single row seeded in v1. No sign-up UI. Present to make all queries owner-scoped without future schema rewrites.*

### `posts`
```sql
id                UUID PRIMARY KEY DEFAULT gen_random_uuid()
owner_id          UUID REFERENCES owners(id)
title             TEXT NOT NULL
slug              TEXT UNIQUE NOT NULL
content           TEXT NOT NULL              -- markdown string (BlockNote output)
excerpt           TEXT                       -- auto-generated, first 160 chars
category          TEXT NOT NULL
status            TEXT NOT NULL DEFAULT 'draft'
                  -- draft | published | archived | agent_draft
is_agent_authored BOOLEAN DEFAULT false
reading_time_mins INTEGER
published_at      TIMESTAMPTZ
deleted_at        TIMESTAMPTZ                -- soft delete
created_at        TIMESTAMPTZ DEFAULT now()
updated_at        TIMESTAMPTZ DEFAULT now()
```

### `tags`
```sql
id        UUID PRIMARY KEY DEFAULT gen_random_uuid()
owner_id  UUID REFERENCES owners(id)
name      TEXT NOT NULL
slug      TEXT NOT NULL
UNIQUE(owner_id, slug)
```

### `post_tags`
```sql
post_id  UUID REFERENCES posts(id) ON DELETE CASCADE
tag_id   UUID REFERENCES tags(id) ON DELETE CASCADE
PRIMARY KEY (post_id, tag_id)
```

### `post_embeddings`
```sql
id          UUID PRIMARY KEY DEFAULT gen_random_uuid()
post_id     UUID REFERENCES posts(id) ON DELETE CASCADE
embedding   VECTOR(1536)                   -- OpenAI text-embedding-3-small
created_at  TIMESTAMPTZ DEFAULT now()
```

### `comments`
```sql
id           UUID PRIMARY KEY DEFAULT gen_random_uuid()
post_id      UUID REFERENCES posts(id) ON DELETE CASCADE
owner_id     UUID REFERENCES owners(id)
display_name TEXT                           -- null = anonymous
body         TEXT NOT NULL
status       TEXT NOT NULL DEFAULT 'pending_spam_check'
             -- pending_spam_check | approved | spam
created_at   TIMESTAMPTZ DEFAULT now()
```

### `user_context`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
owner_id        UUID REFERENCES owners(id) UNIQUE
bio             TEXT
interests       JSONB DEFAULT '[]'          -- string array
tone_notes      TEXT
writing_samples JSONB DEFAULT '[]'          -- array of { label, content }
updated_at      TIMESTAMPTZ DEFAULT now()
```

### `context_embeddings`
```sql
id          UUID PRIMARY KEY DEFAULT gen_random_uuid()
owner_id    UUID REFERENCES owners(id)
field_key   TEXT                            -- bio | interests | tone_notes
embedding   VECTOR(1536)
updated_at  TIMESTAMPTZ DEFAULT now()
```

### `post_feedback`
```sql
id          UUID PRIMARY KEY DEFAULT gen_random_uuid()
post_id     UUID REFERENCES posts(id)
owner_id    UUID REFERENCES owners(id)
rating      TEXT NOT NULL                   -- positive | mixed | negative
edit_diff   TEXT                            -- unified diff (populated for mixed)
notes       TEXT                            -- optional rejection reason
created_at  TIMESTAMPTZ DEFAULT now()
```

### `agent_runs`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
owner_id        UUID REFERENCES owners(id)
topic           TEXT
model_used      TEXT
status          TEXT                        -- running | completed | failed
output_post_id  UUID REFERENCES posts(id)
run_log         JSONB                       -- node-by-node execution log
triggered_by    TEXT                        -- scheduler | manual
started_at      TIMESTAMPTZ DEFAULT now()
completed_at    TIMESTAMPTZ
```

### `agent_schedule`
```sql
id          UUID PRIMARY KEY DEFAULT gen_random_uuid()
owner_id    UUID REFERENCES owners(id) UNIQUE
cron_expr   TEXT NOT NULL DEFAULT '0 9 * * 1'  -- every Monday 9am
is_active   BOOLEAN DEFAULT true
updated_at  TIMESTAMPTZ DEFAULT now()
```

---

## 8. API Contracts

**Base URL:** `/api/v1`

### Public Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/posts` | List published posts. Params: `category`, `tag`, `page`, `limit` |
| GET | `/posts/{slug}` | Single published post by slug |
| GET | `/search?q={query}` | Semantic + fallback keyword search |
| POST | `/comments` | Submit comment on a post |
| GET | `/posts/{slug}/comments` | Approved comments for a post |

### Admin Endpoints (Auth required)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/posts` | All posts (all statuses) |
| POST | `/admin/posts` | Create post |
| PATCH | `/admin/posts/{id}` | Update post |
| DELETE | `/admin/posts/{id}` | Soft delete post |
| GET | `/admin/agent-drafts` | List agent_draft posts |
| POST | `/admin/agent-drafts/{id}/approve` | Approve draft |
| POST | `/admin/agent-drafts/{id}/reject` | Reject draft |
| GET | `/admin/context` | Get user context |
| PUT | `/admin/context` | Update context (triggers re-embedding) |
| GET | `/admin/agent/schedule` | Get agent schedule |
| PUT | `/admin/agent/schedule` | Update schedule |
| POST | `/admin/agent/run` | Trigger manual agent run |
| GET | `/admin/agent/runs` | Agent run history |
| GET | `/admin/agent/runs/{id}/log` | Stream run log via SSE |
| DELETE | `/admin/comments/{id}` | Delete comment |
| GET | `/admin/categories` | List categories |
| POST | `/admin/categories` | Create category |
| PATCH | `/admin/categories/{id}` | Rename category |
| DELETE | `/admin/categories/{id}` | Delete category |

---

## 9. Non-Functional Requirements

### Performance
- Blog post LCP < 1.5s on standard broadband
- Semantic search < 500ms (p95)
- Admin CRUD operations < 300ms (p95)
- Agent runs complete within 90 seconds; long runs stream progress via SSE

### Security
- Admin routes protected by NextAuth.js session middleware
- FastAPI admin endpoints validate signed JWT from NextAuth
- Rate limiting on comment submission: 3 per IP per hour
- Honeypot field on all public forms
- All secrets in `.env` files, never committed; documented in `.env.example`
- Input sanitisation on all user-generated content

### Reliability
- Agent run failures caught and logged to `agent_runs.status = failed` — server does not crash
- BlockNote autosave to `localStorage` every 30 seconds
- Soft deletes on all content

### SEO
- Dynamic `<title>` and `<meta description>` via Next.js `generateMetadata`
- OpenGraph tags on every post
- Static generation (`generateStaticParams`) for published posts with revalidation on publish/edit
- Auto-generated `sitemap.xml` from published posts
- `robots.txt` allows public routes; blocks `/admin`

---

## 10. Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | Next.js 14 (App Router) | SSR + SSG for SEO |
| Styling | Tailwind CSS + shadcn/ui | Component primitives |
| Editor | BlockNote | Notion-style WYSIWYG, markdown output |
| State / data fetching | Zustand + React Query | Server state via React Query |
| Auth | NextAuth.js | Admin-only, credentials provider |
| Backend | FastAPI (Python 3.11+) | Async, type-safe |
| Agent framework | LangGraph | Stateful multi-agent graph, max 4 nodes |
| LLM provider | OpenAI GPT-4o | Single provider for simplicity |
| Web search tool | Tavily API | Built for LLM agents |
| Embeddings | OpenAI text-embedding-3-small | 1536 dimensions |
| Database | PostgreSQL 15+ | Primary data store |
| Vector extension | pgvector | Semantic search + agent memory |
| DB hosting | Supabase or Neon | Managed Postgres + pgvector |
| Backend hosting | Railway or Render | Python deploy targets |
| Frontend hosting | Vercel | Zero-config Next.js |
| Image hosting | Cloudinary | CDN, transformations, free tier |
| Email | Resend | Agent run notifications |
| Scheduler | APScheduler (Python) | In-process cron |
| Tracing | Langfuse | LLM + agent observability (Phase 3) |
| Monorepo | Turborepo | Task orchestration, shared packages |
| CI/CD | GitHub Actions | Lint, test, deploy on merge to main |

---

## 11. Observability & Metrics

### External Tracing — Langfuse (Phase 3)

Langfuse is integrated during Phase 3 alongside the agent pipeline. It traces:

- LangGraph node execution (entry, exit, duration per node)
- Every LLM call (model name, prompt, completion, token usage, latency)
- Tavily search calls (query, results count, latency)
- Agent run outcomes (completed, failed, topic selected)

Langfuse is cloud-hosted on its free tier. No self-hosted observability infrastructure is built.

### Internal Admin Dashboard (Phase 4)

Lightweight metrics displayed in the admin panel, computed from existing DB tables:

| Metric | Source |
|--------|--------|
| Draft approval rate | `post_feedback` |
| Average edits per approved post | `post_feedback.edit_diff` |
| Rejection rate | `post_feedback` |
| Content diff visualisation | `post_feedback.edit_diff` — AI output vs final |
| Agent run summaries | `agent_runs` |

> **Note:** Content diff visualisation is a Phase 4 feature. It depends on `post_feedback` and edit diff storage being fully operational from Phase 4 feedback loop work. It must not be started earlier.

---

## 12. Development Phases & Timeline

### Phase 1 — Foundation (Core Blog, No AI)
**Goal:** A fully working, deployable personal blog the author can use immediately.

- [ ] Monorepo scaffolding (Turborepo, apps/web, apps/api, packages/)
- [ ] PostgreSQL schema + Alembic migrations
- [ ] FastAPI: posts CRUD, categories, tags, comments endpoints
- [ ] Next.js: public blog feed, post detail, markdown rendering
- [ ] Sidebar TOC with IntersectionObserver active section tracking
- [ ] BlockNote editor in admin (markdown output configured)
- [ ] Admin post management (create, edit, publish, delete, soft-delete)
- [ ] NextAuth.js admin auth (credentials provider)
- [ ] Light / dark mode (next-themes + Tailwind)
- [ ] Cloudinary image upload integration
- [ ] Vercel + Railway/Render deployment
- [ ] GitHub Actions CI/CD pipeline
- [ ] sitemap.xml + robots.txt

**Exit criteria:** Author can write and publish a post from the admin panel. Blog is live.

---

### Phase 2 — Semantic Layer
**Goal:** All content is semantically searchable. Agent infrastructure is in place.

- [ ] pgvector extension enabled and configured
- [ ] Embedding pipeline: embed posts on save/publish (background task, text-embedding-3-small, 1536d)
- [ ] `post_embeddings` and `context_embeddings` tables with ivfflat indexes
- [ ] Semantic search FastAPI endpoint with cosine similarity + full-text fallback
- [ ] Search UI in Next.js (debounced, results panel)
- [ ] Context management page in admin (bio, interests, tone notes, writing samples)
- [ ] Context re-embedding on save

**Exit criteria:** Semantic search is live. Admin context page functional. pgvector schema confirmed for Phase 3.

---

### Phase 3 — AI Agent Pipeline
**Goal:** Agents generate draft posts autonomously on a configurable schedule.

- [ ] LangGraph graph definition and AgentState schema
- [ ] Orchestrator node (topic selection, interest querying, pgvector dedup)
- [ ] Research Agent node (Tavily integration, source summarisation)
- [ ] Tone/Feedback Agent node (tone directive generation, context retrieval)
- [ ] Writer Agent node (GPT-4o draft generation, markdown output)
- [ ] Review Router node (save as agent_draft, email notification)
- [ ] APScheduler integration with configurable cron from DB
- [ ] Agent configuration UI in admin (schedule, manual trigger)
- [ ] Agent run log streaming via SSE
- [ ] Agent draft review UI (approve, edit, reject)
- [ ] `agent_runs` table + structured logging
- [ ] Langfuse integration (LLM calls, node traces, run outcomes)

**Exit criteria:** Agent runs on schedule, produces a draft, author can review and approve from admin. Langfuse traces are visible.

---

### Phase 4 — Learning Loop & Observability
**Goal:** Agent output improves from author feedback. Internal metrics are visible.

- [ ] `post_feedback` table and schema
- [ ] Feedback capture on draft approval (positive/mixed/negative + unified diff)
- [ ] Edit diff computation and storage on approval-with-edits
- [ ] Tone/Feedback Agent updated to query and incorporate feedback history (5 most recent signals)
- [ ] Internal admin metrics dashboard (approval rate, avg edits, rejection rate)
- [ ] Content diff visualisation (AI draft vs final approved — Phase 4 only)
- [ ] Agent run summaries in admin

**Exit criteria:** Tone Agent incorporates feedback signals. Measurable improvement in draft-to-publish edit count over time. Diff visualisation functional.

---

### Phase 5 — Polish
**Goal:** Production quality, performance, and any remaining gaps.

- [ ] Full mobile responsiveness audit
- [ ] Core Web Vitals audit and fixes
- [ ] OG image generation per post (Vercel OG or Cloudinary)
- [ ] RSS feed
- [ ] Accessibility audit (WCAG AA)
- [ ] Performance audit (Lighthouse)
- [ ] Documentation: README, architecture overview, setup guide

---

## 13. Portfolio Value

This project is designed to be read as a portfolio artifact as much as it is designed to be used. It demonstrates:

| Skill area | What it shows |
|------------|---------------|
| Multi-agent AI system design | LangGraph graph with typed state, constrained node count, deliberate agent responsibilities |
| Human-in-the-loop AI workflows | Draft approval system, feedback capture, no auto-publishing |
| Semantic search with vector databases | pgvector, cosine similarity, embedding pipeline, full-text fallback |
| Feedback-driven AI improvement | Prompt-level learning loop using stored diffs and few-shot examples |
| Full-stack engineering | Next.js, FastAPI, PostgreSQL, Turborepo monorepo, CI/CD |
| Real-world AI observability | Langfuse integration for LLM and agent tracing |
| Production deployment | Vercel, Railway/Render, managed Postgres, image CDN |
| Clean architecture | Separation of concerns across frontend, backend, agent, and data layers |

---

## 14. Non-Goals (v1)

| Item | Reason deferred |
|------|----------------|
| SaaS / multi-tenant UI | Not a v1 goal; personal use only |
| Billing or monetization | No SaaS pivot in v1 |
| Full autonomy / auto-publishing | Human review is a core design principle |
| Fine-tuning | Prompt-level learning loop is sufficient for v1 |
| Knowledge graph | Adds significant complexity without clear v1 payoff |
| Comments moderation queue | Basic spam filtering is sufficient for personal blog |
| Guest / co-authors | Single-author only |
| Mobile app | Web-first only |
| Self-hosted observability | Langfuse cloud handles this |
| Over-engineered agent expansion | 4 nodes maximum; every agent must earn its place |

---

## 15. Open Questions

| # | Question | Impact | Decision needed by |
|---|----------|--------|--------------------|
| 1 | Supabase vs Neon for managed Postgres? Supabase has a built-in auth SDK and realtime layer; Neon has serverless branching useful for staging environments. | DB hosting, local dev setup | Before Phase 1 |
| 2 | Railway vs Render for FastAPI hosting? Railway has better developer experience; Render has a more predictable free tier. | Backend deploy pipeline | Before Phase 1 |
| 3 | What are your portfolio website's exact colour tokens (hex values)? Required before any frontend UI work begins. | Tailwind config, design system | Before Phase 1 UI work |
| 4 | Should agent run email notifications (Resend) be on by default, or opt-in from the admin config page? | Agent configuration UI | Before Phase 3 |

---

*End of PRD v2.0 — d3jusdevspace*
