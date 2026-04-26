# Screen 06 — Post Editor
**Routes:** `/admin/posts/new` and `/admin/posts/[id]/edit`
**Auth required:** Yes (admin only)
**Document version:** 1.0

---

## Purpose
The primary content creation interface. A focused, distraction-minimised writing environment built around the BlockNote editor. Handles both creating new posts from scratch and editing existing ones (human-written or agent-drafted). The editor outputs clean markdown stored in the database.

---

## Layout structure

```
┌────────────────────────────────────────────────────────┐
│                  EDITOR TOP BAR                        │
│   (breadcrumb, save status, action buttons)            │
├───────────────────────────┬────────────────────────────┤
│                           │                            │
│    BLOCKNOTE EDITOR       │   POST SETTINGS PANEL      │
│    (main, fluid)          │   (right, 280px)           │
│                           │   Status, category, tags,  │
│                           │   slug, publish date       │
│                           │                            │
└───────────────────────────┴────────────────────────────┘
```

**Breakpoint behaviour:**
- `lg+`: Side-by-side — editor fluid left, settings panel 280px right
- `md` and below: Settings panel moves to a slide-in drawer, triggered by a `"Settings"` button in the editor top bar

---

## Components

### 1. Editor top bar
**Height:** `56px`
**Background:** `var(--color-bg-surface)`
**Border bottom:** `1px solid var(--color-border-subtle)`
**Position:** sticky top (below admin top bar), `z-index: 30`

Left slot:
- Back chevron: Lucide `ChevronLeft`, links back to `/admin` — `var(--color-text-secondary)`
- Breadcrumb: `Posts / New post` or `Posts / [Post title truncated]` — `Space Grotesk`, `var(--text-body-sm)`, `var(--color-text-secondary)`

Centre slot:
- Autosave status indicator (updates dynamically):
  - Saving: Lucide `Loader2` (spinning) + `"Saving..."` — `var(--color-text-tertiary)`
  - Saved: Lucide `Check` + `"Saved"` — `var(--color-success)`
  - Unsaved changes: Lucide `Circle` (filled, small) + `"Unsaved changes"` — `var(--color-warning)`
- Font: `JetBrains Mono`, `var(--text-xs)`

Right slot:
- `"Settings"` button (md and below only): Lucide `SlidersHorizontal` icon + text, `.btn-ghost`
- `"Save draft"` button: `.btn-ghost`
- `"Publish"` button: `.btn-primary` (changes to `"Update"` when editing an already-published post)

---

### 2. Post title input
**Position:** above the BlockNote editor, inside the editor column
**Padding:** `var(--space-10)` top, `var(--space-6)` bottom

Input styles:
- No visible input border or background — bare, full-width text input
- Font: `Montserrat`, `var(--text-display)`, `var(--weight-bold)`, `var(--color-text-primary)`
- Placeholder: `"Post title..."` — `var(--color-text-tertiary)`
- Line height: `var(--leading-tight)`
- On change: auto-generates a slug suggestion in the settings panel (user can override)
- `max-length`: none — author writes freely

---

### 3. BlockNote editor
**Position:** below title input, fluid width
**Background:** transparent (inherits `var(--color-bg-page)`)
**Min-height:** fills remaining viewport height
**Padding:** `0 var(--space-6)` horizontal, generous vertical spacing between blocks

BlockNote configuration:
- **Output format:** Markdown — BlockNote is configured to serialise all content to a markdown string on save
- **Theme:** custom theme matching the design system tokens (dark/light mode aware)
- **Placeholder text:** shown in the first empty paragraph block: `"Write something great..."` — `var(--color-text-tertiary)`

Enabled block types and their visual treatment:

| Block type | Visual |
|------------|--------|
| Paragraph | `Space Grotesk`, `var(--text-body-lg)`, `var(--leading-relaxed)` |
| Heading 1 | `Montserrat`, `var(--text-h1)`, bold |
| Heading 2 | `Montserrat`, `var(--text-h2)`, bold |
| Heading 3 | `Space Grotesk`, `var(--text-h3)`, semibold |
| Bulleted list | Standard indent, filled circle bullet in `var(--color-accent)` |
| Numbered list | Standard indent, number in `var(--color-accent)` |
| Code block | `JetBrains Mono`, `var(--text-caption)`, `background: var(--color-bg-subtle)`, `border: 1px solid var(--color-border-subtle)`, `border-radius: var(--radius-md)`, language selector dropdown top-right |
| Blockquote | Left border `3px solid var(--color-accent)`, italic, `var(--color-text-secondary)` |
| Image | Full-width with caption slot below; clicking image area opens Cloudinary upload dialog |
| Divider (---) | `1px solid var(--color-border-subtle)`, `margin: var(--space-8) 0` |
| Inline code | `JetBrains Mono`, `background: var(--color-bg-subtle)`, `padding: 2px 6px`, `border-radius: var(--radius-sm)` |

