# Screen 05 — Admin Dashboard / Posts Table
**Route:** `/admin`
**Auth required:** Yes (admin only)
**Document version:** 1.0

---

## Purpose
The home screen of the admin panel. Gives the author a complete, actionable view of all content in the system — across all statuses — and serves as the primary content management interface. Fast access to edit, publish, unpublish, and delete. Also surfaces at-a-glance stats.

---

## Layout structure

All admin screens share this persistent shell:

```
┌────────────────────────────────────────────────────────┐
│                     TOP BAR (56px)                     │
├───────────────┬────────────────────────────────────────┤
│               │                                        │
│   SIDEBAR     │         MAIN CONTENT AREA              │
│   (240px)     │                                        │
│   (fixed)     │                                        │
│               │                                        │
└───────────────┴────────────────────────────────────────┘
```

The sidebar and top bar persist across all admin screens. Only the main content area changes per route.

---

## Admin shell components

### Top bar
**Height:** `56px`
**Background:** `var(--color-bg-surface)`
**Border bottom:** `1px solid var(--color-border-subtle)`
**Position:** sticky top, `z-index: 40`

Left slot:
- Hamburger/close icon (mobile only): Lucide `Menu` / `X`
- Site name: `d3jusdevspace` — `JetBrains Mono`, bold, `var(--color-accent)`, neon shadow — links to `/` (public site) in new tab

Right slot:
- `"View site"` link: Lucide `ExternalLink` icon + `"View site"` text — `.btn-ghost`, opens public site in new tab
- Admin avatar/initials circle: `32px`, `border-radius: var(--radius-full)`, `background: var(--color-accent-muted)`, initials in `var(--color-accent)` — clicking opens a small dropdown with `"Sign out"`

---

### Admin sidebar
**Width:** `240px`, fixed left
**Background:** `var(--color-bg-surface)`
**Border right:** `1px solid var(--color-border-subtle)`
**Padding:** `var(--space-4)`

Navigation sections (top to bottom):

**Content**
- `Posts` — Lucide `FileText` icon — routes to `/admin`
- `New post` — Lucide `Plus` icon — routes to `/admin/posts/new`
- `Agent Drafts` — Lucide `Sparkles` icon — routes to `/admin/agent-drafts` — shows a count badge if pending drafts exist

**Settings** (section label, not a link)
- `My Context` — Lucide `User` icon — routes to `/admin/settings/context`
- `Agent Settings` — Lucide `Bot` icon — routes to `/admin/settings/agent`

**Activity**
- `Run Log` — Lucide `Activity` icon — routes to `/admin/agent/runs`

Nav item styles:
- Default: `Space Grotesk`, `var(--text-body-sm)`, `var(--color-text-secondary)`, `border-radius: var(--radius-md)`, padding `var(--space-2) var(--space-3)`
- Active: `var(--color-accent)` text, `background: var(--color-accent-muted)`, left border `3px solid var(--color-accent)`
- Hover (non-active): `background: var(--color-bg-elevated)`, `var(--color-text-primary)`
- Icons: `var(--icon-sm)`, colour inherits from text

Pending drafts badge:
- Small pill next to `Agent Drafts`: count in `var(--color-accent)` text, `background: var(--color-accent-muted)`, `border-radius: var(--radius-full)`, font `JetBrains Mono`, `var(--text-xs)`

Mobile sidebar:
- Hidden by default, slides in from left on hamburger tap
- Overlay backdrop: `rgba(0,0,0,0.5)`, tap to close

---

## Main content: Admin Dashboard

### Stats row
**Layout:** 4 metric cards in a horizontal row
**Gap:** `var(--space-4)`
**Card styles:** `background: var(--color-bg-surface)`, `border: 1px solid var(--color-border-subtle)`, `border-radius: var(--radius-lg)`, padding `var(--space-5)`

Cards (left to right):
1. **Total posts** — number, Lucide `FileText` icon in muted accent tint
2. **Published** — count of status=published posts, Lucide `Globe` icon, value in `var(--color-success)`
3. **Drafts** — count of status=draft + agent_draft, Lucide `Edit3` icon
4. **Agent drafts pending** — count of status=agent_draft, Lucide `Sparkles` icon, value in `var(--color-accent)`

