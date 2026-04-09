# Frontend Redesign — Documentation Update Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update all frontend design system docs and userflow docs to reflect the "Selective Drama" redesign — new typography, color system, navigation architecture, dashboard layout, naming conventions, and UX patterns.

**Architecture:** This is a documentation-only update across the `frontend/` and `Userflow/` folders. Every file that references old design decisions (Inter font, default blue, 30+ sidebar items, tab-based detail pages, "Exception Engine" naming, etc.) must be updated to match the approved spec at `docs/superpowers/specs/2026-04-08-frontend-redesign-design.md`.

**Tech Stack:** Markdown (Obsidian vault), no code changes.

**Reference Spec:** `docs/superpowers/specs/2026-04-08-frontend-redesign-design.md`

---

### Task 1: Update Color Tokens

**Files:**
- Modify: `frontend/design-system/foundations/color-tokens.md`

- [ ] **Step 1: Replace the CSS custom properties block**

Replace the entire `:root` block with the new Violet Electric palette:

```css
:root {
  /* Brand — Violet Electric */
  --primary: 263 70% 50.4%;           /* #7c3aed */
  --primary-hover: 263 78% 50.2%;     /* #6d28d9 */
  --primary-light: 258 90% 66.3%;     /* #8b5cf6 */
  --primary-muted: 258 90% 76.1%;     /* #a78bfa */
  --primary-foreground: 0 0% 98%;
  --primary-subtle: 258 90% 66.3% / 0.04;
  --primary-glow: 258 90% 66.3% / 0.25;

  /* Backgrounds */
  --background: 240 10% 3.9%;          /* #09090b */
  --foreground: 0 0% 98%;              /* #fafafa */
  --card: 240 5.9% 10%;                /* #18181b */
  --card-foreground: 0 0% 98%;
  --muted: 240 3.7% 15.9%;             /* #27272a */
  --muted-foreground: 240 5% 64.9%;    /* #a1a1aa */

  /* Borders */
  --border: 0 0% 100% / 0.06;
  --border-hover: 0 0% 100% / 0.1;
  --ring: 263 70% 50.4%;

  /* Status (fixed, not theme-dependent) */
  --status-active: 142 71% 45.3%;      /* #22c55e */
  --status-warning: 38 92% 50.2%;      /* #f59e0b */
  --status-critical: 0 84.2% 60.2%;    /* #ef4444 */
  --status-info: 189 94% 42.7%;        /* #06b6d4 */
  --status-partial: 24.6 95% 53.1%;    /* #f97316 */

  /* Severity */
  --severity-info: 189 94% 42.7%;
  --severity-warning: 38 92% 50.2%;
  --severity-critical: 0 84.2% 60.2%;

  /* Sidebar */
  --sidebar-background: 240 10% 3.9% / 0.85;
  --sidebar-foreground: 0 0% 98%;

  /* Glass surfaces */
  --glass-bg: 240 33% 5% / 0.85;
  --glass-border: 0 0% 100% / 0.06;
  --glass-glow: 263 70% 50.4% / 0.15;
}

.light {
  --background: 0 0% 98%;              /* #fafafa */
  --foreground: 240 10% 3.9%;          /* #09090b */
  --card: 0 0% 100%;                   /* #ffffff */
  --card-foreground: 240 10% 3.9%;
  --muted: 240 4.8% 95.9%;             /* #f4f4f5 */
  --muted-foreground: 240 3.8% 46.1%;  /* #71717a (as secondary) */
  --border: 240 5.9% 90%;              /* #e4e4e7 */
  --border-hover: 240 5.9% 85%;
  --sidebar-background: 0 0% 100% / 0.7;
  --glass-bg: 0 0% 100% / 0.7;
  --glass-border: 0 0% 0% / 0.06;
}
```

- [ ] **Step 2: Update the Semantic Color Usage table**

Replace the table with:

```markdown
| Purpose | Token | CSS Variable |
|:--------|:------|:-------------|
| Primary actions | `text-primary`, `bg-primary` | `--primary` |
| Primary hover | `hover:bg-primary-hover` | `--primary-hover` |
| Active/selected accent | `text-primary-light` | `--primary-light` |
| Muted accent text | `text-primary-muted` | `--primary-muted` |
| Subtle hover tint | `bg-primary-subtle` | `--primary-subtle` |
| Glow effects | `shadow-primary-glow` | `--primary-glow` |
| Page background | `bg-background` | `--background` |
| Card surface | `bg-card` | `--card` |
| Subtle background | `bg-muted` | `--muted` |
| Secondary text | `text-muted-foreground` | `--muted-foreground` |
| Borders | `border` | `--border` |
| Glass surface | `bg-glass` | `--glass-bg` |
| Glass border | `border-glass` | `--glass-border` |
| Active/online | `text-status-active` | `--status-active` |
| Warning | `text-status-warning` | `--status-warning` |
| Critical/error | `text-status-critical` | `--status-critical` |
| Info/on leave | `text-status-info` | `--status-info` |
```

- [ ] **Step 3: Add Gradient section**

Add after the table:

