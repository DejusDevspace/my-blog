# Screen 02 — Post Detail
**Route:** `/posts/[slug]`
**Auth required:** No
**Document version:** 1.0

---

## Purpose
The core reading experience. Renders a single published post in full. Prioritises readability, focus, and navigability for long-form content. Includes the TOC sidebar for structured navigation and a comments section for reader engagement.

---

## Layout structure

```
┌─────────────────────────────────────────────────────────┐
│                       NAV BAR                           │
├─────────────────────────────────────────────────────────┤
│  READING PROGRESS BAR  (full width, accent colour)      │
├───────────────────┬─────────────────────┬───────────────┤
│                   │                     │               │
│   (left margin)   │   POST CONTENT      │  TOC SIDEBAR  │
│                   │   max-width: 720px  │  width: 260px │
│                   │                     │  (sticky)     │
│                   │                     │               │
│                   ├─────────────────────┤               │
│                   │     COMMENTS        │               │
│                   ├─────────────────────┤               │
│                   │   PREV / NEXT NAV   │               │
└───────────────────┴─────────────────────┴───────────────┘
│                       FOOTER                            │
└─────────────────────────────────────────────────────────┘
```

**Breakpoint behaviour:**
- `lg+`: Three-zone layout — left margin, reading column (720px centred), TOC sidebar right (260px)
- `md`: TOC sidebar collapses — becomes a floating `"Contents"` button (bottom right) that opens a drawer
- `sm`: Single column, no TOC button (drawer triggered from a top-of-post "Jump to section" link)

---

## Components

### 1. Reading progress bar
**Position:** fixed top, full viewport width, `z-index: 100`, sits below the nav bar
- `height: 3px`
- Background: `var(--color-accent)`
- Fills left-to-right as user scrolls through the post content
- Calculated: `scrollY / (documentHeight - viewportHeight) * 100`
- Animation: `transition: width 50ms linear` for smooth tracking

---

### 2. Post hero / header
**Width:** matches reading column (720px max)
**Padding top:** `var(--space-16)`

Contents (top to bottom):

1. **Breadcrumb** — `Home / Blog / [Category]`
   - Font: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`
   - Links: `var(--color-accent)` on hover

2. **Badge row** — flex, gap `var(--space-2)`
   - Category badge: `.tag`
   - Agent badge: `.badge-agent` with `"✦ Agent"` — conditional on `is_agent_authored`

3. **Post title**
   - Font: `Montserrat`, `var(--text-display)`, `var(--weight-bold)`
   - Colour: `var(--color-text-primary)`
   - Line height: `var(--leading-tight)`

4. **Meta row** — flex, align-centre, gap `var(--space-4)`
   - Published date: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-secondary)`
   - `·` separator
   - Reading time: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-secondary)`
   - `·` separator (if agent authored)
   - Agent label: `"Written by AI agent"` — `JetBrains Mono`, `var(--text-xs)`, `var(--color-accent)`

5. **Tags row** — flex wrap, gap `var(--space-2)`
   - All post tags rendered as `.tag` pills

6. **Divider** — `1px solid var(--color-border-subtle)`, `margin: var(--space-8) 0`

---

### 3. Post body content

**Container:** `.prose` wrapper applying all prose styles from the style guide
**Max-width:** `720px`
**Font:** `Space Grotesk`, `var(--text-body-lg)`, `var(--leading-relaxed)`

Markdown rendering handles:
- H2, H3, H4 headings (each gets an auto-generated `id` for TOC anchor linking)
- Paragraphs, bold, italic, strikethrough
- Ordered and unordered lists
- Blockquotes (left accent border in `var(--color-accent)`)
- Inline code — `JetBrains Mono`, `var(--color-bg-subtle)` background
- Code blocks — `JetBrains Mono`, syntax highlighted via `rehype-highlight`, language label shown in top-right of block
- Images — `max-width: 100%`, `border-radius: var(--radius-md)`, optional caption in muted text below
- Tables — full `.prose table` styles from style guide
- Horizontal rules
- Links — `var(--color-accent)`, underline offset 3px, open external links in new tab

**Code block anatomy:**
```
┌──────────────────────────────────────┬────────────┐
│ // language label (e.g. "python")   │  Copy icon │
├──────────────────────────────────────┴────────────┤
│                                                   │
│  const graph = new StateGraph(AgentState);        │
│  graph.addNode("orchestrator", orchestratorNode); │
│                                                   │
└───────────────────────────────────────────────────┘
```
- Language label: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`
- Copy button: Lucide `Copy` icon, `var(--icon-sm)`, on click copies content and briefly shows `Check` icon

---

### 4. TOC (Table of Contents) sidebar

**Position:** sticky, `top: 80px` (below nav)
**Width:** `260px`
**Visible:** `lg+` breakpoint only

Header:
- Label: `"On this page"` — `JetBrains Mono`, `var(--text-xs)`, uppercase, `var(--color-text-tertiary)`

TOC list:
- Generated from all `h2` and `h3` headings in the post content
- `h2` items: `Space Grotesk`, `var(--text-caption)`, `var(--weight-medium)`, `var(--color-text-secondary)`
- `h3` items: `Space Grotesk`, `var(--text-caption)`, `var(--weight-regular)`, `var(--color-text-tertiary)`, indented `var(--space-4)` left
- Active heading (tracked via `IntersectionObserver`):
  - Text colour: `var(--color-accent)`
  - Left border: `2px solid var(--color-accent)`
  - Padding left shifts to accommodate border
  - `transition: var(--transition-fast)`
