# ONEVO Frontend Redesign — "Selective Drama"

**Date:** 2026-04-08  
**Status:** Approved  
**Approach:** Selective Drama — glassmorphism on hero surfaces, flat on workhorse pages

---

## 1. Brand Identity

### Personality
Bold & Energetic. High contrast, confident, innovative. ONEVO should feel like a modern command center — not a generic HR tool.

### Typography
- **Display/Headings:** Outfit (variable, 400–800 weight). Rounded, friendly, professional.
- **Body/UI Text:** Geist (400–500 weight). Clean, readable, modern.
- **Monospace:** JetBrains Mono — IDs, timestamps, code snippets.

### Color System — "Violet Electric"

**Accent Palette:**
| Token | Value | Usage |
|:------|:------|:------|
| `--primary` | `#7c3aed` | Buttons, active states, primary actions |
| `--primary-hover` | `#6d28d9` | Button hover |
| `--primary-light` | `#8b5cf6` | Active nav items, selection highlights |
| `--primary-muted` | `#a78bfa` | Secondary accent text, chart labels |
| `--primary-subtle` | `rgba(139,92,246,0.04)` | Table row hover tint |
| `--primary-glow` | `rgba(139,92,246,0.25)` | Glow effects on glass borders |

**Gradient:**
Primary action gradient: `linear-gradient(135deg, #7c3aed, #8b5cf6)`

**Dark Theme Surfaces:**
| Token | Value | Usage |
|:------|:------|:------|
| `--bg-base` | `#09090b` | Page background |
| `--bg-raised` | `#18181b` | Cards, table backgrounds |
| `--bg-overlay` | `#27272a` | Hover backgrounds, dividers |
| `--border-default` | `rgba(255,255,255,0.06)` | Card/panel borders |
| `--border-hover` | `rgba(255,255,255,0.1)` | Hover state borders |
| `--text-primary` | `#fafafa` | Headings, primary text |
| `--text-secondary` | `#a1a1aa` | Body text, descriptions |
| `--text-muted` | `#71717a` | Labels, captions |
| `--text-disabled` | `#52525b` | Disabled states |

**Light Theme Surfaces:**
| Token | Value | Usage |
|:------|:------|:------|
| `--bg-base` | `#fafafa` | Page background |
| `--bg-raised` | `#ffffff` | Cards |
| `--bg-overlay` | `#f4f4f5` | Hover backgrounds |
| `--border-default` | `#e4e4e7` | Card borders |
| `--text-primary` | `#09090b` | Headings |
| `--text-secondary` | `#52525b` | Body text |
| `--text-muted` | `#a1a1aa` | Labels |

**Status Colors (fixed across themes):**
| Status | Color | Usage |
|:-------|:------|:------|
| Active/Success | `#22c55e` | Online, approved, healthy |
| Warning | `#f59e0b` | Pending, expiring soon |
| Critical/Error | `#ef4444` | Offline, rejected, critical alerts |
| Info | `#06b6d4` | Informational, on leave |
| Partial | `#f97316` | Partial attendance, incomplete |

**Theme Mode:** System-follows (`prefers-color-scheme`) with user override. Persisted in localStorage. Tenant branding can set a default.

---

## 2. Surface Treatment — Selective Drama

### Glass Surfaces (hero elements only)
Used on: sidebar, topbar, KPI stat cards, modals, command palette.

```css
.glass {
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

/* Light theme glass */
.light .glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 0, 0, 0.06);
}
```

Violet glow bleeds on important/active glass elements:
```css
.glass-glow {
  box-shadow: 0 0 16px rgba(124, 58, 237, 0.15);
  border-color: rgba(124, 58, 237, 0.3);
}
```

### Flat Surfaces (workhorse elements)
Used on: tables, forms, detail page sections, activity feeds, list pages.

```css
.flat {
  background: var(--bg-raised);
  border: 1px solid var(--border-default);
  border-radius: 8px;
}
```

No shadows by default. Shadows only on floating UI (dropdowns, popovers, modals).

---

## 3. Navigation — Pillar-Based Two-Level Sidebar

### Final Sidebar Structure (8 items)