Slash command menu (`/`):
- Opens inline below the cursor
- Background: `var(--color-bg-elevated)`, `border: 1px solid var(--color-border-default)`, `border-radius: var(--radius-lg)`, `box-shadow: var(--shadow-md)`
- Searchable list of all block types
- Each option has a Lucide icon, block type name, and a short description
- Keyboard navigable (arrow keys + Enter)
- Font: `Space Grotesk`, `var(--text-body-sm)`

Image upload flow:
1. Author inserts an image block (via slash menu or drag-and-drop)
2. Upload dialog opens — file picker or drag-and-drop zone
3. On selection, file is sent to `/admin/uploads` endpoint which forwards to Cloudinary
4. On success, the Cloudinary CDN URL is inserted into the image block
5. Loading state: pulsing placeholder in image block dimensions while uploading

---

### 4. Post settings panel
**Width:** `280px`
**Background:** `var(--color-bg-surface)`
**Border left:** `1px solid var(--color-border-subtle)`
**Padding:** `var(--space-5)`
**Position:** sticky, scrolls independently of the editor

Sections (top to bottom):

#### Status
- Label: `"Status"` — `JetBrains Mono`, `var(--text-xs)`, uppercase, `var(--color-text-tertiary)`
- Current status badge: `.badge-published`, `.badge-draft`, etc.
- If post is `agent_draft`: a `"✦ AI-generated draft"` info banner in `var(--color-accent-muted)` background with agent icon

#### Publish
- `"Publish"` button (`.btn-primary`, full width) — or `"Unpublish"` if currently published
- `"Save as draft"` button (`.btn-ghost`, full width) below

#### Category
- Label: `"Category"` — same label style as Status
- Single-select dropdown: `"Projects"`, `"Thoughts"`, `"Blog"`, `"Docs"`
- Style: `.input`

#### Tags
- Label: `"Tags"`
- Tag input: type-to-add interface — typing a tag name shows matching existing tags as dropdown suggestions, pressing Enter or comma creates a new tag
- Existing tags shown as removable pills (`.tag` + `×` button)

#### Slug
- Label: `"URL slug"`
- Text input: `.input`, pre-populated from title (auto-slugified: lowercase, hyphens)
- Below the input: preview URL in muted text — `"d3jusdevspace.com/posts/[slug]"` — `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`
- Validation: red border if slug is already taken (checked on blur)

#### Metadata (collapsible, `"Advanced"` toggle)
- Reading time: auto-calculated from word count, display-only — `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-secondary)`
- Word count: display-only
- Created date: display-only
- Published date: display-only (if published)

---

## Autosave behaviour

- Every 30 seconds, if there are unsaved changes, the editor content is saved to `localStorage` with key `draft-[postId]` (or `draft-new` for new posts)
- On page load, if a `localStorage` draft exists and is newer than the server version, a banner appears:
  - `"You have unsaved local changes from [timestamp]. Restore them?"` with `"Restore"` and `"Dismiss"` buttons
  - Background: `var(--color-warning-muted)`, text `var(--color-warning)`
- On successful server save, the `localStorage` draft is cleared

---

## Publish confirmation

When clicking `"Publish"` on a new post or draft:
- A small confirmation popover appears anchored to the Publish button (not a full modal):
  - `"Publish this post?"` heading
  - `"It will be visible to all readers immediately."` — muted text
  - `"Publish now"` button (`.btn-primary`) + `"Cancel"` (`.btn-ghost`)
- On confirm: POST to API, status updated, success toast notification appears bottom-right:
  - `"Post published!"` — `var(--color-success)` background, `var(--color-text-inverse)` text, auto-dismisses after 3 seconds

---

## Agent-drafted post editing

When the editor is opened from the Agent Drafts review screen, the post settings panel shows an additional section at the top:

**Agent info banner:**
- Background: `var(--color-accent-muted)`, border `1px solid var(--color-accent-border)`, `border-radius: var(--radius-md)`
- Content: `"✦ Written by AI agent"` heading + `"Topic: [topic]"` + `"Generated: [date]"` + `"Model: [model name]"`
- Font: `JetBrains Mono`, `var(--text-xs)`

The `is_agent_authored` flag is locked — it cannot be changed from the editor UI even if content is edited.

---

## Page states

### New post
- Title input empty, editor empty with placeholder
- Settings panel: status = `draft`, all fields empty/default

### Editing existing post
- Title and editor pre-populated with saved content
- Settings panel: reflects current post metadata

### Saving
- Top bar status shows `"Saving..."` with spinner
- Action buttons briefly disabled

### Save error
- Status shows `"Save failed"` in `var(--color-danger)` + Lucide `AlertCircle` icon
- Toast notification: `"Failed to save. Check your connection."` — `var(--color-danger-muted)` background

---

## Responsive summary

| Element | lg+ | md | sm |
|---------|-----|----|----|
| Layout | Side by side | Editor full, settings in drawer | Editor full, settings in drawer |
| Settings panel | 280px fixed right | Slide-in drawer from right | Slide-in drawer from right |
| Title input | `var(--text-display)` | `var(--text-h1)` | `var(--text-h2)` |
| Top bar | Full | Full | Compressed (hide breadcrumb text) |