- On click: smooth scroll to heading anchor, updates URL hash

**Mobile TOC (md and below):**
- A floating `"Contents"` button appears bottom-right: `position: fixed`, `bottom: var(--space-6)`, `right: var(--space-6)`
- Button style: `.btn-primary`, Lucide `List` icon + `"Contents"` label
- Opens a bottom drawer with full TOC list
- Drawer closes on item click or backdrop tap

---

### 5. Post footer

Below the last line of content, before comments:

1. **Tags row** (repeated for discoverability): same as hero tags
2. **Divider**
3. **Share row** (optional, non-essential):
   - `"Share this post"` label in muted text
   - Copy link button: Lucide `Link` icon, `.btn-ghost`

---

### 6. Prev / Next navigation

**Layout:** Two cards side by side (or stacked on mobile)
**Background:** `var(--color-bg-surface)`
**Border:** `1px solid var(--color-border-subtle)`, `var(--radius-lg)`

Left card (prev post):
- Label: `"← Previous"` — muted, `var(--text-xs)`, `JetBrains Mono`
- Post title: truncated to 2 lines

Right card (next post):
- Label: `"Next →"` — muted, `var(--text-xs)`, `JetBrains Mono`
- Post title: truncated to 2 lines

If no previous or next post exists, that card is either hidden or shows a greyed placeholder.

---

### 7. Comments section

**Position:** below the post body, above prev/next nav
**Heading:** `"Comments"` — `Space Grotesk`, `var(--text-h3)`, `var(--weight-semibold)` + comment count in muted text

#### Comment list

Each comment:
```
┌──────────────────────────────────────────────────┐
│  [AVATAR]  DisplayName or "Anonymous"  · date   │
│            ──────────────────────────────────    │
│            Comment body text                     │
└──────────────────────────────────────────────────┘
```
- Avatar: initials circle (first letter of display name, or `?` for anonymous)
  - Background: `var(--color-bg-elevated)`, text `var(--color-text-secondary)`
  - Size: 32px, `border-radius: var(--radius-full)`
- Name: `Space Grotesk`, `var(--text-body-sm)`, `var(--weight-medium)`, `var(--color-text-primary)`
- `"Anonymous"` shown in `var(--color-text-tertiary)` italic when no display name
- Date: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)` — relative time (`"3 days ago"`)
- Body: `Space Grotesk`, `var(--text-body-sm)`, `var(--color-text-secondary)`, `var(--leading-normal)`
- Border bottom: `1px solid var(--color-border-subtle)` between comments

#### Comment form

```
┌──────────────────────────────────────────────────┐
│  Leave a comment                                 │
│                                                  │
│  [ Name field — hidden when anon toggled on ]    │
│                                                  │
│  [ Comment textarea — 4 rows                  ] │
│                                                  │
│  [ ] Post anonymously                            │
│                                     [ Submit ]   │
│                                                  │
│  ⚠ Honeypot field (visually hidden)              │
└──────────────────────────────────────────────────┘
```

- Heading: `"Leave a comment"` — `Space Grotesk`, `var(--text-h4)`, `var(--weight-semibold)`
- Name input: `.input`, placeholder `"Your name"`, `max-length: 50` — hidden with `display: none` when anonymous toggle is on
- Textarea: `.input`, `rows: 4`, `resize: vertical`, placeholder `"Share your thoughts..."`
- Anonymous toggle: checkbox + label `"Post anonymously"` — `Space Grotesk`, `var(--text-body-sm)`
  - When checked: name field fades out, label changes to `"Posting as Anonymous"`
- Submit button: `.btn-primary`, `"Post comment"` label
- Honeypot: `<input type="text" name="website" tabindex="-1" aria-hidden="true" style="display:none">`
- On submit success: form clears, a `"Comment posted!"` inline success message appears in `var(--color-success)`
- On submit error (rate limit, validation): inline error message in `var(--color-danger)`

#### Empty comments state
- `"No comments yet"` in `var(--color-text-tertiary)`, centred above the form
- `"Be the first to leave one."` sub-text

---

## Page states

### Loading
- Nav, hero, and post title render immediately (SSG)
- Post body renders fully (SSG — no skeleton needed for static content)
- Comments section shows skeleton loaders (3 comment skeletons) while fetching

### 404 — post not found
- Clean error page with nav and footer retained
- Heading: `"Post not found"` — `Montserrat`, `var(--text-display)`
- Sub-text: `"This post doesn't exist or has been unpublished."`
- CTA: `"← Back to all posts"` — `.btn-primary`

---

## SEO & metadata

```html
<title>[Post Title] — d3jusdevspace</title>
<meta name="description" content="[Post excerpt, 160 chars max]" />
<meta property="og:title" content="[Post Title]" />
<meta property="og:description" content="[Post excerpt]" />
<meta property="og:type" content="article" />
<meta property="article:published_time" content="[ISO date]" />
<meta property="article:tag" content="[tag1], [tag2]" />
```

---

## Responsive summary

| Element | lg+ | md | sm |
|---------|-----|----|----|
| Reading column | 720px centred | fluid, padded | full width, 16px padding |
| TOC sidebar | 260px sticky right | hidden (floating btn) | hidden (top link) |
| Progress bar | full width | full width | full width |
| Prev/next nav | side by side | side by side | stacked |
| Comment form | full width | full width | full width |