```markdown
## Gradients

| Name | Value | Usage |
|:-----|:------|:------|
| Primary gradient | `linear-gradient(135deg, #7c3aed, #8b5cf6)` | Primary action buttons |
| Chart fill | `linear-gradient(180deg, #7c3aed20, transparent)` | Area chart fills |
```

- [ ] **Step 4: Commit**

```bash
git add frontend/design-system/foundations/color-tokens.md
git commit -m "docs: update color tokens to Violet Electric palette"
```

---

### Task 2: Update Typography

**Files:**
- Modify: `frontend/design-system/foundations/typography.md`

- [ ] **Step 1: Replace the Font section**

Replace:
```markdown
## Font

- **Primary:** Inter (variable font) — clean, readable, good for data-dense UIs
- **Monospace:** JetBrains Mono — code snippets, IDs, timestamps
```

With:
```markdown
## Font

- **Display/Headings:** Outfit (variable, 400–800 weight) — rounded, friendly, professional. Strong character for dashboards.
- **Body/UI Text:** Geist (400–500 weight) — clean, readable, modern. Pairs with Outfit for contrast.
- **Monospace:** JetBrains Mono — code snippets, IDs, timestamps

### Font Loading

```tsx
// app/layout.tsx
import { Outfit, Geist, JetBrains_Mono } from 'next/font/google';

const outfit = Outfit({ subsets: ['latin'], variable: '--font-display' });
const geist = Geist({ subsets: ['latin'], variable: '--font-body' });
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' });
```
```

- [ ] **Step 2: Update the Scale table**

Replace the Scale table, changing font references from Inter to Outfit/Geist:

```markdown
## Scale

| Name | Size | Weight | Font | Usage |
|:-----|:-----|:-------|:-----|:------|
| `h1` | 2rem (32px) | 700 | Outfit | Page titles |
| `h2` | 1.5rem (24px) | 600 | Outfit | Section headers |
| `h3` | 1.25rem (20px) | 600 | Outfit | Card titles |
| `h4` | 1.125rem (18px) | 600 | Outfit | Subsection headers |
| `body` | 0.875rem (14px) | 400 | Geist | Default body text |
| `body-sm` | 0.8125rem (13px) | 400 | Geist | Table cells, secondary text |
| `caption` | 0.75rem (12px) | 400 | Geist | Labels, timestamps, badges |
| `metric` | 2rem (32px) | 700 | Outfit | KPI numbers |
| `metric-sm` | 1.5rem (24px) | 600 | Outfit | Secondary metrics |
```

- [ ] **Step 3: Update the Tailwind Classes examples**

Replace all `className` examples to use the new font variables:

```tsx
// Page title
<h1 className="font-display text-2xl font-bold tracking-tight">Employees</h1>

// Section header
<h2 className="font-display text-lg font-semibold">Department Overview</h2>

// Card title
<h3 className="font-display text-base font-semibold">Active Employees</h3>

// Body text
<p className="font-body text-sm text-foreground">...</p>

// Secondary text
<p className="font-body text-sm text-muted-foreground">...</p>

// Caption/label
<span className="font-body text-xs text-muted-foreground">Last updated 30s ago</span>

// KPI metric
<p className="font-display text-2xl font-bold tabular-nums">1,247</p>

// Monospace (IDs, timestamps)
<code className="font-mono text-xs">emp-a1b2c3d4</code>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/design-system/foundations/typography.md
git commit -m "docs: update typography to Outfit + Geist font pairing"
```

---

### Task 3: Update Navigation Patterns

**Files:**
- Modify: `frontend/design-system/patterns/navigation-patterns.md`

- [ ] **Step 1: Replace the Navigation Hierarchy diagram**

Replace the entire ASCII diagram at the top with the new pillar-based layout:

```markdown
## Navigation Hierarchy

```
┌─ Topbar ──────────────────────────────────────────────────────────┐
│  Breadcrumbs              [🔍 Search... ⌘K]   [🔔 3]  [Avatar ▼] │
├──────┬───────────┬────────────────────────────────────────────────┤
│      │           │                                                │
│ Rail │  Panel    │  Page Content                                  │
│ 64px │  220px    │                                                │
│      │ (slides)  │                                                │
│  🏠  │ ┌───────┐ │                                                │
│  👥  │ │People │ │                                                │
│  📡  │ │───────│ │                                                │
│  🏢  │ │Employ.│ │                                                │
│  📅  │ │Leave  │ │                                                │
│  📥  │ └───────┘ │                                                │
│  🔧  │           │                                                │
│  ⚙️  │           │                                                │
│      │           │                                                │
│ ──── │           │                                                │
│ 🧑‍💼  │           │                                                │
│  🌙  │           │                                                │
└──────┴───────────┴────────────────────────────────────────────────┘
```
```

- [ ] **Step 2: Replace the Sidebar section**

Replace the entire `## Sidebar` section (states table, section visibility, navigation config, rendering logic) with:

```markdown
## Sidebar — Pillar-Based Two-Level

### Architecture

The sidebar is a two-panel system:

1. **Icon Rail** (64px, always visible) — top-level pillars
2. **Expansion Panel** (220px, slides out on click) — sub-items for the active pillar

### Icon Rail

| Property | Value |
|:---------|:------|
| Width | 64px (`w-16`) |
| Surface | Glass: `rgba(10,10,15,0.85)` + `backdrop-filter: blur(16px)` |
| Right border | `rgba(255,255,255,0.06)` |
| Top element | ONEVO logo mark (stylized "O") |
| Bottom elements | User avatar + theme toggle |
| Active indicator | Violet glow pip: `#8b5cf6`, `box-shadow: 0 0 12px rgba(139,92,246,0.25)` |

### Expansion Panel

| Property | Value |
|:---------|:------|
| Width | 220px |
| Surface | Glass: `rgba(20,20,28,0.9)` + `backdrop-filter: blur(16px)` |
| Header | Pillar name, Outfit 600, violet |
| Items | Icon + label, Geist 13px, `zinc-400` default, white active |
| Active indicator | 3px violet left border + faint violet bg tint |
| Animation | `translateX` 200ms ease-out |
| Pin behavior | Pinnable on ≥1280px. Flyout tooltip on hover when collapsed |

### Pillar Configuration (8 items)

```tsx
interface Pillar {
  icon: LucideIcon;
  label: string;
  href?: string;             // Direct nav (no panel) — e.g., Home, Calendar
  permission?: string;
  feature?: string;
  badge?: () => number;
  items?: PillarItem[];      // Sub-items shown in expansion panel
}

interface PillarItem {
  icon: LucideIcon;
  label: string;
  href: string;
  permission?: string;
  feature?: string;
  badge?: () => number;
}

const pillars: Pillar[] = [
  // ── Home ──
  {
    icon: LayoutDashboard,
    label: 'Home',
    href: '/',
  },

  // ── People ──
  {
    icon: Users,
    label: 'People',
    permission: 'hr:read',
    items: [
      { icon: Users, label: 'Employees', href: '/people/employees', permission: 'employees:read' },
      { icon: CalendarDays, label: 'Leave', href: '/people/leave', permission: 'leave:read' },
    ],
  },

  // ── Workforce Live ──
  {
    icon: Activity,
    label: 'Workforce',
    permission: 'workforce:read',
    feature: 'workforceIntelligence',
    items: [
      { icon: Activity, label: 'Live Dashboard', href: '/workforce/live', permission: 'workforce:dashboard' },
    ],
    // Activity, Productivity, Online Status are tabs within Live Dashboard
  },

  // ── Organization ──
  {
    icon: Network,
    label: 'Organization',
    permission: 'org:read',
    items: [
      { icon: Network, label: 'Org Chart', href: '/org/chart', permission: 'org:read' },
      { icon: Building2, label: 'Departments', href: '/org/departments', permission: 'departments:read' },
      { icon: UsersRound, label: 'Teams', href: '/org/teams', permission: 'teams:read' },
    ],
  },

  // ── Calendar ──
  {
    icon: CalendarRange,
    label: 'Calendar',
    href: '/calendar',
    permission: 'calendar:read',
  },

  // ── Inbox ──
  {
    icon: Inbox,
    label: 'Inbox',
    href: '/inbox',
    permission: 'approvals:read',
    badge: () => useUnresolvedInboxCount(),
  },

  // ── Admin ──
  {
    icon: UserCog,
    label: 'Admin',
    permission: 'admin:access',
    items: [
      { icon: UserCog, label: 'Users & Roles', href: '/admin/users', permission: 'users:manage' },
      { icon: ScrollText, label: 'Audit Log', href: '/admin/audit', permission: 'audit:read' },
      { icon: Monitor, label: 'Agents', href: '/admin/agents', permission: 'agents:manage' },
      { icon: HardDrive, label: 'Devices', href: '/admin/devices', permission: 'devices:manage' },
      { icon: ShieldAlert, label: 'Compliance', href: '/admin/compliance', permission: 'compliance:manage' },
    ],
  },

  // ── Settings ──
  {
    icon: Settings,
    label: 'Settings',
    permission: 'settings:read',
    items: [
      { icon: Settings, label: 'General', href: '/settings/general', permission: 'settings:read' },
      { icon: SlidersHorizontal, label: 'Monitoring', href: '/settings/monitoring', permission: 'monitoring:configure' },
      { icon: Bell, label: 'Notifications', href: '/settings/notifications', permission: 'notifications:configure' },
      { icon: Plug, label: 'Integrations', href: '/settings/integrations', permission: 'integrations:manage' },
      { icon: Palette, label: 'Branding', href: '/settings/branding', permission: 'branding:manage' },
      { icon: CreditCard, label: 'Billing', href: '/settings/billing', permission: 'billing:read' },
      { icon: AlertTriangle, label: 'Alert Rules', href: '/settings/alert-rules', permission: 'exceptions:manage' },
    ],
  },
];
```

### Rendering Logic

```tsx
function Sidebar() {
  const { hasPermission } = usePermissions();
  const { isEnabled } = useFeatureFlags();
  const [activePillar, setActivePillar] = useState<string | null>(null);
  const [isPinned, setIsPinned] = useState(false);

  const visiblePillars = pillars.filter(pillar => {
    if (pillar.permission && !hasPermission(pillar.permission)) return false;
    if (pillar.feature && !isEnabled(pillar.feature)) return false;
    return true;
  });

  return (
    <>
      <IconRail
        pillars={visiblePillars}
        activePillar={activePillar}
        onPillarClick={(pillar) => {
          if (pillar.href) {
            router.push(pillar.href);
            setActivePillar(null);
          } else {
            setActivePillar(activePillar === pillar.label ? null : pillar.label);
          }
        }}
      />
      {activePillar && (
        <ExpansionPanel
          pillar={visiblePillars.find(p => p.label === activePillar)!}
          isPinned={isPinned}
          onPin={() => setIsPinned(!isPinned)}
          onClose={() => !isPinned && setActivePillar(null)}
        />
      )}
    </>
  );
}
```

### Collapsed State

When collapsed (rail only), hovering a pillar reveals a flyout with the section items:

```tsx
{isCollapsed ? (
  <HoverCard>
    <HoverCardTrigger asChild>
      <button className="flex items-center justify-center w-10 h-10 rounded-md">
        <pillar.icon className="h-5 w-5" />
      </button>
    </HoverCardTrigger>
    <HoverCardContent side="right" className="glass w-48 p-2">
      <p className="font-display text-sm font-semibold text-primary-light mb-2">{pillar.label}</p>
      {pillar.items?.map(item => (
        <a key={item.href} href={item.href} className="flex items-center gap-2 px-2 py-1.5 text-xs rounded-md hover:bg-primary-subtle">
          <item.icon className="h-4 w-4" />
          {item.label}
        </a>
      ))}
    </HoverCardContent>
  </HoverCard>
) : null}
```
```

- [ ] **Step 3: Update the Sidebar States table**

Replace the existing states table with:

```markdown
### Responsive States

| State | Rail | Panel | Trigger | Persistence |
|:------|:-----|:------|:--------|:------------|
| Full | 64px | 220px (pinned) | Default on ≥1280px | Zustand + localStorage |
| Rail only | 64px | Flyout on hover | Default on ≥1024px, or user unpins | Zustand + localStorage |
| Hidden | 0px | 0px | ≤768px | Responsive only |
| Overlay | 64px + 220px | Hamburger tap on ≤768px | Temporary overlay | Session only |
```

- [ ] **Step 4: Update the Topbar section**

Replace the Topbar table with:

```markdown
## Topbar

Height: 56px. Glass surface: `rgba(12,12,18,0.8)` + `backdrop-filter: blur(12px)`. Bottom border: `rgba(255,255,255,0.06)`.

| Element | Position | Behavior |
|:--------|:---------|:---------|
| Hamburger (≤768px) | Left | Opens sidebar overlay |
| Breadcrumbs | Left | Auto-generated from route. Outfit 400, 13px, `zinc-500`. Current page white |
| Quick Search | Center | Pill-shaped hint: "Search... ⌘K". Glass surface. Opens command palette |
| Notifications Bell | Right | FYI-only updates. Violet dot badge. Popover with recent items |
| User Avatar | Right | 32px circle. Dropdown: name, role, theme toggle, profile, logout |
```

- [ ] **Step 5: Update Command Palette section**

Rename `## Command Palette` to `## Quick Search (⌘K)` and update the component:

```tsx
function QuickSearch() {
  return (
    <CommandDialog className="glass">
      <CommandInput placeholder="Search employees, pages, actions..." className="font-body" />
      <CommandList>
        <CommandGroup heading="Navigation">
          <CommandItem onSelect={() => router.push('/people/employees')}>
            <Users className="h-4 w-4 mr-2" /> Employees
          </CommandItem>
          <CommandItem onSelect={() => router.push('/people/leave')}>
            <CalendarDays className="h-4 w-4 mr-2" /> Leave
          </CommandItem>
        </CommandGroup>
        <CommandGroup heading="Recent Employees">
          {recentEmployees.map(emp => (
            <CommandItem key={emp.id} onSelect={() => router.push(`/people/employees/${emp.id}`)}>
              <Avatar className="h-6 w-6 mr-2" /> {emp.name}
            </CommandItem>
          ))}
        </CommandGroup>
        <CommandGroup heading="Actions">
          <CommandItem onSelect={openCreateEmployee}>
            <Plus className="h-4 w-4 mr-2" /> Add Employee
          </CommandItem>
          <CommandItem onSelect={openCreateLeaveRequest}>
            <Plus className="h-4 w-4 mr-2" /> Submit Leave
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
```

- [ ] **Step 6: Update Notification Bell**

Update to clarify FYI-only role (actionable items go to Inbox):

```markdown
### Notification Bell

FYI-only updates — actionable items live in [[Inbox]].

```tsx
function NotificationBell() {
  const { data: unread } = useUnreadNotificationCount();

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unread > 0 && (
            <span className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center text-[10px] rounded-full bg-primary text-primary-foreground animate-count-bump">
              {unread > 99 ? '99+' : unread}
            </span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="glass w-80 p-0" align="end">
        <NotificationPanel />
      </PopoverContent>
    </Popover>
  );
}
```

**Distinction:**
- **Bell** = informational ("John was promoted", "Policy updated") — no action needed
- **Inbox** = actionable ("Leave request pending your approval") — needs your decision
```

- [ ] **Step 7: Commit**

```bash
git add frontend/design-system/patterns/navigation-patterns.md
git commit -m "docs: redesign navigation to pillar-based two-level sidebar with 8 items"
```

---

### Task 4: Update Elevation & Surface System

**Files:**
- Modify: `frontend/design-system/foundations/elevation.md`

- [ ] **Step 1: Add Glass Surface section**

Add a new section after the Shadow Scale:

```markdown
## Glass Surfaces (Selective Drama)

Glassmorphism is reserved for **hero elements only** — sidebar, topbar, KPI stat cards, modals, command palette.

### Glass Variants

| Variant | Background | Blur | Border | Usage |
|:--------|:-----------|:-----|:-------|:------|
| `glass` | `rgba(10,10,15,0.85)` | `blur(16px)` | `rgba(255,255,255,0.06)` | Sidebar, topbar |
| `glass-light` | `rgba(20,20,28,0.9)` | `blur(16px)` | `rgba(255,255,255,0.06)` | Expansion panel |
| `glass-glow` | Same as `glass` | `blur(16px)` | `rgba(124,58,237,0.3)` + `box-shadow: 0 0 16px rgba(124,58,237,0.15)` | Active/important glass elements |

### Light Theme Glass

```css
.light .glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 0, 0, 0.06);
}
```

### High Contrast Fallback

```css
@media (prefers-contrast: more) {
  .glass {
    background: var(--bg-raised);
    backdrop-filter: none;
    border: 1px solid var(--border-default);
  }
}
```

### What Does NOT Get Glass

- DataTables and list pages → flat bordered cards
- Form fields and detail page sections → flat bordered cards
- Activity feeds and timelines → flat bordered cards
- Charts containers on non-dashboard pages → flat bordered cards

These use the standard flat surface:

```css
.flat {
  background: var(--bg-raised);
  border: 1px solid var(--border-default);
  border-radius: 8px;
}
```
```