```
Icon Rail (64px)          Expansion Panel (220px, on click)
─────────────────         ─────────────────────────────────
🏠 Home                   (no panel — navigates directly to dashboard)
👥 People                 → Employees, Leave
📡 Workforce Live         → Live Dashboard (tabs: Activity, Productivity, Online Status)
🏢 Organization           → Org Chart, Departments, Teams
📅 Calendar               (no panel — navigates directly)
📥 Inbox (badge)          (no panel — navigates directly)
🔧 Admin                  → Users & Roles, Audit Log, Agents, Devices, Compliance
⚙️ Settings               → General, Monitoring, Notifications, Integrations, Branding, Billing, Alert Rules
```

### Icon Rail (always visible)
- Width: 64px
- Glass surface: `rgba(10,10,15,0.85)` + `backdrop-filter: blur(16px)`
- ONEVO logo mark at top (stylized "O", not full wordmark)
- Pillar icons stacked vertically with 8px gap
- Active pillar: violet glow pip (`#8b5cf6`, `box-shadow: 0 0 12px rgba(139,92,246,0.25)`), brighter icon
- Bottom: user avatar (profile/logout popover) + theme toggle
- Right border: `rgba(255,255,255,0.06)`

### Expansion Panel (slides out on pillar click)
- Width: 220px
- Glass surface, slightly lighter: `rgba(20,20,28,0.9)`
- Pillar name as header: Outfit 600, violet
- Sub-items: icon + label, Geist 13px, `zinc-400` default, white on active
- Active sub-item: 3px violet left border + faint violet background tint
- Slide animation: `translateX` 200ms ease-out
- Pinnable on desktop ≥1280px (toggle pin icon at panel top)
- Collapsed state: only rail shows. Hover pillar → flyout tooltip

### Removed From Sidebar (absorbed into pages)
| Item | Now Lives In |
|:-----|:-------------|
| Onboarding | Employee creation flow |
| Performance | Employee profile section |
| Pay & Benefits | Employee profile section |
| Skills & Learning | Employee profile section |
| Documents | Employee profile section + bulk view under People |
| Complaints | Employee profile section |
| Expense | Employee profile sub-page |
| Activity | Workforce Live tab |
| Productivity | Workforce Live tab |
| Online Status | Workforce Live tab |
| ID Checks | Employee profile or Admin |
| Alerts/Exceptions | Inline layer on dashboard + contextual banners |
| Reports | Quick Search (⌘K) + dashboard charts |
| Departments | Inside Org Chart |
| Teams | Inside Org Chart |
| Job Families | Inside Settings or Org |
| Audit Log | Admin tab |
| Agents | Admin tab |
| Devices | Admin tab |
| Compliance | Admin tab |

### Permission Behavior
Entire pillars hide if user lacks section-level permission. Sub-items within a visible pillar also filter individually via `hasPermission()`.

---

## 4. Topbar

Height: 56px. Glass surface matching sidebar.

**Layout (left → right):**
- Hamburger (mobile <768px only) — opens sidebar overlay
- Breadcrumbs — Outfit 400, 13px. Segments clickable except last. `zinc-500` with current page in white
- Spacer
- Global Search pill — "Search... ⌘K". Glass surface, subtle border. Opens Command Palette
- Notification Bell — ghost button, violet dot badge with count. Popover with recent FYI notifications
- User Avatar — 32px circle. Dropdown: name, role, theme toggle, profile, logout

### Quick Search / Command Palette (⌘K)
- Full-screen overlay with centered glass modal (480px wide)
- Search input at top, categorized results: Navigation, Recent Employees, Actions
- Keyboard navigable (arrow keys + enter)
- Violet highlight on focused result row

### Notification Bell
Shows FYI-only updates (not actionable items — those go to Inbox):
- "John Doe was promoted to Senior Engineer"
- "Leave policy updated by admin"
- System announcements

---

## 5. Dashboard — Mission Control

The landing page. Follows **action → awareness → analysis** priority.

### Section Order

**1. Greeting Bar**
- "Good morning, Thiva" — Outfit 700, 24px, white
- Subtitle: today's date + one-line summary ("3 items need your attention")
- Right: quick action buttons (ghost) — "Add Employee", "Submit Leave"

