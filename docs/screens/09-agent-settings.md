# Screen 09 — Agent Settings (Settings)
**Route:** `/admin/settings/agent`
**Auth required:** Yes (admin only)
**Document version:** 1.0

---

## Purpose
Configuration control centre for the AI agent pipeline. The author sets how often the agent runs, triggers manual runs, monitors the last run status, and toggles notification preferences. Intentionally lightweight — the agent system handles complexity internally; this page exposes only the controls the author actually needs.

---

## Layout structure

```
┌──────────────────────────────────────────────────────┐
│           ADMIN SHELL (top bar + sidebar)            │
├──────────────────────────────────────────────────────┤
│  SETTINGS NAV (tabs: My Context | Agent Settings)    │
├──────────────────────────────────────────────────────┤
│                                                      │
│       AGENT SETTINGS FORM (centred, max 720px)       │
│                                                      │
│   Schedule section                                   │
│   Manual trigger section                             │
│   Notifications section                              │
│   Last run summary (read-only)                       │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Max form width:** `720px`, centred
**Single column on all breakpoints**

---

## Components

### 1. Settings sub-navigation
Identical to Screen 08. `"Agent Settings"` tab is active here.

---

### 2. Page header
- Heading: `"Agent Settings"` — `Space Grotesk`, `var(--text-h2)`, `var(--weight-semibold)`
- Sub-text: `"Control when and how the AI agent generates post drafts."` — `var(--text-body-sm)`, `var(--color-text-secondary)`

---

### 3. Schedule section

**Heading:** `"Generation schedule"`
**Helper text:** `"How often the agent should automatically run and generate a new draft. Drafts are always saved for your review — nothing publishes automatically."`

**Schedule selector:**
A set of preset options rendered as a visual option group (not a raw dropdown):

```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐
│   Daily        │  │   Weekly       │  │   Bi-weekly    │  │   Custom     │
│ Every day      │  │ Once a week    │  │ Twice a week   │  │  Set cron    │
└────────────────┘  └────────────────┘  └────────────────┘  └──────────────┘
```

- Each option is a selectable card: `background: var(--color-bg-surface)`, `border: 1px solid var(--color-border-default)`, `border-radius: var(--radius-lg)`, padding `var(--space-4)`
- Selected card: `border-color: var(--color-accent)`, `background: var(--color-accent-muted)`
- Title: `Space Grotesk`, `var(--text-body-sm)`, `var(--weight-semibold)`
- Sub-label: `Space Grotesk`, `var(--text-xs)`, `var(--color-text-secondary)`

**When "Custom" is selected**, a cron input expands below the option group:
- Label: `"Cron expression"`
- Input: `.input`, monospace font, placeholder: `"0 9 * * 1"` (every Monday at 9am)
- Below the input: human-readable translation updates live as the user types: `"Every Monday at 9:00 AM"` — `Space Grotesk`, `var(--text-body-sm)`, `var(--color-accent)`
- If invalid cron: `"Invalid cron expression"` in `var(--color-danger)` below the input

**Run time selector** (shown for all schedule options):
- Label: `"Preferred run time"`
- Dropdown: hour selector, 24-hour format — `"09:00"`, `"12:00"`, etc.
- Style: `.input`, `max-width: 120px`

**Schedule active toggle:**
- Label: `"Schedule active"`
- Toggle switch (right-aligned): on = `var(--color-success)` track, off = `var(--color-border-default)` track
- When toggled off: a muted notice appears: `"The agent will not run automatically while the schedule is paused."`

---

### 4. Manual trigger section

**Heading:** `"Run now"`
**Helper text:** `"Trigger a single agent run immediately. The agent will pick a topic from your context, research it, and save a draft for your review. You can watch the run live."`

**Content:**

Status indicator row:
- Last run: `"Last run: 2 days ago"` — `JetBrains Mono`, `var(--text-xs)`, `var(--color-text-secondary)`
- Last run status badge: `.badge-published` for completed, `.badge-draft` for failed
- `"View run log"` link: `var(--color-accent)`, routes to `/admin/agent/runs`

Action:
- `"Run agent now"` button: `.btn-primary`, Lucide `Play` icon, full width on sm / auto width on lg
- Disabled with spinner while a run is already in progress
- On click: sends POST to `/api/v1/admin/agent/run`, then routes to the run log page with the new run's ID to show the live stream

**Active run banner** (conditional — shown when a run is in progress):
- Background: `var(--color-accent-muted)`, `border: 1px solid var(--color-accent-border)`, `border-radius: var(--radius-lg)`
- Content: Lucide `Loader2` (spinning) + `"Agent is running..."` + `"View live log"` link
- Auto-dismisses when the run completes (polled every 5 seconds)

---

### 5. Notifications section

**Heading:** `"Email notifications"`
**Helper text:** `"Receive an email when the agent finishes generating a draft. The email contains the draft title and a direct link to the review page."`

**Toggle:**
- Label: `"Notify me when a draft is ready"`
- Toggle switch (right-aligned)
- Default: **off** (as decided in open questions resolution)
- When toggled on: a confirmation note appears below: `"You'll receive emails at [admin email]."` — `Space Grotesk`, `var(--text-body-sm)`, `var(--color-text-secondary)`

---

### 6. Last run summary (read-only)

**Heading:** `"Last agent run"`
**Style:** info card — `background: var(--color-bg-surface)`, `border: 1px solid var(--color-border-subtle)`, `border-radius: var(--radius-lg)`, padding `var(--space-5)`

Content grid (2 columns):
- `"Status"` / status badge
- `"Topic selected"` / topic text
- `"Model"` / `"GPT-4o"`
- `"Triggered by"` / `"Scheduler"` or `"Manual"`
- `"Started"` / datetime, `JetBrains Mono`, `var(--text-xs)`
- `"Completed"` / datetime or `"—"` if failed
- `"Output"` / link to the generated draft (`"View draft →"`) or `"—"` if failed

Label font: `JetBrains Mono`, `var(--text-xs)`, uppercase, `var(--color-text-tertiary)`
Value font: `Space Grotesk`, `var(--text-body-sm)`, `var(--color-text-primary)`

Footer of the card:
- `"View full run history"` — `var(--color-accent)`, `var(--text-body-sm)`, links to `/admin/agent/runs`

---

### 7. Save button area

- `"Save settings"` button: `.btn-primary`
- Success/error status to the right — same pattern as Screen 08

---

## Page states

### No runs yet (first-time setup)
- Last run summary card shows: `"No runs yet. Trigger your first run above."`
- All form fields default to: schedule = `Weekly`, time = `09:00`, schedule = active, notifications = off

### A run is in progress
- Manual trigger section shows the active run banner
- `"Run agent now"` button is disabled

### Schedule disabled
- Schedule selector cards are dimmed (`opacity: 0.5`)
- A muted notice: `"Re-enable the schedule to allow automatic runs."`

---

## Responsive summary

| Element | lg+ | md | sm |
|---------|-----|----|----|
| Form column | 720px centred | fluid, padded | full width, 16px padding |
| Schedule option cards | 4 in a row | 2×2 grid | 2×2 grid |
| Save button | inline | inline | sticky bottom bar |