- [ ] **Step 2: Update the Cards — Always Flat rule**

Update the "Cards — Always Flat" section to clarify the selective drama approach:

```markdown
### Cards — Selective

- **Glass cards:** KPI stat cards on dashboard, sidebar panels, modals
- **Flat cards:** Data tables, form sections, detail page sections, activity feeds
- Flat cards use borders (`border`) not shadows. Shadows only for floating UI
- Glass cards on dashboard get violet glow when they represent actionable items (pending approvals, alerts)
```

- [ ] **Step 3: Commit**

```bash
git add frontend/design-system/foundations/elevation.md
git commit -m "docs: add glass surface system for selective drama approach"
```

---

### Task 5: Update Motion & Animation

**Files:**
- Modify: `frontend/design-system/foundations/motion.md`

- [ ] **Step 1: Add branded animation patterns**

Add these new patterns to the `## Animation Patterns` section:

```markdown
### KPI Card Hover

```css
@keyframes card-lift {
  to { transform: translateY(-2px); }
}

.kpi-card:hover {
  animation: card-lift 150ms ease-out forwards;
  box-shadow: 0 0 20px rgba(124, 58, 237, 0.2);
  border-color: rgba(124, 58, 237, 0.3);
}
```

### Violet Shimmer (Branded Skeleton Loading)

```css
@keyframes violet-shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.skeleton-violet {
  background: linear-gradient(
    90deg,
    var(--bg-raised) 25%,
    rgba(139, 92, 246, 0.08) 50%,
    var(--bg-raised) 75%
  );
  background-size: 200% 100%;
  animation: violet-shimmer 1.5s ease-in-out infinite;
}
```

### KPI Number Count-Up

```tsx
// Animated number transition on first load
<motion.span
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.4 }}
>
  {animatedValue}