**2. Primary KPIs (actionable, larger cards)**
- Glass cards, wider and taller than secondary
- Violet glow if count > 0 (e.g., pending approvals), red glow if critical
- Items: Pending Approvals, Open Alerts, Expiring Documents
- Each card: label (11px, uppercase, zinc-500), big number (Outfit 700, 32px), trend arrow, click navigates to relevant page

**3. Secondary KPIs (reference, standard size cards)**
- Glass cards, standard size
- Items: Total Employees, Attendance Rate, New Hires This Month, Avg Productivity Score
- Same structure but no glow treatment

**4. Upcoming Events + Quick Links**
- Left: next 5 calendar events in horizontal card strip (flat bordered cards)
- Right: pinned/most-visited pages — personalized shortcuts

**5. Activity Feed + Alerts**
- Left: Recent Activity — timeline with avatar, action, timestamp. Last 10 items. Flat surface
- Right: Active alerts — severity-colored left border. Click → relevant record. Flat surface

**6. Charts & Graphs**
- Left (60%): Attendance trend — area chart, violet gradient fill, last 30 days. Glass container
- Right (40%): Department headcount — ring chart, violet-to-lavender gradient
- Date range selector shared across charts
- Text summary above each chart ("Attendance averaged 94% this month, up 2%")

---

## 6. List Pages (Employees, Leave, etc.)

Workhorse pages — **flat surfaces, not glass**. Readability over drama.

### Structure
- **Page Header:** Title (Outfit 700, 24px) + primary action button (violet gradient). Secondary actions as ghost buttons
- **Filter Bar:** Search input, dropdown filters (department, status, date range), "Clear filters" link. URL state via `nuqs`
- **DataTable:** Bordered rows, alternating `zinc-900`/`zinc-950`. Row hover: faint violet tint. Sortable headers. Bulk selection checkboxes (violet check). Pagination at bottom
- **Row Actions:** Kebab menu (three dots) — view, edit, archive. No inline buttons
- **Empty State:** Illustrated placeholder with CTA
- **Bulk Actions:** Floating action bar at bottom when rows selected — export, assign, archive

### Table Details
- Density: 13px Geist, 40px row height
- Sticky header row on scroll
- Column resizing via drag

---

## 7. Detail Pages (Employee Profile, etc.)

Single scrollable page with collapsible sections — **no tabs** (except for truly separate concerns like Audit Log).

### Priority-Ordered Sections

**1. Identity Card (glass)**
- Avatar (64px), name (Outfit 700, 22px), job title, department, status badge (colored dot), hire date, reports to
- Right side: Edit button, More dropdown

**2. Quick Facts Strip**
- 4-5 inline stat pills: tenure, leave balance, last review score, salary band, next milestone
- Scannable in 2 seconds

**3. Alerts / Action Items**
- If anything needs attention (expiring visa, pending review, probation ending), it surfaces HERE
- Banner-style cards with severity-colored left border
- Click → opens the relevant action (e.g., renew visa form)

**4. Employment Details (expanded by default)**
- Current position, history, contract type
- Collapsible section header with chevron

**5. Pay & Benefits (permission-gated)**
- Salary, benefits, last revision
- Section doesn't render at all if unauthorized

**6. Documents (collapsed by default)**
- Recent docs list, upload area
- Expand on click

**7. Activity Timeline (collapsed by default)**
- Recent changes — who changed what, when
- Chronological feed

### Inline Editing
- Click edit icon on any section → fields become editable in-place
- Save/Cancel at section level, not page level

---

## 8. Forms & Wizards

### Simple Forms (Leave Request, Quick Edit)
- Slide-over panel from right (480px, glass surface)
- Keeps context visible behind overlay
- Fields stacked vertically, grouped by relevance
- Violet gradient submit button pinned at bottom
- Cancel dismisses, dirty-state warning only if changes made

### Complex Forms (Employee Onboarding)
- Full-page with progress stepper at top
- Steps: Personal Info → Employment → Pay & Benefits → Documents → Review
- Stepper states: completed (violet check), current (violet glow), upcoming (zinc-600)
- Scroll-snapped sections, not separate routes
- Review step at end — summary with inline edit
- Auto-save drafts every 30 seconds

### Validation
- Inline, immediate — field-level errors on blur, not on submit
- Required fields: violet asterisk (consistent with brand)