Card anatomy:
- Icon: `var(--icon-md)`, in a small `32px` circle with matching muted background
- Value: `Space Grotesk`, `2rem`, `var(--weight-bold)`, `var(--color-text-primary)`
- Label: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`, uppercase, letter-spacing

---

### Posts table

**Heading row:** `"All posts"` — `Space Grotesk`, `var(--text-h3)`, `var(--weight-semibold)` — left aligned, with `"New post"` `.btn-primary` button on the right

**Filter/search bar** (above the table):
- Left: text search input — `placeholder="Search posts..."`, filters the table client-side on title
- Right: status filter dropdown — `"All statuses"` default, options: `All`, `Published`, `Draft`, `Agent Draft`, `Archived`
- Category filter dropdown — `"All categories"`

**Table:**

| Column | Content | Width | Notes |
|--------|---------|-------|-------|
| Title | Post title (truncated, links to editor) | fluid | Bold, `var(--color-text-primary)` |
| Status | Status badge | 120px | `.badge-published`, `.badge-draft`, etc. |
| Category | Category tag pill | 100px | `.tag` styles |
| Agent | `"✦"` icon if agent-authored | 60px | Centred, `var(--color-accent)`, else empty |
| Date | Published or updated date | 120px | `JetBrains Mono`, `var(--text-xs)` |
| Actions | Icon buttons | 100px | Edit, Preview, Delete |

Table styles:
- Header row: `background: var(--color-bg-elevated)`, `JetBrains Mono`, `var(--text-xs)`, uppercase, `var(--color-text-tertiary)`, `letter-spacing: 0.06em`
- Body rows: `border-bottom: 1px solid var(--color-border-subtle)`
- Alternate row shading: even rows get `background: var(--color-bg-elevated)` at very low opacity (subtle striping)
- Row hover: `background: var(--color-bg-elevated)`
- Clicking a title cell navigates to `/admin/posts/[id]/edit`

Action buttons (per row, icon-only with tooltip on hover):
- Edit: Lucide `Edit3`, `.btn-ghost` sizing
- Preview: Lucide `ExternalLink` — opens `/posts/[slug]` in new tab (only shown for published posts)
- Delete: Lucide `Trash2`, text `var(--color-danger)` on hover

**Delete confirmation:**
- Clicking delete opens an inline confirmation in the row: `"Delete this post?"` with `"Cancel"` and `"Delete"` (`.btn-danger`) buttons — no modal
- Confirmed deletion performs soft-delete, row fades out and disappears

---

### Bulk actions (optional v1 enhancement)
- Checkbox column on left of table
- When 1+ rows selected, a sticky actions bar appears above the table: `"3 posts selected"` + `"Publish all"` / `"Archive all"` / `"Delete all"` buttons

---

## Page states

### Loading
- Stats row shows skeleton metric cards (4 cards, same dimensions, pulsing)
- Table shows 8 skeleton rows

### Empty (no posts yet)
- Stats row: all zeros
- Table replaced by centred empty state:
  - Icon: Lucide `FileText`, `var(--icon-lg)`, `var(--color-text-tertiary)`
  - Heading: `"No posts yet"`
  - CTA: `"Write your first post"` — `.btn-primary`, routes to `/admin/posts/new`

### Unauthenticated access attempt
- Redirect to `/admin/login` before rendering any admin content

---

## Admin login page
**Route:** `/admin/login`

Simple centred card:
- Card: `max-width: 400px`, centred on page, `var(--color-bg-surface)` background
- Site name at top
- Heading: `"Admin login"` — `Space Grotesk`, `var(--text-h2)`
- Email input: `.input`, full width
- Password input: `.input`, full width, toggle show/hide password
- Submit button: `.btn-primary`, full width, `"Sign in"`
- On error: inline message below form: `"Invalid credentials"` — `var(--color-danger)`, `var(--text-body-sm)`

---

## Responsive summary

| Element | lg+ | md | sm |
|---------|-----|----|----|
| Sidebar | 240px fixed | hidden, drawer | hidden, drawer |
| Stats row | 4 columns | 2×2 grid | 2×2 grid |
| Table | full columns | hide Agent, Date cols | title + status + actions only |
| Top bar | full | full | full |
