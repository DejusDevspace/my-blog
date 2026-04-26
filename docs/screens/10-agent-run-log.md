# Screen 10 — Agent Run Log
**Route:** `/admin/agent/runs` and `/admin/agent/runs/[id]`
**Auth required:** Yes (admin only)
**Document version:** 1.0

---

## Purpose
Full visibility into the agent pipeline's activity — both historical runs and live-streaming active runs. Lets the author understand what the agent did, why it chose a topic, what it researched, and how it arrived at a draft. This is the observability surface that makes the agent system trustworthy and debuggable, and is a key portfolio showcase of production-grade AI engineering practice.

---

## Layout structure

Same master-detail pattern as Agent Drafts (Screen 07):

```
┌──────────────────────────────────────────────────────────┐
│              ADMIN SHELL (top bar + sidebar)             │
├────────────────────────┬─────────────────────────────────┤
│                        │                                 │
│   RUN LIST             │   RUN DETAIL PANEL              │
│   (left, 320px)        │   (right, fluid)                │
│                        │                                 │
│   - Scrollable list    │   - Run metadata                │
│   - Sorted newest-     │   - Node-by-node log            │
│     first              │   - Live stream (if active)     │
│   - Status badges      │   - Output draft link           │
│                        │                                 │
└────────────────────────┴─────────────────────────────────┘
```

**Breakpoint behaviour:**
- `lg+`: Master-detail side by side
- `md` and below: List view → tap run → full-screen detail (back button returns to list)

---

## Components

### 1. Page header

Left: `"Agent Run Log"` — `Space Grotesk`, `var(--text-h2)`, `var(--weight-semibold)`
Sub-text: `"A history of every agent run and its output."` — `var(--text-body-sm)`, `var(--color-text-secondary)`

Right: `"Run agent now"` shortcut button — `.btn-primary`, Lucide `Play` icon — triggers a manual run and immediately opens the new run's detail panel with live stream

---

### 2. Run list (left panel)

Each run row:

```
┌──────────────────────────────────────────────────┐
│  STATUS BADGE           TRIGGERED BY             │
│  Topic selected for this run (truncated)         │
│  Started [date] · [duration] · [model]           │
└──────────────────────────────────────────────────┘
```

- Padding: `var(--space-4)`
- Border bottom: `1px solid var(--color-border-subtle)`

Status badge (top left):
- `completed`: `.badge-published` (green)
- `running`: animated pulsing dot + `"Running"` — `var(--color-accent)` text
- `failed`: `.badge-danger` style — `var(--color-danger)` text

Triggered by (top right):
- `"Scheduler"` or `"Manual"` — `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`

Topic:
- Font: `Space Grotesk`, `var(--text-body-sm)`, `var(--weight-medium)`, `var(--color-text-primary)`
- Max 1 line, truncated

Meta line:
- Font: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`
- Format: `"Apr 18, 2026 · 42s · GPT-4o"`
- Duration shown in seconds if under a minute, `"1m 23s"` if longer
- If failed: duration replaced with `"Failed after 12s"` in `var(--color-danger)`

Active/selected row:
- `background: var(--color-accent-muted)`, `border-left: 3px solid var(--color-accent)`

---

### 3. Run detail panel (right)

#### When no run is selected (initial state)
Centred empty state:
- Icon: Lucide `Activity`, `var(--icon-lg)`, `var(--color-text-tertiary)`
- Text: `"Select a run to view its details"` — `var(--color-text-tertiary)`

---

#### Run detail — completed run

**Run header:**
- Status badge (large): `.badge-published` + `"Completed"` or failure equivalent
- Run ID: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)` — full UUID, copyable via small copy icon
- Triggered by + date + duration — same meta format as the list row

**Run metadata card:**
- Same 2-column grid style as Agent Settings last-run card (Screen 09)
- Fields: Status, Topic, Model, Triggered by, Started, Completed, Duration, Output post

**Output post link:**
- `"View generated draft →"` — `var(--color-accent)`, links to `/admin/agent-drafts` with the draft pre-selected
- Or `"View published post →"` if already approved and published

---

#### Run detail — node-by-node log

**Heading:** `"Execution log"` — `Space Grotesk`, `var(--text-h4)`, `var(--weight-semibold)`

The log is rendered as a vertical timeline of nodes, each with a collapsed/expanded state:

