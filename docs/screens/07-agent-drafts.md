# Screen 07 — Agent Drafts Review
**Route:** `/admin/agent-drafts`
**Auth required:** Yes (admin only)
**Document version:** 1.0

---

## Purpose
The dedicated interface for reviewing AI-generated post drafts. Lets the author efficiently read, assess, and action each draft — approve it, edit it further, or reject it — with full visibility into the agent's reasoning and source material.

---

## Layout structure

```
┌──────────────────────────────────────────────────────────┐
│              ADMIN SHELL (top bar + sidebar)             │
├────────────────────────────┬─────────────────────────────┤
│                            │                             │
│   DRAFT LIST               │   DRAFT DETAIL PANEL        │
│   (left, 340px)            │   (right, fluid)            │
│                            │                             │
│   - Scrollable list        │   - Full draft content      │
│   - One draft per row      │   - Agent metadata          │
│   - Click to select        │   - Action buttons          │
│                            │                             │
└────────────────────────────┴─────────────────────────────┘
```

**Breakpoint behaviour:**
- `lg+`: Master-detail layout — list left (340px), detail panel right
- `md` and below: Single column — list view first, tapping a draft navigates to a full-screen detail view (back button returns to list)

---

## Components

### 1. Page header
**Inside the main content area (not the top bar)**
**Padding:** `var(--space-6)` all sides, `border-bottom: 1px solid var(--color-border-subtle)`

Left: `"Agent Drafts"` — `Space Grotesk`, `var(--text-h2)`, `var(--weight-semibold)`
Sub-text: `"3 drafts awaiting review"` (dynamic count) — `var(--text-body-sm)`, `var(--color-text-secondary)`

Right: Lucide `RefreshCw` icon button (`.btn-ghost`) — manually refreshes the draft list

---

### 2. Draft list (left panel)
**Width:** `340px`
**Background:** `var(--color-bg-surface)`
**Border right:** `1px solid var(--color-border-subtle)`
**Overflow:** scrollable vertically

Each draft row:
```
┌──────────────────────────────────────────────┐
│  ✦  DRAFT TITLE (2 lines max)                │
│     Topic: [topic used by agent]             │
│     Generated [relative time] · [model]     │
└──────────────────────────────────────────────┘
```
- Padding: `var(--space-4)`
- Border bottom: `1px solid var(--color-border-subtle)`
- `✦` icon: `var(--color-accent)`, `var(--text-caption)`, neon shadow

Title:
- Font: `Space Grotesk`, `var(--text-body-sm)`, `var(--weight-semibold)`, `var(--color-text-primary)`
- Max 2 lines, truncated

Topic label:
- Font: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-secondary)`
- Prefix: `"Topic: "` in `var(--color-text-tertiary)`

Meta line:
- Font: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`
- Format: `"Generated 2 days ago · GPT-4o"`

Active/selected row:
- `background: var(--color-accent-muted)`, `border-left: 3px solid var(--color-accent)`
- Title colour: `var(--color-accent)`

Hover (non-active):
- `background: var(--color-bg-elevated)`

---

### 3. Draft detail panel (right)
**Background:** `var(--color-bg-page)`
**Padding:** `var(--space-8)`
**Overflow:** scrollable vertically

When no draft is selected (initial state):
- Centred empty state:
  - Icon: Lucide `Sparkles`, `var(--icon-lg)`, `var(--color-text-tertiary)`
  - Text: `"Select a draft to review"` — `var(--color-text-tertiary)`

When a draft is selected, the panel has three sections:

---

#### Section A: Draft header + actions

**Post title:**
- Font: `Montserrat`, `var(--text-display)`, `var(--weight-bold)`
- Editable inline (clicking makes it a text input) — changes saved on blur