</motion.span>
```

### Chart Progressive Draw

```tsx
// Line charts trace left-to-right on mount
<Area
  animationBegin={0}
  animationDuration={800}
  animationEasing="ease-out"
/>
```

### Alert Badge Pulse

```css
@keyframes alert-breathe {
  0%, 100% { box-shadow: 0 0 8px rgba(124, 58, 237, 0.2); }
  50% { box-shadow: 0 0 16px rgba(124, 58, 237, 0.4); }
}

.alert-badge {
  animation: alert-breathe 2s ease-in-out infinite;
}
```

### Page Content Enter

```css
@keyframes page-enter {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-content {
  animation: page-enter 150ms ease-out;
}
```

### Sidebar Panel Slide

```css
.expansion-panel {
  transition: transform 200ms ease-out;
}

.expansion-panel[data-state="closed"] {
  transform: translateX(-100%);
}

.expansion-panel[data-state="open"] {
  transform: translateX(0);
}
```
```

- [ ] **Step 2: Update Sidebar Collapse pattern**

Replace the existing sidebar collapse animation to match the new pillar-based system:

```markdown
### Sidebar Panel Expand/Collapse

```css
/* Expansion panel slides in from left */
.expansion-panel {
  transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1);
}
```
```

- [ ] **Step 3: Commit**

```bash
git add frontend/design-system/foundations/motion.md
git commit -m "docs: add branded animation patterns for selective drama"
```

---

### Task 6: Update Dark Mode / Theming

**Files:**
- Modify: `frontend/design-system/theming/dark-mode.md`

- [ ] **Step 1: Update Strategy section**

Replace the strategy to reflect system-follows with user override:

```markdown
## Strategy

- **Default:** System preference (`prefers-color-scheme`)
- **User override:** Toggle in sidebar bottom + user dropdown. Overrides system when set.
- **Persistence:** `localStorage` key `theme` — values: `system` | `light` | `dark`
- **Tenant default:** Tenant branding can set a default theme. User override still takes precedence.
- **Dark is the hero mode:** The "Selective Drama" glass aesthetic is designed dark-first. Light mode is fully supported but the brand showcase is dark.
```

- [ ] **Step 2: Update the Root Layout implementation**

Replace the root layout code to use the new theme provider:

```tsx
// app/layout.tsx
import { Outfit, JetBrains_Mono } from 'next/font/google';
import localFont from 'next/font/local';

const outfit = Outfit({ subsets: ['latin'], variable: '--font-display' });
const geist = localFont({ src: './fonts/Geist-Variable.woff2', variable: '--font-body' });
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' });

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning className={`${outfit.variable} ${geist.variable} ${jetbrainsMono.variable}`}>
      <body className="font-body">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

- [ ] **Step 3: Update Color Token Mapping to use new palette**

Replace the mapping table with new Violet Electric values for both modes.

- [ ] **Step 4: Add glass surface adaptation note**

Add to Dark Mode Rules:

```markdown
### Glass Surfaces in Light Mode

Glass surfaces use different opacity values in light mode:
- Dark: `rgba(10, 10, 15, 0.85)` — frosted dark glass
- Light: `rgba(255, 255, 255, 0.7)` — frosted white glass
- `backdrop-filter: blur(16px)` remains the same
- Violet glow effects use lower opacity in light mode (`0.1` vs `0.25`)
```

- [ ] **Step 5: Commit**

```bash
git add frontend/design-system/theming/dark-mode.md
git commit -m "docs: update dark mode to system-follows with selective drama glass rules"
```

---

### Task 7: Update Layout Patterns

**Files:**
- Modify: `frontend/design-system/patterns/layout-patterns.md`

- [ ] **Step 1: Replace the Dashboard Layout diagram**

Replace the existing ASCII diagram with the new pillar-based layout:

```markdown
## Dashboard Layout

```
┌──────────────────────────────────────────────────────────┐
│ Topbar (glass) — breadcrumbs, search, bell, avatar       │
├──────┬──────────┬────────────────────────────────────────┤
│      │          │                                        │
│ Rail │  Panel   │  Page Content                          │
│ 64px │  220px   │                                        │
│glass │  glass   │  (scrollable)                          │
│      │ (slides) │                                        │
│      │          │                                        │
│      │          │                                        │
│      │          │                                        │
│      │          │                                        │
└──────┴──────────┴────────────────────────────────────────┘
```
```

- [ ] **Step 2: Replace the Sidebar Navigation tree**

Replace the old tree with the 8-pillar structure:

```markdown
## Sidebar Pillars

```
ONEVO (logo mark)
├── 🏠 Home                    → Dashboard (direct nav)
├── 👥 People                  → Employees, Leave
├── 📡 Workforce               → Live Dashboard (tabs: Activity, Work Insights, Online Status)
├── 🏢 Organization            → Org Chart, Departments, Teams
├── 📅 Calendar                → Calendar (direct nav)
├── 📥 Inbox (badge)           → Approvals, tasks, mentions
├── 🔧 Admin                   → Users & Roles, Audit Log, Agents, Devices, Compliance
└── ⚙️ Settings                → General, Monitoring, Notifications, Integrations, Branding, Billing, Alert Rules
```
```

- [ ] **Step 3: Update the Dashboard Page pattern**

Replace the dashboard page layout to follow action → awareness → analysis:

```markdown
### Dashboard Page (Home)

Follows **action → awareness → analysis** priority:

```
Greeting Bar ("Good morning, Thiva" + quick actions)
Primary KPIs (larger glass cards — actionable: approvals, alerts, expiring docs)
Secondary KPIs (standard glass cards — reference: total employees, attendance, new hires)
Upcoming Events strip + Quick Links (pinned/most-visited pages)
Activity Feed (left) + Active Alerts (right) — flat surfaces
Charts & Graphs (attendance trend, dept headcount) — glass containers
```
```

- [ ] **Step 4: Update the Detail Page pattern**

Replace the tab-based detail page with the scrollable section approach:

```markdown
### Detail Page (Employee Profile, etc.)

Single scrollable page with collapsible sections — **no tabs** (except Audit Log).

```
Identity Card (glass) — avatar, name, title, dept, status, hire date, reports to
Quick Facts Strip — tenure, leave balance, review score, salary band, next milestone
Alerts / Action Items — expiring visa, pending review, probation ending
Employment Details (expanded by default, collapsible)
Pay & Benefits (permission-gated — hidden if unauthorized)
Documents (collapsed by default)
Activity Timeline (collapsed by default)
```