```
┌─────────────────────────────────────────────────────────┐
│  ● Orchestrator          completed in 1.2s    ▼         │
│  ┊  Topic selected: "Building production RAG pipelines"  │
│  ┊  Reason: Last covered "RAG" 18 days ago. High interest│
│  ┊  pgvector query: 3 similar recent posts checked       │
├─────────────────────────────────────────────────────────┤
│  ● Research Agent        completed in 8.4s    ▼         │
│  ┊  3 sources retrieved from Tavily                      │
│  ┊  Source 1: towardsdatascience.com · "RAG patterns..." │
│  ┊  Source 2: arxiv.org · "Hybrid retrieval..."          │
│  ┊  Source 3: langchain.dev · "Production RAG..."        │
├─────────────────────────────────────────────────────────┤
│  ● Tone/Feedback Agent   completed in 2.1s    ▼         │
│  ┊  5 feedback signals retrieved                         │
│  ┊  3 positive, 1 mixed, 1 negative                      │
│  ┊  Tone directive: 2 paragraphs (click to expand)       │
├─────────────────────────────────────────────────────────┤
│  ● Writer Agent          completed in 28.3s   ▼         │
│  ┊  Model: GPT-4o · Tokens: 1,842 prompt / 1,204 output  │
│  ┊  Draft generated: "Building production RAG pipelines" │
└─────────────────────────────────────────────────────────┘
```

Node row (collapsed):
- Left: coloured status dot — green for completed, amber for running, red for failed
- Node name: `Space Grotesk`, `var(--text-body-sm)`, `var(--weight-semibold)`, `var(--color-text-primary)`
- Duration: `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-tertiary)`, right-aligned
- Expand chevron: Lucide `ChevronDown` / `ChevronUp`, `var(--color-text-tertiary)`
- Bottom border between nodes: `1px solid var(--color-border-subtle)`

Node row (expanded):
- Background: `var(--color-bg-subtle)`, `border-radius: var(--radius-md)`, `padding: var(--space-4)`
- Content is structured text from `agent_runs.run_log[node_name]`
- Font: `Space Grotesk`, `var(--text-body-sm)`, `var(--color-text-secondary)`, `var(--leading-normal)`
- Key values (topic names, source URLs, token counts) rendered in `JetBrains Mono`, `var(--color-accent)`
- Links (source URLs) styled as `var(--color-accent)`, open in new tab

---

#### Run detail — live streaming run

When a run is `status: running`, the node log becomes a live stream:

**Live banner:**
- Full width: `background: var(--color-accent-muted)`, `border-bottom: 1px solid var(--color-accent-border)`
- Content: animated pulsing accent dot + `"Agent is running..."` + elapsed time counter (ticking up in real-time)
- Font: `JetBrains Mono`, `var(--text-xs)`, `var(--color-accent)`

**Node timeline (live):**
- Completed nodes: same styling as historical log, fully expanded by default during live view
- Currently executing node: amber pulsing dot + `"Running..."` status + a streaming log text area that appends lines as SSE events arrive:
  - Background: `var(--color-bg-subtle)`, monospace font, `var(--text-xs)`, auto-scrolls to bottom
  - Each new log line fades in
- Pending nodes: greyed out with `"Pending"` label — `var(--color-text-tertiary)`

**SSE connection:**
- Connects to `/api/v1/admin/agent/runs/[id]/log` on load if status is `running`
- Auto-reconnects on disconnect
- On run completion: banner updates to `"Completed in 42s"` with green styling, all nodes show final state

---

#### Run detail — failed run

- Run header status badge: `var(--color-danger)` styling
- Error card below the metadata:
  - Background: `var(--color-danger-muted)`, `border: 1px solid var(--color-danger)`, `border-radius: var(--radius-lg)`
  - Heading: `"Run failed"` — `Space Grotesk`, `var(--text-body-sm)`, `var(--weight-semibold)`, `var(--color-danger)`
  - Error message from `agent_runs.run_log.error`
  - The node at which failure occurred is highlighted red in the timeline
- `"Retry run"` button: `.btn-ghost`, Lucide `RefreshCw` icon — triggers a new run with the same topic

---

## Page states

### No runs yet
Both panels show centred empty state:
- Icon: Lucide `Bot`, `var(--icon-lg)`, `var(--color-text-tertiary)`
- Heading: `"No runs yet"`
- Sub-text: `"Trigger your first agent run to see the log here."`
- CTA: `"Run agent now"` — `.btn-primary`

### Loading
- Run list: 5 skeleton rows
- Detail panel: skeleton for header, metadata card, and 4 node rows

---

## Responsive summary

| Element | lg+ | md | sm |
|---------|-----|----|----|
| Layout | Master-detail | List → full detail | List → full detail |
| Run list | 320px fixed | Full-width list | Full-width list |
| Node log | Full with expand | Full with expand | Collapsed by default |
| Live stream text | Full | Full | Scrollable, reduced height |
