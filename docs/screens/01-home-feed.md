# Screen 01 — Home / Feed
**Route:** `/`
**Auth required:** No
**Document version:** 1.0

---

## Purpose
The primary entry point for all visitors. Presents all published posts in a scannable, filterable feed. Sets the tone for the entire site — the first impression of the author's brand, aesthetic, and content depth.

---

## Layout structure

```
┌─────────────────────────────────────────────────────┐
│                     NAV BAR                         │
├─────────────────────────────────────────────────────┤
│                   HERO / HEADER                     │
├──────────────────┬──────────────────────────────────┤
│                  │                                  │
│  FILTER SIDEBAR  │        POST FEED GRID            │
│  (sticky, left)  │        (main content)            │
│                  │                                  │
│                  ├──────────────────────────────────┤
│                  │          PAGINATION              │
└──────────────────┴──────────────────────────────────┘
```

**Breakpoint behaviour:**
- `lg+` (1024px+): Two-column layout — filter sidebar left (240px), post grid right (fluid)
- `md` (768–1023px): Filter sidebar collapses into a horizontal filter bar above the grid
- `sm` (< 768px): Single column, filter bar becomes a dropdown/sheet trigger

---

## Components

### 1. Nav bar
**Position:** sticky top, `z-index: 50`, `height: 64px`
**Background:** `var(--color-bg-surface)` with `border-bottom: 1px solid var(--color-border-subtle)`

Left slot:
- Site name: `d3jusdevspace` — `JetBrains Mono`, bold, `var(--color-accent)`, `var(--shadow-neon-accent)`

Centre slot:
- Search bar (desktop): `placeholder="Search posts..."`, `width: 320px`, clicking it expands or routes to search

Right slot (left to right):
- Theme toggle button (sun/moon icon, `Lucide`)
- Optional: GitHub icon link (external)

---

### 2. Hero / Header section
**Height:** ~200px
**Background:** `var(--color-bg-page)` with a subtle top border accent line in `var(--color-accent)` (3px)

Contents:
- Headline: `"Hi, I'm d3jus"` — `Montserrat`, `var(--text-display)`, bold
- Sub-headline: one-liner bio (pulled from `user_context.bio`, truncated to ~120 chars) — `Space Grotesk`, `var(--text-body-lg)`, `var(--color-text-secondary)`
- Post count stat: `"42 posts"` — `JetBrains Mono`, `var(--text-caption)`, `var(--color-accent)`

On mobile: hero shrinks to ~120px, headline drops to `var(--text-h1)`

---

### 3. Filter sidebar (desktop) / Filter bar (mobile)

**Desktop sidebar:**
- `width: 240px`, sticky within the content area (not the viewport)
- `background: var(--color-bg-surface)`, `border-right: 1px solid var(--color-border-subtle)`
- Padding: `var(--space-6)`

Contents:
- Section label: `"Categories"` — `JetBrains Mono`, `var(--text-xs)`, uppercase, `var(--color-text-tertiary)`
- Category list: clickable items — `All`, `Projects`, `Thoughts`, `Blog`, `Docs`
  - Active item: `var(--color-accent)` text, left border `3px solid var(--color-accent)`
  - Inactive item: `var(--color-text-secondary)`, no border
  - Each item shows a post count in muted text: `Projects (12)`
- Divider
- Section label: `"Tags"`
- Tag cloud: pill tags using `.tag` component styles, wrapping flexbox
  - Top 15 tags by post count shown
  - "Show all tags" expand toggle if more than 15
- Divider
- Active filter summary: `"Showing: Projects + langchain"` with a clear button — only visible when filters are active

**Mobile filter bar:**
- Horizontal scrollable row of category pills above the grid
- "Filter" button opens a bottom sheet with full category + tag filter UI

---

### 4. Post feed grid

**Layout:** Single column of post cards, max-width fluid
**Gap between cards:** `var(--space-5)`

#### Post card component

```
┌────────────────────────────────────────────────┐
│  CATEGORY BADGE   ✦ AGENT BADGE (conditional)  │
│                                                │
│  POST TITLE                                    │
│  (2 lines max, truncated with ellipsis)        │
│                                                │
│  EXCERPT                                       │
│  (3 lines max)                                 │
│                                                │
│  ─────────────────────────────────────────     │
│  DATE · READ TIME · TAGS...                    │
└────────────────────────────────────────────────┘
```