Deep-linking via anchor links to sections: `/people/employees/abc123#pay-benefits`
```

- [ ] **Step 5: Update the Sidebar width values in the table**

Replace sidebar width references:

```markdown
| Sidebar width (rail) | 64px | `w-16` |
| Sidebar width (panel) | 220px | `w-[220px]` |
```

- [ ] **Step 6: Commit**

```bash
git add frontend/design-system/patterns/layout-patterns.md
git commit -m "docs: update layouts to pillar sidebar, action-priority dashboard, scrollable detail pages"
```

---

### Task 8: Update App Structure & Routing

**Files:**
- Modify: `frontend/architecture/app-structure.md`
- Modify: `frontend/architecture/routing.md`

- [ ] **Step 1: Update the Route Tree in app-structure.md**

Update route paths to reflect new pillar structure. Key changes:
- `/hr/employees` → `/people/employees`
- `/hr/leave` → `/people/leave`
- `/hr/onboarding` → removed (part of employee creation flow)
- `/hr/performance`, `/hr/payroll`, `/hr/skills`, `/hr/documents`, `/hr/grievance`, `/hr/expense` → removed from routes (sections within employee profile)
- `/workforce/dashboard` → `/workforce/live`
- `/workforce/activity`, `/workforce/productivity`, `/workforce/presence`, `/workforce/exceptions`, `/workforce/verification` → removed (tabs within live dashboard or employee profile)
- `/approvals` → `/inbox`
- `/reports` → removed from routes (accessible via Quick Search)
- Add `/inbox` route

- [ ] **Step 2: Update the Module → Route Mapping table**

Update to reflect reduced route count and new paths.

- [ ] **Step 3: Update the Layout System**

Update Dashboard Layout description:

```markdown
### Dashboard Layout (`(dashboard)/layout.tsx`)
- **Icon Rail:** 64px glass sidebar with 8 pillar icons, always visible on desktop
- **Expansion Panel:** 220px glass panel, slides out on pillar click, pinnable
- **Topbar:** Glass surface. Quick Search (⌘K), notification bell (FYI only), user menu
- **Main content:** Breadcrumbs + page content
- **Pillar visibility:** Permission-gated via `hasPermission()` — checks role permissions AND employee-level overrides
```

- [ ] **Step 4: Update Page Count table**

```markdown
| Section | Pages |
|---------|-------|
| Auth | 4 |
| People (Employees + Leave) | ~12 |
| Workforce Live | ~4 |
| Org | 4 |
| Calendar | 2 |
| Inbox | 1 |
| Admin | ~6 |
| Settings | 8 |
| **Total** | **~41** |
```

- [ ] **Step 5: Update routing.md — Route Groups**

Update route groups to match new structure:
- `(dashboard)/people/` instead of `(dashboard)/hr/`
- `(dashboard)/inbox/` instead of `(dashboard)/approvals/`
- Remove routes for modules absorbed into profiles/tabs

- [ ] **Step 6: Update routing.md — Navigation State**

```tsx
const pathname = usePathname();
const activePillar = pathname.split('/')[1]; // 'people' | 'workforce' | 'org' | 'calendar' | 'inbox' | 'admin' | 'settings'
const activeItem = pathname.split('/')[2];   // 'employees' | 'leave' | 'live' | 'chart' | etc.
```

- [ ] **Step 7: Update routing.md — Breadcrumb Generation**

Update examples to use new names:
```
People > Employees > John Doe
People > Leave > Calendar
Workforce > Live Dashboard
Settings > Alert Rules
```

- [ ] **Step 8: Commit**

```bash
git add frontend/architecture/app-structure.md frontend/architecture/routing.md
git commit -m "docs: update routes and app structure to match pillar-based navigation"
```

---

### Task 9: Update Design System README

**Files:**
- Modify: `frontend/design-system/README.md`

- [ ] **Step 1: Update the description**

Replace:
```markdown
**shadcn/ui + Radix + Tailwind CSS** — accessible primitives, full customization, information-dense dashboard aesthetic.
```

With:
```markdown
**shadcn/ui + Radix + Tailwind CSS** — "Selective Drama" design language. Glassmorphism on hero surfaces (sidebar, stat cards, modals), flat on workhorse pages (tables, forms, detail sections). Violet Electric accent palette. Outfit + Geist typography.
```

- [ ] **Step 2: Update Key Principles**

Replace the principles list:

```markdown
## Key Principles

1. **Selective Drama** — glass surfaces for hero elements (sidebar, KPI cards, modals), flat for workhorse elements (tables, forms, detail sections)
2. **Action → Awareness → Analysis** — dashboard and page layouts prioritize what needs user action first, then context, then deep data
3. **8-pillar navigation** — icon rail + expansion panel. Everything else is discoverable within pages or via Quick Search
4. **Information density** — compact tables, small cards, 14px body text. This is a work tool, not a marketing site
5. **Status at a glance** — color-coded badges, pulsing dots, severity indicators
6. **Permission-aware** — components hide or mask content based on permissions (role + employee-level overrides)
7. **Accessible** — WCAG 2.1 AA, keyboard nav, screen reader support. Glass degrades gracefully under `prefers-contrast: more`
8. **Desktop-first** — optimized for ≥1280px, functional at 768px, not optimized below
9. **Simple naming** — every label passes the "would a non-technical HR manager understand this in 1 second?" test
```

- [ ] **Step 3: Commit**

```bash
git add frontend/design-system/README.md
git commit -m "docs: update design system README with Selective Drama identity"
```

---

### Task 10: Update Frontend README

**Files:**
- Modify: `frontend/README.md`

- [ ] **Step 1: Update the header**

Replace:
```markdown
**Next.js 14 App Router** | React 18 | TypeScript | TanStack Query | Zustand | shadcn/ui | Tailwind CSS | SignalR
```

With:
```markdown
**Next.js 14 App Router** | React 18 | TypeScript | TanStack Query | Zustand | shadcn/ui | Tailwind CSS | SignalR | Outfit + Geist | Violet Electric
```

- [ ] **Step 2: Commit**

```bash
git add frontend/README.md
git commit -m "docs: update frontend README with new design identity"
```

---

### Task 11: Update Component Catalog

**Files:**
- Modify: `frontend/design-system/components/component-catalog.md`

- [ ] **Step 1: Add Glass components**

Add to the Composed Components section:

```markdown
### Glass Components

| Component | Props | Usage |
|:----------|:------|:------|
| `GlassCard` | `glow?: boolean` | Glass surface card. `glow` adds violet border glow for actionable items |
| `GlassSurface` | `variant?: 'default' \| 'light'` | Base glass surface wrapper |
| `IconRail` | `pillars: Pillar[]` | Left nav rail with pillar icons |
| `ExpansionPanel` | `pillar: Pillar, isPinned: boolean` | Slide-out sub-navigation panel |
| `InboxBadge` | — | Inbox count badge with violet glow pulse |
```

- [ ] **Step 2: Update Status Colors**

Update color references from raw Tailwind to semantic tokens:

```markdown
## Status Colors

| Status | Token | Usage |
|:-------|:------|:------|
| Active | `text-status-active` / `bg-status-active` | Online, approved, healthy |
| Warning | `text-status-warning` / `bg-status-warning` | Idle, pending, expiring |
| Critical | `text-status-critical` / `bg-status-critical` | Offline, rejected, critical |
| Info | `text-status-info` / `bg-status-info` | On leave, informational |
```

- [ ] **Step 3: Commit**

```bash
git add frontend/design-system/components/component-catalog.md
git commit -m "docs: add glass components and update status color tokens"
```

---

### Task 12: Update Spacing (Sidebar Widths)

**Files:**
- Modify: `frontend/design-system/foundations/spacing.md`

- [ ] **Step 1: Update Layout Spacing table**

Change sidebar width entries:

Replace:
```
| Sidebar width (expanded) | 256px | `w-64` |
| Sidebar width (collapsed) | 64px | `w-16` |
```

With:
```
| Sidebar rail width | 64px | `w-16` |
| Sidebar panel width | 220px | `w-[220px]` |
| Sidebar total (rail + panel) | 284px | — |
```

- [ ] **Step 2: Commit**

```bash
git add frontend/design-system/foundations/spacing.md
git commit -m "docs: update sidebar spacing for pillar-based layout"
```

---

### Task 13: Update Iconography

**Files:**
- Modify: `frontend/design-system/foundations/iconography.md`

- [ ] **Step 1: Update the Navigation icon map**

Replace the navigation icon list to match the 8 pillars:

```markdown
### Navigation (Sidebar Pillars)

