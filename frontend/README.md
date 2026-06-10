# d3jusdevspace — Frontend

The frontend for my personal AI-powered blog and knowledge hub. Built with Next.js App Router, Tailwind CSS v4, and React Query, featuring a modern Cyber-Luxury design.

## Tech Stack

| Technology           | Purpose                                             |
| -------------------- | --------------------------------------------------- |
| **Next.js 16**       | React framework with App Router                     |
| **Tailwind CSS v4**  | Utility-first CSS framework for styling             |
| **React Query (v5)** | Data fetching, caching, and state management        |
| **NextAuth.js**      | Admin authentication                                |
| **BlockNote**        | Block-based rich text editor for markdown           |
| **React Markdown**   | Rendering markdown content with syntax highlighting |
| **Lucide React**     | Icon library for admin UI                           |

## Features

- **Public Blog**: View posts filtered by category, tag, or series.
- **Hybrid Search**: Debounced search bar with semantic + FTS results, aggregated relevance scoring, and highlighted snippets.
- **Admin Dashboard**: Full CMS for managing posts, categories, tags, series, and comments.
- **Markdown Editor**: Rich text editing with BlockNote, supporting code blocks and image uploads via Cloudinary.
- **Agent Settings**: Schedule management with preset cards (Daily/Weekly/Bi-weekly/Custom), manual pipeline trigger with loading state, and last-run summary card.
- **Agent Run Log**: Paginated table of all pipeline runs with status badges, topic, trigger source, duration, and detail view with run log JSON viewer, LangFuse trace link, and output post link.
- **Agent Drafts Review**: Card-based list of agent-authored drafts with excerpt and category tags; detail page with full content preview, publish/edit/delete actions, and confirm modal for deletion.
- **Admin Settings**: Context management interface for AI agent personalisation (bio, interests, learning focus, lifestyle).
- **Cyber-Luxury Aesthetic**: Custom dark theme with neon accents, smooth gradients, and glassmorphism elements.
- **API Proxy**: Next.js proxy route (`/api/proxy`) to forward requests to the FastAPI backend, handling authentication transparently.

## Environment Variables

Copy `.env.example` to `.env.local` and configure your settings:

```env
BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-here
NEXTAUTH_URL=http://localhost:3000
ADMIN_EMAIL=admin@d3jus.dev
ADMIN_PASSWORD=admin
```

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Run the development server:
   ```bash
   npm run dev
   ```
3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Architecture Highlights

- **`src/app`**: Next.js App Router pages and layouts, organised into public and admin route groups. Admin includes agent settings, run log (list + detail), and draft review pages.
- **`src/app/api/proxy`**: Proxies requests to the backend. Handles `multipart/form-data` for image uploads.
- **`src/components`**: Reusable UI components, editor components, blog layouts, settings forms, agent schedule form, and feed filtering.
- **`src/services/api.ts`**: API wrapper functions that interface with the backend via `apiClient.ts`. Includes agent trigger, run history, schedule, and draft management endpoints.
- **`src/hooks/useApi.ts`**: React Query hooks for fetching and mutating data. Agent hooks use dedicated query keys for schedule, runs list, and run detail with automatic cache invalidation on trigger/update.
- **`src/types`**: TypeScript interfaces that mirror backend Pydantic schemas, including agent run, schedule, and trigger response types.