**Card styles:**
- Background: `var(--color-bg-surface)`
- Border: `1px solid var(--color-border-subtle)`, `var(--radius-lg)`
- Padding: `var(--space-6)`
- Hover: `border-color: var(--color-border-default)`, subtle `translateY(-2px)` transform, `transition: var(--transition-base)`
- Cursor: `pointer` — entire card is clickable, routes to post detail

**Inside the card (top to bottom):**

1. **Badge row** — flex, space-between
   - Left: Category badge — `.tag` styles, e.g. `blog`, `projects`
   - Right: Agent badge — `.badge-agent` with `"✦ Agent"` text — only rendered when `is_agent_authored === true`

2. **Post title**
   - Font: `Space Grotesk`, `var(--text-h4)`, `var(--weight-semibold)`
   - Colour: `var(--color-text-primary)`
   - Max 2 lines, `overflow: hidden`, `text-overflow: ellipsis`
   - On hover: colour shifts to `var(--color-accent)`

3. **Excerpt**
   - Font: `Space Grotesk`, `var(--text-body-sm)`, `var(--weight-regular)`
   - Colour: `var(--color-text-secondary)`
   - Max 3 lines, `overflow: hidden`

4. **Divider** — `1px solid var(--color-border-subtle)`

5. **Meta row** — flex, align-centre, gap `var(--space-3)`
   - Published date: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`
   - Separator dot: `·`
   - Reading time: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`
   - Tags: up to 2 tag pills, any additional shown as `+N more`

---

### 5. Pagination

**Position:** below the post grid, centred
**Style:** simple prev/next + page numbers
- Current page number highlighted with `var(--color-accent)` background (muted), `var(--color-accent)` text
- Prev/Next buttons: `.btn-ghost`
- Show at most 7 page numbers with `...` ellipsis for large ranges
- Font: `JetBrains Mono`, `var(--text-xs)`

---

### 6. Footer
**Background:** `var(--color-bg-surface)`
**Border top:** `1px solid var(--color-border-subtle)`
**Padding:** `var(--space-10)` vertical

Contents (centred):
- Site name — same treatment as nav
- Short tagline — `Space Grotesk`, `var(--color-text-tertiary)`
- Links row: GitHub, LinkedIn (or other socials) — icon + text, `var(--color-text-secondary)`
- Copyright: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`

---

## Page states

### Loading state
- Nav and hero render immediately (static)
- Post card skeletons: same card dimensions, animated pulse using `@keyframes skeleton-pulse`
- Show 6 skeleton cards while data loads

### Empty state (no posts yet, or filter returns nothing)
- Centred in the grid area
- Icon: `FileText` from Lucide, `var(--icon-lg)`, `var(--color-text-tertiary)`
- Heading: `"Nothing here yet"` — `Space Grotesk`, `var(--text-h3)`
- Sub-text differs by context:
  - No posts at all: `"Check back soon — content is on the way."`
  - Filter active: `"No posts match this filter."` + a `"Clear filters"` link

### Error state
- Same centred layout as empty state
- Icon: `AlertCircle`, `var(--color-danger)`
- Heading: `"Couldn't load posts"`
- Sub-text: `"Something went wrong. Try refreshing."`

---

## Interactions & behaviour

- Clicking any post card navigates to `/posts/[slug]`
- Clicking a category in the sidebar updates the URL param (`?category=projects`) and re-fetches — no full page reload (React Query refetch)
- Clicking a tag pill does the same (`?tag=langchain`)
- Multiple filters are additive: `?category=blog&tag=fastapi`
- Clearing a filter removes its URL param
- Search bar focus: on desktop, expands slightly; on click, routes to `/search` with the typed query as a param
- Theme toggle: immediately applies `[data-theme="light"]` attribute to `<html>` and persists to `localStorage`

---

## SEO & metadata

```html
<title>d3jusdevspace — AI engineer, builder, thinker</title>
<meta name="description" content="Personal blog by d3jus. Writing about AI engineering, projects, and thoughts." />
<meta property="og:title" content="d3jusdevspace" />
<meta property="og:description" content="Personal blog by d3jus." />
```

---

## Responsive summary

| Breakpoint | Filter | Grid | Cards |
|------------|--------|------|-------|
| `2xl` | 240px sidebar | 3-column | Full |
| `xl` | 240px sidebar | 2-column | Full |
| `lg` | 240px sidebar | 1-column | Full |
| `md` | Horizontal scroll pills | 1-column | Full |
| `sm` | Filter button → bottom sheet | 1-column | Compact (no excerpt) |