| Icon | Component | Pillar |
|:-----|:----------|:-------|
| `LayoutDashboard` | Home | Dashboard |
| `Users` | People | Employees, Leave |
| `Activity` | Workforce | Live Dashboard |
| `Network` | Organization | Org Chart, Depts, Teams |
| `CalendarRange` | Calendar | Calendar |
| `Inbox` | Inbox | Approvals, tasks, mentions |
| `UserCog` | Admin | Users & Roles, Audit, Agents, Devices, Compliance |
| `Settings` | Settings | General, Monitoring, Notifications, Integrations, Branding, Billing, Alert Rules |
```

- [ ] **Step 2: Update Sidebar Nav Item pattern**

```tsx
// Pillar icon in rail
<button className="flex items-center justify-center w-10 h-10 rounded-md glass">
  <Users className="h-5 w-5 text-muted-foreground" />
</button>

// Active pillar — violet glow
<button className="flex items-center justify-center w-10 h-10 rounded-md glass-glow">
  <Users className="h-5 w-5 text-primary-light" />
</button>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/design-system/foundations/iconography.md
git commit -m "docs: update icon map for 8-pillar navigation"
```

---

### Task 14: Update Tenant Branding

**Files:**
- Modify: `frontend/design-system/theming/tenant-branding.md`

- [ ] **Step 1: Update customizable tokens**

Add glass surface customization and theme default:

```markdown
### Additional Customizable Properties

| Property | Default | Scope |
|:---------|:--------|:------|
| Default theme | `system` | Tenant can set `dark` or `light` as default (user override still applies) |
| Glass opacity | `0.85` | Tenant can adjust glass surface opacity |
| Accent glow intensity | `0.15` | Tenant can adjust violet glow intensity |
```

- [ ] **Step 2: Commit**

```bash
git add frontend/design-system/theming/tenant-branding.md
git commit -m "docs: add glass and theme customization to tenant branding"
```

---

### Task 15: Update Userflow — Profile Management

**Files:**
- Modify: `Userflow/Employee-Management/profile-management.md`

- [ ] **Step 1: Update Step 2 — View Profile Sections**

Replace the tabbed layout with scrollable sections:

```markdown
### Step 2: View Profile Sections
- **UI:** Single scrollable page with collapsible sections (no tabs):
  1. **Identity Card** (glass): Name, photo, title, dept, status badge, hire date, reports to
  2. **Quick Facts Strip**: Tenure, leave balance, last review score, salary band, next milestone
  3. **Alerts / Action Items**: Expiring visa, pending review, probation ending (if any)
  4. **Employment Details** (expanded by default): Department, team, job family, level, title, manager, start date, status
  5. **Pay & Benefits** (permission-gated, requires `payroll:read`): Salary, allowances, bank details (masked)
  6. **Documents** (collapsed by default, requires `documents:read`): Uploaded documents
  7. **Skills & Qualifications** (collapsed by default): Declared skills, education, certifications
  8. **Dependents** (collapsed by default): Emergency contacts, family
  9. **Leave** (collapsed by default, requires `leave:read-own`): Balances and requests
  10. **Activity Timeline** (collapsed by default): Recent changes
```

- [ ] **Step 2: Update Step 1 navigation path**

Replace:
```
Navigate: Sidebar → HR Management → Employees → select employee
```

With:
```
Navigate: Sidebar → People → Employees → select employee
```

- [ ] **Step 3: Commit**

```bash
git add Userflow/Employee-Management/profile-management.md
git commit -m "docs: update profile management to scrollable sections, new nav path"
```

---

### Task 16: Update Userflow — Exception Dashboard → Alerts

**Files:**
- Modify: `Userflow/Exception-Engine/exception-dashboard.md`

- [ ] **Step 1: Update title and description**

Replace "Exception Dashboard" with "Alerts Overview" throughout. Update the flow to describe alerts as an **inline layer** rather than a dedicated page:

```markdown
# Alerts Overview

Alerts surface contextually across the application — on the dashboard, in employee profiles, and via the notification bell. There is no dedicated alerts page.

## Where Alerts Appear

1. **Dashboard** — Alert cards in the Activity & Alerts section (position 5). Severity-colored left border. Click → navigates to relevant record.
2. **Employee Profile** — Banner at position 3 (Alerts / Action Items section). Shows alerts specific to that employee.
3. **Notification Bell** — Real-time alert push via SignalR. Click → navigates to relevant record.

## Alert Configuration

Alert rules are configured under **Settings → Alert Rules** (admin only). See [[Userflow/Exception-Engine/exception-rule-setup|Alert Rule Setup]].
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Exception-Engine/exception-dashboard.md
git commit -m "docs: update exception dashboard to inline alerts model"
```

---

### Task 17: Update Userflow — Notification View

**Files:**
- Modify: `Userflow/Notifications/notification-view.md`

- [ ] **Step 1: Add Inbox distinction**

Add a section clarifying the split between Bell and Inbox:

```markdown
## Notification Channels

| Channel | Purpose | Content |
|:--------|:--------|:--------|
| **Notification Bell** (topbar) | FYI updates — no action needed | "John was promoted", "Policy updated", system announcements |
| **Inbox** (sidebar) | Actionable items — needs your decision | Leave approvals, expense reviews, onboarding sign-offs, assigned tasks |

Users should never have to check two places for the same thing. Each notification routes to exactly one channel based on whether it requires action.
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Notifications/notification-view.md
git commit -m "docs: add inbox vs bell distinction to notification flow"
```

---

### Task 18: Update Userflow — Live Dashboard

**Files:**
- Modify: `Userflow/Workforce-Intelligence/live-dashboard.md`

- [ ] **Step 1: Update navigation path**

Replace any references to `Sidebar → Workforce Intelligence → Live Dashboard` with:
```
Navigate: Sidebar → Workforce → Live Dashboard
```

- [ ] **Step 2: Add absorbed views as tabs**

Add a note that Activity, Work Insights (Productivity), and Online Status are tabs within the Live Dashboard, not separate sidebar items:

```markdown
### Tabs Within Live Dashboard

