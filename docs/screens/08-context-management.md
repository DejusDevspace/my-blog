# Screen 08 — My Context (Settings)
**Route:** `/admin/settings/context`
**Auth required:** Yes (admin only)
**Document version:** 1.0

---

## Purpose
The page where the author maintains the personal context that powers the AI agent pipeline. This is not configuration — it's identity. The author describes who they are, what they care about, and what they're currently engaged with. The agent reads this on every run to select relevant topics and produce content that feels authentically authored.

Writing samples and tone notes are deliberately excluded. The agent infers voice and style from the author's published posts corpus via semantic search — this page handles only the factual personal context that the author actively maintains.

---

## Layout structure

```
┌──────────────────────────────────────────────────────┐
│           ADMIN SHELL (top bar + sidebar)            │
├──────────────────────────────────────────────────────┤
│  SETTINGS NAV (sub-nav tabs: My Context | Agent Settings) │
├──────────────────────────────────────────────────────┤
│                                                      │
│           CONTEXT FORM (centred, max 720px)          │
│                                                      │
│   Bio section                                        │
│   Interests / topics section                         │
│   What I'm learning section                          │
│   Lifestyle & personal context section               │
│                                                      │
│           [ Save changes ]                           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Max form width:** `720px`, centred within the main content area
**Breakpoint:** single-column on all screen sizes — this is a form page, no need for multi-column layout

---

## Components

### 1. Settings sub-navigation
**Position:** below the main content area header, above the form
**Style:** horizontal tab strip
- `"My Context"` tab — active (accent underline, `var(--color-accent)` text)
- `"Agent Settings"` tab — inactive, routes to `/admin/settings/agent`
- Font: `Space Grotesk`, `var(--text-body-sm)`, `var(--weight-medium)`
- Active indicator: `border-bottom: 2px solid var(--color-accent)`, tab text `var(--color-accent)`
- Inactive: `var(--color-text-secondary)`, hover `var(--color-text-primary)`
- Border bottom on the whole tab bar: `1px solid var(--color-border-subtle)`

---

### 2. Page header
- Heading: `"My Context"` — `Space Grotesk`, `var(--text-h2)`, `var(--weight-semibold)`
- Sub-text: `"This is what the AI agent knows about you. Keep it current for better drafts."` — `Space Grotesk`, `var(--text-body-sm)`, `var(--color-text-secondary)`
- Last saved indicator: `"Last saved 2 hours ago"` — `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`

---

### 3. Context form sections

Each section follows the same anatomy:
- **Section heading:** `Space Grotesk`, `var(--text-h4)`, `var(--weight-semibold)`, `var(--color-text-primary)`
- **Helper text:** `Space Grotesk`, `var(--text-body-sm)`, `var(--color-text-secondary)` — explains what the agent uses this field for
- **Input element** (varies per section)
- **Character count** (where applicable): `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`, right-aligned below the input
- **Section divider:** `1px solid var(--color-border-subtle)`, `margin: var(--space-8) 0`

---

#### Section: Bio

**Heading:** `"About me"`
**Helper text:** `"A short description of who you are, what you do, and what you currently work on. The agent uses this to contextualise post introductions and tailor the content to your background."`

**Input:** Textarea
- Rows: `6`
- Max-length: `800` characters
- Placeholder: `"e.g. I'm a mid-level AI Software Engineer based in Abuja. I build full-stack AI systems, enjoy working across the agent, backend, and frontend stacks, and I'm currently focused on multi-agent architectures and RAG systems."`
- Style: `.input`, `resize: vertical`, `font-family: var(--font-body)`

Character count: `"312 / 800"`

---

#### Section: Interests & topics

**Heading:** `"Interests & topics"`
**Helper text:** `"Topics you want the agent to write about. These feed directly into topic selection on each agent run. Be specific — the more specific the topic, the more focused the draft."`

**Input:** Tag-style multi-input
- Existing interests shown as removable pill tags: `.tag` + `×` remove button
- Text input at the end of the pills row for adding new interests
  - Placeholder: `"Add a topic..."`
  - Press Enter or comma to add
  - Dropdown suggestions from previously used interests on other runs (if applicable)
- Font for pills: `JetBrains Mono`, `var(--text-xs)`
- Max: 30 interests

**Example values (shown as placeholder state):**
`LangGraph` `FastAPI` `multi-agent systems` `RAG` `vector databases` `AI engineering` `career growth` `software architecture`

---

#### Section: What I'm learning

**Heading:** `"What I'm currently learning"`
**Helper text:** `"Technologies, concepts, or skills you're actively studying or exploring right now. The agent prioritises these for post topics — writing about what you're learning produces more authentic content."`

**Input:** Textarea
- Rows: `4`
- Max-length: `500` characters
- Placeholder: `"e.g. I'm currently going deep on LangGraph for stateful multi-agent systems, learning Rust for performance-critical side projects, and exploring how knowledge graphs can augment RAG pipelines."`
- Style: `.input`, `resize: vertical`

Character count: `"0 / 500"`

---

#### Section: Lifestyle & personal context

**Heading:** `"Lifestyle & personal context"`
**Helper text:** `"Anything personal that gives the agent cultural or lifestyle context — your background, where you're from, things you care about beyond tech. This is what makes the writing feel like it's from a person, not a bot."`

**Input:** Textarea
- Rows: `5`
- Max-length: `600` characters
- Placeholder: `"e.g. Nigerian software engineer. Grew up in Lagos, currently based in Abuja. Music lover — Afrobeats and alternative R&B. Fitness-focused. I prefer directness over corporate speak and I have a dry sense of humour."`
- Style: `.input`, `resize: vertical`

Character count: `"0 / 600"`

---

### 4. Save button area

**Position:** below the last section, sticky bottom on scroll for easy access

Layout:
- `"Save changes"` button: `.btn-primary`, `min-width: 160px`
- Save status to the right of the button (appears after save attempt):
  - Success: Lucide `Check` + `"Context saved and re-embedded"` — `var(--color-success)`
  - Error: Lucide `AlertCircle` + `"Failed to save. Try again."` — `var(--color-danger)`
- Font: `Space Grotesk`, `var(--text-body-sm)`

**On save:**
- Button shows loading spinner while request is in flight
- Backend re-embeds all context fields via `text-embedding-3-small` and upserts to `context_embeddings`
- Success message auto-dismisses after 4 seconds

---

### 5. Context status panel (informational, right sidebar on lg+)

On `lg+` breakpoints, a narrow right panel (240px) shows read-only agent usage context:

**Heading:** `"Used by agents"` — `JetBrains Mono`, `var(--text-xs)`, uppercase, `var(--color-text-tertiary)`

Entries:
- `"Bio"` → `"Orchestrator, Writer Agent"`
- `"Interests"` → `"Orchestrator (topic selection)"`
- `"Learning"` → `"Orchestrator (topic priority)"`
- `"Lifestyle"` → `"Writer Agent (voice)"`

Each entry:
- Field name: `JetBrains Mono`, `var(--text-xs)`, `var(--color-accent)`
- Used by: `Space Grotesk`, `var(--text-xs)`, `var(--color-text-secondary)`

Divider, then:

**Heading:** `"Embedding status"`
- Last embedded: `"2 hours ago"` — `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-secondary)`
- Status indicator: green dot + `"Up to date"` — or amber dot + `"Pending re-embed"` if unsaved changes exist

---

## Page states

### Unsaved changes
- Save button area becomes sticky (if not already in view)
- A subtle banner at the top of the form: `"You have unsaved changes"` — `var(--color-warning-muted)` background, `var(--color-warning)` text, `JetBrains Mono`, `var(--text-xs)`

### Empty state (first time, no context saved)
- Form renders empty with all placeholder text
- A blue info banner at the top: `"The agent won't run until you've saved your context."` — `var(--color-info-muted)` background, `var(--color-info)` text

### Loading
- Skeleton placeholders in each textarea and the interests pill row

---

## Responsive summary

| Element | lg+ | md | sm |
|---------|-----|----|----|
| Form column | 720px, left | fluid, padded | full width, 16px padding |
| Right info panel | 240px fixed right | hidden | hidden |
| Save button | inline at bottom | sticky bottom bar | sticky bottom bar |
| Settings sub-nav | tab strip | tab strip | tab strip (scrollable) |