**Agent metadata strip:**
- Background: `var(--color-bg-surface)`, `border: 1px solid var(--color-border-subtle)`, `border-radius: var(--radius-lg)`
- Padding: `var(--space-4)`
- Grid layout, 2 columns:
  - `"Topic"` / `[topic value]`
  - `"Generated"` / `[date and time]`
  - `"Model"` / `GPT-4o`
  - `"Run ID"` / `[agent_run id, monospace, truncated]`
- Label font: `JetBrains Mono`, `var(--text-xs)`, uppercase, `var(--color-text-tertiary)`
- Value font: `Space Grotesk`, `var(--text-body-sm)`, `var(--color-text-primary)`

**Sources used** (collapsible section, collapsed by default):
- Toggle: `"Sources (3)"` — `JetBrains Mono`, `var(--text-xs)`, `var(--color-accent)`, with Lucide `ChevronDown` icon
- Expanded list:
  - Each source: favicon + domain name + truncated page title, linking to the original URL
  - Font: `Space Grotesk`, `var(--text-body-sm)`, `var(--color-text-secondary)`
  - Border bottom between sources

**Action buttons row:**
```
[ ✦ Approve & Publish ]  [ Save as Draft ]  [ Reject ]  [ Edit in editor ]
```
- `"Approve & Publish"`: `.btn-primary`, Lucide `CheckCircle` icon, publishes immediately
- `"Save as Draft"`: `.btn-ghost`, Lucide `Save` icon, moves to regular draft status for further editing
- `"Reject"`: text `var(--color-danger)`, Lucide `XCircle` icon, `.btn-ghost` but with danger hover
- `"Edit in editor"`: `.btn-ghost`, Lucide `Edit3` icon, opens full post editor at `/admin/posts/[id]/edit`

---

#### Section B: Draft content preview

**Rendered markdown:**
- Full post content rendered as `.prose` — same styles as the public post detail page
- This is a read-only preview, not an editable surface (editing goes via the editor)
- If the content is very long, this section scrolls within the panel

**Suggested category and tags** (below the content):
- Label: `"Agent suggested:"` — `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`
- Category badge: `.tag`
- Tag pills: `.tag` for each suggested tag
- Small note: `"These will be applied on approval. Edit in the post editor."` — `var(--text-xs)`, `var(--color-text-tertiary)`

---

#### Approve confirmation flow

Clicking `"Approve & Publish"`:
- Inline confirmation banner slides down below the action buttons:
  - `"This will publish the post immediately."` — `var(--color-warning-muted)` background
  - `"Confirm publish"` (`.btn-primary`) + `"Cancel"` (`.btn-ghost`)

Clicking `"Reject"`:
- Inline rejection panel slides down:
  - `"Reason for rejection (optional)"` — textarea, `.input`, `rows: 3`
  - `"Confirm rejection"` (`.btn-danger`) + `"Cancel"` (`.btn-ghost`)
- On confirm: draft is archived, removed from the list, feedback stored as `rating: negative`

On successful approval:
- Draft disappears from the list
- Toast notification: `"Post published!"` — `var(--color-success)`
- Next draft in the list is auto-selected

On successful rejection:
- Draft disappears from the list with a fade-out transition
- Toast: `"Draft rejected."` — neutral, auto-dismisses

---

## Page states

### Empty state (no pending drafts)
Both panels collapse into a centred empty state:
- Icon: Lucide `CheckCircle2`, `var(--icon-lg)`, `var(--color-success)`
- Heading: `"All caught up"`
- Sub-text: `"No agent drafts are waiting for review."`
- CTA: `"View run history"` — `.btn-ghost`, links to `/admin/agent/runs`

### Loading
- Draft list: 3 skeleton rows
- Detail panel: skeleton for title, metadata strip, and content blocks

---

## Responsive summary

| Element | lg+ | md | sm |
|---------|-----|----|----|
| Layout | Master-detail (side by side) | List → full-screen detail | List → full-screen detail |
| Draft list | 340px fixed | Full width list view | Full width list view |
| Detail panel | Fluid right | Full screen | Full screen |
| Action buttons | Horizontal row | Horizontal row | 2×2 grid |