| Tab | Content | Previously |
|:----|:--------|:-----------|
| Overview | Real-time employee grid, summary stats | Live Dashboard |
| Activity | Activity snapshots, app usage | Separate sidebar item "Activity" |
| Work Insights | Productivity metrics, trends | Separate sidebar item "Productivity" |
| Online Status | Presence tracking, status dots | Separate sidebar item "Presence" |
```

- [ ] **Step 3: Commit**

```bash
git add Userflow/Workforce-Intelligence/live-dashboard.md
git commit -m "docs: update live dashboard with absorbed tabs and new nav path"
```

---

### Task 19: Update Userflow README

**Files:**
- Modify: `Userflow/README.md`

- [ ] **Step 1: Add Naming Conventions section**

Add a section at the top or after the overview:

```markdown
## Naming Conventions

All user-facing labels use simple, everyday language. When writing userflows, use the user-facing name, not the system/module name.

| System Module | User-Facing Label |
|:--------------|:------------------|
| Exception Engine | Alerts |
| Workforce Intelligence | Workforce |
| Compensation | Pay & Benefits |
| Grievance | Complaints |
| Presence | Online Status |
| Verification | ID Checks |
| Productivity Dashboard | Work Insights |
| Approvals | Inbox |
| Command Palette | Quick Search |
```

- [ ] **Step 2: Update navigation references**

Update any sidebar navigation references from the old structure (HR Management → Employees) to the new pillar structure (People → Employees).

- [ ] **Step 3: Commit**

```bash
git add Userflow/README.md
git commit -m "docs: add naming conventions and update nav references in userflow README"
```

---

### Task 20: Create Inbox Userflow

**Files:**
- Create: `Userflow/Notifications/inbox.md`

- [ ] **Step 1: Write the Inbox userflow**

```markdown
# Inbox

The personal action center — everything waiting for YOUR decision, in one place.

## Preconditions

- User is authenticated
- User has `approvals:read` permission

## Flow Steps

### Step 1: Open Inbox
- **Navigate:** Sidebar → Inbox (badge shows unresolved count)
- **UI:** Single-column list sorted by urgency then date

### Step 2: Review Items
- **UI:** Each item shows: icon, title, source (who submitted), timestamp, action buttons
- **Item types:**
  - Leave requests → Approve / Reject
  - Expense claims → Approve / Reject / Request Info
  - Onboarding sign-offs → Complete / Defer
  - Transfer/promotion requests → Approve / Reject
  - Assigned tasks → View / Complete
  - Mentions → View context

### Step 3: Take Action
- **UI:** Click action button → inline confirmation or slide-over detail panel
- Bulk approve/reject available for similar items (e.g., 5 leave requests)
- Completed items move to "Done" section (collapsible, below active items)

### Step 4: Empty State
- **UI:** "You're all caught up" with illustration. No pending items.

## Distinction from Notification Bell

- **Inbox** = actionable (needs your decision)
- **Bell** = informational (FYI updates, no action needed)

## Related Flows

- [[Userflow/Leave/leave-approval|Leave Approval]]
- [[Userflow/Expense/expense-approval|Expense Approval]]
- [[Userflow/Notifications/notification-view|Notification View]]

## Module References

- [[modules/notifications/overview|Notifications Module]]
```

- [ ] **Step 2: Commit**

```bash
git add Userflow/Notifications/inbox.md
git commit -m "docs: add inbox userflow for personal action center"
```

---

### Task 21: Add Naming Conventions Doc

**Files:**
- Create: `frontend/design-system/naming-conventions.md`

- [ ] **Step 1: Write the naming guide**

```markdown
# Naming Conventions

## Principle

Every user-facing label passes the "would a non-technical HR manager understand this in 1 second?" test. If a label needs explanation, it's wrong.

## System → User-Facing Label Map

| System/Module Name | User-Facing Label | Why |
|:-------------------|:------------------|:----|
| Exception Engine | Alerts | Users think in alerts, not exceptions |
| Workforce Intelligence | Workforce | "Intelligence" sounds like surveillance |
| Data Visualization | Charts & Graphs | Everyone knows what a chart is |
| Command Palette | Quick Search | Human label for ⌘K |
| Compensation | Pay & Benefits | What people actually call it |
| Grievance | Complaints | Less legal-sounding, or "Employee Concerns" |
| Presence | Online Status | Instant understanding |
| Verification | ID Checks | Says what it does |
| Productivity Dashboard | Work Insights | Less "Big Brother" energy |
| Approvals | Inbox | Personal action center, broader than just approvals |
| Micro-interactions | Animations | Self-explanatory |

## Rules

1. **No jargon** — if a word is only used by developers or HR software vendors, find a simpler one
2. **Action-oriented** — labels should hint at what the user can DO there (Inbox → act on items, not just view them)
3. **Consistent** — once we name something, use that name everywhere (docs, code, UI, userflows)
4. **Short** — one or two words maximum for navigation labels

## Related

- [[frontend/design-system/patterns/navigation-patterns|Navigation Patterns]] — sidebar labels
- [[Userflow/README|Userflow Overview]] — naming in userflows
```

- [ ] **Step 2: Update design-system/README.md to link to this doc**

Add to the Foundations section:
```markdown
- [[frontend/design-system/naming-conventions|Naming Conventions]] — user-facing label rules, system-to-label mapping
```

- [ ] **Step 3: Commit**

```bash
git add frontend/design-system/naming-conventions.md frontend/design-system/README.md
git commit -m "docs: add naming conventions guide for user-facing labels"
```

---

### Task 22: Final Cross-Reference Audit

**Files:**
- All files modified in Tasks 1–21

- [ ] **Step 1: Search for stale references**

Search all files in `frontend/` and `Userflow/` for:
- `Inter` (old font) — should be `Outfit` or `Geist`
- `222.2 84% 51%` (old primary blue) — should be new violet values
- `Sidebar → HR Management` — should be `Sidebar → People`
- `Exception` used as a nav/page label — should be `Alert`
- `/hr/employees` — should be `/people/employees`
- `Approvals` used as nav label — should be `Inbox`
- `Command Palette` as label — should be `Quick Search`
- `w-64` sidebar width — should be `w-16` (rail) or `w-[220px]` (panel)

- [ ] **Step 2: Fix any remaining stale references found**

Update each file with the correct new terminology.

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "docs: fix stale references across frontend and userflow docs"
```
