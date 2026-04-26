# Screen 03 — Search Results
**Route:** `/search?q=[query]`
**Auth required:** No
**Document version:** 1.0

---

## Purpose
Surfaces semantically relevant posts in response to a natural language query. Designed to feel fast, intelligent, and transparent — the reader should understand why each result is relevant. This page is a key showcase of the semantic search infrastructure underpinning the site.

---

## Layout structure

```
┌──────────────────────────────────────────────────────┐
│                      NAV BAR                         │
├──────────────────────────────────────────────────────┤
│                   SEARCH HERO                        │
│              (search bar, prominent)                 │
├──────────────────────────────────────────────────────┤
│   RESULT METADATA BAR                                │
│   "12 results for 'building agents with LangGraph'"  │
├──────────────────────────────────────────────────────┤
│                                                      │
│              SEARCH RESULT CARDS                     │
│              (single column, stacked)                │
│                                                      │
├──────────────────────────────────────────────────────┤
│                   PAGINATION                         │
└──────────────────────────────────────────────────────┘
│                     FOOTER                           │
└──────────────────────────────────────────────────────┘
```

**Max content width:** 800px, centred — narrower than home feed to keep results focused and scannable.

---

## Components

### 1. Search hero
**Background:** `var(--color-bg-surface)`, `border-bottom: 1px solid var(--color-border-subtle)`
**Padding:** `var(--space-12)` top/bottom

Contents:
- Heading: `"Search"` — `Montserrat`, `var(--text-h1)`, `var(--weight-bold)`, `var(--color-text-primary)`
- Sub-label: `"Ask anything. Powered by semantic search."` — `Space Grotesk`, `var(--text-body-sm)`, `var(--color-text-tertiary)`
- Search input bar (full-width, prominent):
  - Width: 100% of the 800px content column
  - Height: `52px`
  - Background: `var(--color-bg-elevated)`
  - Border: `1px solid var(--color-border-default)`
  - Border-radius: `var(--radius-md)`
  - Font: `Space Grotesk`, `var(--text-body)`, `var(--color-text-primary)`
  - Placeholder: `"e.g. how to build a multi-agent system with LangGraph"` — `var(--color-text-tertiary)`
  - Left icon: Lucide `Search`, `var(--icon-md)`, `var(--color-text-tertiary)`
  - Right slot: clear button (Lucide `X`, appears when input has value) + loading spinner (appears while fetching)
  - On focus: `border-color: var(--color-accent)`, `box-shadow: 0 0 0 3px var(--color-accent-muted)`
  - Pre-populated with the `q` URL param value on load
  - Debounce: 300ms before triggering new search on keystroke
  - On Enter / search icon click: updates URL param and fetches results

---

### 2. Result metadata bar
**Background:** transparent
**Padding:** `var(--space-4)` vertical
**Border bottom:** `1px solid var(--color-border-subtle)`

Contents (single row, flex, space-between):
- Left: result summary text
  - `"12 results for "` in `var(--color-text-secondary)` + `"building agents with LangGraph"` in `var(--color-text-primary)`, quoted, `var(--weight-medium)` — `Space Grotesk`, `var(--text-body-sm)`
  - If fallback keyword search was used: append `"(keyword match)"` in `var(--color-text-tertiary)` italic
- Right: search mode indicator pill
  - Semantic mode: `"✦ Semantic"` — `.badge-agent` styles (accent colour, neon glow)
  - Keyword fallback mode: `"Keyword"` — `.badge-archived` styles (warning colour)

---

### 3. Search result cards
**Layout:** single column, gap `var(--space-4)`

Each result card:

```
┌──────────────────────────────────────────────────────────┐
│  CATEGORY BADGE          ✦ AGENT BADGE (conditional)     │
│                                                          │
│  POST TITLE                                              │
│                                                          │
│  EXCERPT with matched terms lightly highlighted          │
│                                                          │
│  ─────────────────────────────────────────────────────   │
│  DATE · READ TIME · TAGS...                              │
└──────────────────────────────────────────────────────────┘
```

Differences from the home feed post card:
- **Excerpt is longer** — up to 5 lines (vs 3 on home feed) to show more context around why the result matched
- **Matched term highlighting** — if the query contains words that appear in the excerpt, those words are wrapped in `<mark>` styled as: `background: var(--color-accent-muted)`, `color: var(--color-accent)`, `border-radius: var(--radius-sm)`, `padding: 1px 3px`
- **No skeleton hover translation** — result cards do not animate on hover (this is a results list, not a browsing grid)
- All other card styles identical to home feed post card

---

### 4. Pagination
Same component as home feed pagination. Shows page controls when results exceed the page limit (default: 10 results per page).

---

## Page states

### Initial (no query yet)
If the user navigates to `/search` without a `q` param:
- Search hero renders with empty input
- No result metadata bar
- Below the search bar:
  - Heading: `"What are you looking for?"` — `Space Grotesk`, `var(--text-h3)`, `var(--color-text-secondary)`
  - Suggested searches section: 4–6 example queries as clickable pills
    - e.g. `"multi-agent systems"`, `"FastAPI tutorial"`, `"career in AI"`, `"LangGraph examples"`
    - Pill style: `.btn-ghost` with a Lucide `ArrowUpRight` icon
    - On click: populates the search bar and triggers a search

### Loading (query submitted, fetching)
- Result metadata bar shows a skeleton line (animated pulse)
- 5 skeleton result cards below it

### Results found
- Standard layout as described above

### No results
- Result metadata bar: `"0 results for "[query]""`
- Below the bar, centred:
  - Icon: Lucide `SearchX`, `var(--icon-lg)`, `var(--color-text-tertiary)`
  - Heading: `"No results found"` — `Space Grotesk`, `var(--text-h3)`
  - Sub-text: `"Try different keywords, or browse all posts."` — `var(--color-text-secondary)`
  - CTA: `"Browse all posts"` — `.btn-primary`, routes to `/`

### Error state
- Icon: Lucide `AlertCircle`, `var(--color-danger)`
- Heading: `"Search unavailable"`
- Sub-text: `"The search service is temporarily unavailable. Try browsing posts instead."`
- CTA: `"Browse all posts"` — `.btn-primary`

---

## Interactions & behaviour

- URL is the source of truth: `?q=my+query` — results are fully shareable and bookmarkable
- Typing in the search bar updates the URL param (using `router.replace`, not `router.push`, so back button doesn't step through every keystroke)
- Pressing `Escape` in the search input clears the query and resets to the initial state
- Clicking a result card navigates to `/posts/[slug]`
- Clicking a tag pill on a result card routes to the tag archive at `/tag/[slug]`
- Browser back from a post detail page returns to the search results at the correct scroll position (preserved via React Query cache)

---

## SEO & metadata

```html
<title>Search: "[query]" — d3jusdevspace</title>
<meta name="robots" content="noindex" />
```

Search result pages are `noindex` — they should not appear in search engine results. Only canonical post pages and category archives should be indexed.

---

## Responsive summary

| Element | lg+ | md | sm |
|---------|-----|----|----|
| Content column | 800px centred | fluid, padded | full width, 16px padding |
| Search bar | 52px tall | 52px tall | 48px tall |
| Metadata bar | flex row | flex row | stacked |
| Result cards | full width | full width | full width, compact excerpt |