---

## 9. Animations

All animations respect `prefers-reduced-motion`.

### Transitions
- Page content: `opacity 0→1` + `translateY(4px→0)`, 150ms ease-out
- Sidebar panel: `translateX` 200ms ease-out
- Modals/slide-overs: backdrop fade + panel slide with spring easing

### Hover States
- KPI cards: `translateY(-2px)` + enhanced violet glow
- Table rows: `rgba(139,92,246,0.04)` background tint
- Buttons: gradient brightens, `scale(1.02)`
- Sidebar items: background tint, icon brightens

### Loading States
- Skeleton screens with violet-tinted shimmer (branded loading)
- KPI numbers: animated count-up on first load (400ms)
- Charts: progressive draw-in (line traces left-to-right)

### Alerts & Notifications
- Bell icon: single subtle shake on new notification
- Alert badges: gentle violet glow pulse (2s breathe cycle)
- Toasts: slide in from top-right, auto-dismiss 5s

---

## 10. Charts & Graphs

**Library:** Recharts with custom ONEVO theme wrapper.

### Color Strategy
- Primary series: violet gradient (`#7c3aed` → `#a78bfa`)
- Secondary series: cyan (`#06b6d4`)
- Tertiary: amber (`#f59e0b`), then zinc shades
- Gridlines: `zinc-800`. Axis labels: Geist 11px, `zinc-500`
- Tooltip: glass surface, white text, violet accent border

### Chart Types by Context
| Context | Chart Type |
|:--------|:-----------|
| Attendance trends | Area chart, violet gradient fill (20% opacity) |
| Department headcount | Ring/donut chart |
| Productivity over time | Multi-series line chart |
| Leave distribution | Horizontal bar chart |
| Alert severity | Stacked bar chart (red/yellow/orange) |
| KPI sparklines | Tiny inline line charts (no axes) |

### UX Rules
- Every chart has a text summary above it — insight in words, not just visuals
- Interactive: hover tooltips, click to filter
- Shared date range selector per page
- Export: PNG or CSV per chart

---

## 11. Naming Conventions

All user-facing labels use simple, everyday language.

| System Concept | User-Facing Label |
|:---------------|:------------------|
| Data Visualization | Charts & Graphs |
| Workforce Intelligence | Workforce |
| Exception Engine | Alerts |
| Command Palette | Quick Search |
| Compensation | Pay & Benefits |
| Grievance | Complaints |
| Presence | Online Status |
| Verification | ID Checks |
| Productivity Dashboard | Work Insights |
| Approvals | Inbox |
| Micro-interactions | Animations |

**Principle:** Every label passes the "would a non-technical HR manager understand this in 1 second?" test.

---

## 12. Responsive Breakpoints

| Breakpoint | Width | Behavior |
|:-----------|:------|:---------|
| Desktop | ≥1280px | Full rail + pinnable panel + content |
| Small Desktop | ≥1024px | Rail only + flyout on hover + content |
| Tablet | ≥768px | Hidden sidebar, hamburger → overlay |
| Mobile | <768px | Not optimized (Phase 2) |

---

## 13. Accessibility

- WCAG 2.1 AA compliance
- All glass surfaces maintain 4.5:1 contrast ratio for text
- Keyboard navigation: Tab through sidebar items, Enter to expand, Escape to collapse
- Screen reader: ARIA labels on all icon-only elements
- Focus rings: violet outline (2px, offset 2px) — visible, branded
- `prefers-reduced-motion`: all animations become instant
- `prefers-contrast: more`: glass effects disabled, solid backgrounds used instead

---

## 14. Inbox (formerly Approvals)

The personal action center — everything waiting for YOUR action.

**Contents:**
- Pending leave approvals
- Expense claims to review
- Onboarding sign-offs
- Transfer/promotion requests
- Alerts assigned to you
- Mentions and assigned tasks

**UI:**
- Single-column list, sorted by urgency then date
- Each item: icon, title, source, timestamp, action buttons (Approve/Reject or View)
- Badge count on sidebar icon shows total unresolved items
- Bulk approve/reject for similar items

**Distinction from Notification Bell:**
- Inbox = actionable (needs your decision)
- Bell = informational (FYI updates, no action needed)
