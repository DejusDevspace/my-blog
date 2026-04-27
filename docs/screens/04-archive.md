# Screen 04 — Category / Tag Archive
**Routes:** `/category/[slug]` and `/tag/[slug]`
**Auth required:** No
**Document version:** 1.0

---

## Purpose
A filtered view of all posts belonging to a specific category or tag. Structurally similar to the Home feed but scoped, with a clear identity header communicating what the reader is browsing. Serves both SEO (indexable archive pages) and navigation (readers exploring a topic).

---

## Layout structure

Identical to Home / Feed (Screen 01) with one addition: an **Archive Header** replaces the Hero section.

```
┌─────────────────────────────────────────────────────┐
│                     NAV BAR                         │
├─────────────────────────────────────────────────────┤
│                  ARCHIVE HEADER                     │
│           (category/tag identity + stats)           │
├──────────────────┬──────────────────────────────────┤
│                  │                                  │
│  FILTER SIDEBAR  │        POST FEED GRID            │
│  (same as home)  │        (scoped to archive)       │
│                  │                                  │
│                  ├──────────────────────────────────┤
│                  │          PAGINATION              │
└──────────────────┴──────────────────────────────────┘
│                       FOOTER                        │
└─────────────────────────────────────────────────────┘
```

---

## Components

### 1. Nav bar
Identical to home feed nav bar. No changes.

---

### 2. Archive header
**Replaces** the hero section from the home feed.
**Background:** `var(--color-bg-surface)`, `border-bottom: 1px solid var(--color-border-subtle)`
**Padding:** `var(--space-10)` vertical

Contents (left-aligned within content column):

1. **Breadcrumb**
   - For category: `Home / [Category Name]`
   - For tag: `Home / Tags / [Tag Name]`
   - Font: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`
   - `Home` links to `/`; `Tags` links to a tags index (if built)

2. **Archive type pill**
   - Category archive: pill with label `"Category"` — `.tag` styles
   - Tag archive: pill with label `"Tag"` — `.tag` styles but with a `#` prefix in the text: `"# langchain"`

3. **Archive name**
   - Font: `Montserrat`, `var(--text-display)`, `var(--weight-bold)`, `var(--color-text-primary)`
   - Category names are title-cased: `"Projects"`, `"Blog"`, `"Thoughts"`, `"Docs"`
   - Tag names are shown as-is: `"langchain"`, `"fastapi"`, `"career"`

4. **Archive description** (category archives only)
   - Short description of what lives in this category
   - e.g. for `projects`: `"Case studies, builds, and side projects."`
   - Font: `Space Grotesk`, `var(--text-body)`, `var(--color-text-secondary)`
   - Tags do not have descriptions — skip this element for tag archives

5. **Post count**
   - `"24 posts"` — `JetBrains Mono`, `var(--text-caption)`, `var(--color-accent)`

---

### 3. Filter sidebar

Same component as the home feed filter sidebar. Behaviour differences:
- The active category is pre-selected and visually locked (highlighted, not clickable to deselect — clicking it would route back to `/`)
- For a tag archive, the tag is shown as an active filter pill in the sidebar's tag cloud section with a remove (`×`) button — clicking remove routes back to `/`
- All other categories and tags are still browsable — combining filters narrows the results within the archive

---

### 4. Post feed grid
Identical post card component to home feed. No changes. Posts are pre-filtered to the archive's category or tag.

---

### 5. Pagination
Identical to home feed pagination.

---

### 6. Footer
Identical to home feed footer.

---

## Page states

### Loading
Same skeleton behaviour as home feed.

### Empty state
Centred in the grid area:
- Icon: Lucide `FolderOpen`, `var(--icon-lg)`, `var(--color-text-tertiary)`
- Heading: `"No posts in [Name] yet"` — `Space Grotesk`, `var(--text-h3)`
- Sub-text: `"Check back soon."` — `var(--color-text-secondary)`
- CTA: `"Browse all posts"` — `.btn-ghost`, routes to `/`

---

## Interactions & behaviour

- URL params (`?tag=`, `?category=`) work the same as on the home feed — additional filters are additive
- Navigating from a category archive to a tag (by clicking a tag pill on a card) routes to the tag archive, does not layer the filters in the URL
- The sidebar active state automatically reflects the current archive context on load
- Back navigation from a post returns to the archive at the correct scroll position

---

## SEO & metadata

Category archive:
```html
<title>[Category Name] — d3jusdevspace</title>
<meta name="description" content="All posts in the [Category] category on d3jusdevspace." />
```

Tag archive:
```html
<title>Posts tagged "[tag]" — d3jusdevspace</title>
<meta name="description" content="All posts tagged [tag] on d3jusdevspace." />
```

Both archive types are fully indexable (`index, follow`). Each is a canonical URL — no duplicate content with the home feed since they have distinct routes and content subsets.

---

## Responsive summary
Identical to home feed responsive behaviour. No exceptions.
