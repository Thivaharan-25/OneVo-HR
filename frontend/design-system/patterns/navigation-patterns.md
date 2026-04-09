# Navigation Patterns

## Navigation Hierarchy

```
┌─ Topbar ─────────────────────────────────────────────────────────────────┐
│  [☰]  Breadcrumbs (Outfit 400, 13px, zinc-500)  [⌘K Search]  [🔔] [Av] │
├──────┬──────────────────┬────────────────────────────────────────────────┤
│ Rail │ Expansion Panel  │  Page Content                                  │
│ 64px │ 220px            │                                                │
│      │                  │                                                │
│  ⌂   │  People          │                                                │
│  👥  │  ├ Employees     │                                                │
│  📊  │  ├ Leave         │                                                │
│  🏢  │                  │                                                │
│  📅  │                  │                                                │
│  📥  │                  │                                                │
│  ⚙   │                  │                                                │
│  🔧  │                  │                                                │
│      │                  │                                                │
│ [Av] │                  │                                                │
│ [🌙] │                  │                                                │
└──────┴──────────────────┴────────────────────────────────────────────────┘
```

---

## Sidebar — Pillar-Based Two-Level

### Architecture

The sidebar is split into two surfaces:

1. **Icon Rail** — always visible (64px wide), shows one icon per pillar. Clicking an icon either navigates directly (for single-destination pillars) or opens the Expansion Panel for that pillar.
2. **Expansion Panel** — slides in at 220px, shows the active pillar's sub-items. Pinnable on ≥1280px; flies out on hover when rail-only.

### Icon Rail

| Property | Value |
|:---------|:------|
| Width | 64px |
| Surface | Glass (`backdrop-blur`, `bg-white/5`) |
| Top slot | ONEVO logo mark |
| Active indicator | Violet glow pip (left edge, `bg-violet-500`, `shadow-violet-500/50`) |
| Bottom slots | User avatar + theme toggle |
| Icon size | 20px (`h-5 w-5`) |
| Font | — (icon-only) |

### Expansion Panel

| Property | Value |
|:---------|:------|
| Width | 220px |
| Surface | Glass lighter (`bg-white/8 backdrop-blur`) |
| Pillar header | Outfit 600, 11px, uppercase, zinc-400 |
| Sub-item font | Geist 13px, zinc-300 |
| Active item | Violet left border (`border-l-2 border-violet-500`), `bg-violet-500/10` |
| Animation | `translateX` 200ms ease-out (slides in from left) |
| Pinnable | Yes, on ≥1280px (Zustand + localStorage) |
| Collapse trigger | Pin toggle button at panel top-right |

---

## Pillar Configuration

```ts
import {
  LayoutDashboard, Users, Activity, Network,
  CalendarRange, Inbox, UserCog, Settings,
} from 'lucide-react';

interface PillarItem {
  label: string;
  href: string;
  permission?: string;
  badge?: () => number;
}

interface Pillar {
  id: string;
  icon: LucideIcon;
  label: string;
  // If `href` is set and `items` is absent → direct navigation (no panel)
  href?: string;
  items?: PillarItem[];
  permission?: string;
  badge?: () => number;
}

// Permission model: hasPermission() checks both role permissions AND
// employee-level overrides. Never hardcode role names.
const pillars: Pillar[] = [
  {
    id: 'home',
    icon: LayoutDashboard,
    label: 'Home',
    href: '/',
    // No permission gate — visible to all authenticated users
  },

  {
    id: 'people',
    icon: Users,
    label: 'People',
    permission: 'people:read',
    items: [
      { label: 'Employees', href: '/people/employees', permission: 'employees:read' },
      { label: 'Leave',      href: '/people/leave',     permission: 'leave:read' },
    ],
  },

  {
    id: 'workforce',
    icon: Activity,
    label: 'Workforce',
    permission: 'workforce:read',
    items: [
      {
        label: 'Live Dashboard',
        href: '/workforce/live',
        permission: 'workforce:dashboard',
        // Activity, Work Insights, and Online Status are tabs within /workforce/live
      },
    ],
  },

  {
    id: 'organization',
    icon: Network,
    label: 'Organization',
    permission: 'org:read',
    items: [
      { label: 'Org Chart',    href: '/org/chart',       permission: 'org:read' },
      { label: 'Departments',  href: '/org/departments', permission: 'departments:read' },
      { label: 'Teams',        href: '/org/teams',       permission: 'teams:read' },
    ],
  },

  {
    id: 'calendar',
    icon: CalendarRange,
    label: 'Calendar',
    href: '/calendar',
    permission: 'calendar:read',
  },

  {
    id: 'inbox',
    icon: Inbox,
    label: 'Inbox',
    href: '/inbox',
    permission: 'inbox:read',
    badge: () => useUnresolvedInboxCount(),   // actionable items only
  },

  {
    id: 'admin',
    icon: UserCog,
    label: 'Admin',
    permission: 'admin:access',
    items: [
      { label: 'Users & Roles', href: '/admin/users',      permission: 'users:manage' },
      { label: 'Audit Log',     href: '/admin/audit',      permission: 'audit:read' },
      { label: 'Agents',        href: '/admin/agents',     permission: 'agents:manage' },
      { label: 'Devices',       href: '/admin/devices',    permission: 'devices:manage' },
      { label: 'Compliance',    href: '/admin/compliance', permission: 'compliance:manage' },
    ],
  },

  {
    id: 'settings',
    icon: Settings,
    label: 'Settings',
    permission: 'settings:read',
    items: [
      { label: 'General',       href: '/settings/general',      permission: 'settings:read' },
      { label: 'Monitoring',    href: '/settings/monitoring',   permission: 'monitoring:configure' },
      { label: 'Notifications', href: '/settings/notifications',permission: 'notifications:configure' },
      { label: 'Integrations',  href: '/settings/integrations', permission: 'integrations:manage' },
      { label: 'Branding',      href: '/settings/branding',     permission: 'branding:manage' },
      { label: 'Billing',       href: '/settings/billing',      permission: 'billing:read' },
      { label: 'Alert Rules',   href: '/settings/alert-rules',  permission: 'alerts:manage' },
    ],
  },
];
```

---

## Rendering Logic

Pillars are filtered at render time. Items the user cannot access are never sent to the client.

```tsx
function Sidebar() {
  const { hasPermission } = usePermissions();
  const pathname = usePathname();
  const [activePillarId, setActivePillarId] = useState<string | null>(null);
  const { isPinned, setIsPinned } = useSidebarStore();

  const visiblePillars = pillars
    .filter(p => !p.permission || hasPermission(p.permission))
    .map(p => ({
      ...p,
      items: p.items?.filter(item => !item.permission || hasPermission(item.permission)),
    }))
    .filter(p => p.href || (p.items && p.items.length > 0));

  function handlePillarClick(pillar: Pillar) {
    if (pillar.href) {
      router.push(pillar.href);
      setActivePillarId(pillar.id);
    } else {
      // Toggle expansion panel
      setActivePillarId(prev => (prev === pillar.id ? null : pillar.id));
    }
  }

  const activePillar = visiblePillars.find(p => p.id === activePillarId) ?? null;

  return (
    <aside className="flex h-full">
      {/* Icon Rail */}
      <div className="flex flex-col w-16 bg-white/5 backdrop-blur border-r border-white/10">
        <div className="flex items-center justify-center h-14">
          <OneVoLogoMark />
        </div>
        <nav className="flex-1 flex flex-col gap-1 px-2 py-2">
          {visiblePillars.map(pillar => (
            <RailItem
              key={pillar.id}
              pillar={pillar}
              isActive={activePillarId === pillar.id}
              onClick={() => handlePillarClick(pillar)}
            />
          ))}
        </nav>
        <div className="flex flex-col items-center gap-2 pb-4">
          <ThemeToggle />
          <UserAvatar />
        </div>
      </div>

      {/* Expansion Panel */}
      {activePillar?.items && (
        <ExpansionPanel
          pillar={activePillar}
          isPinned={isPinned}
          onPin={() => setIsPinned(!isPinned)}
          pathname={pathname}
        />
      )}
    </aside>
  );
}
```

---

## Collapsed State (Rail Only)

When the expansion panel is closed (rail-only mode), hovering a pillar that has sub-items shows a **HoverCard flyout** pinned to the right edge of the rail.

```tsx
function RailItem({ pillar, isActive, onClick }: RailItemProps) {
  if (!pillar.items) {
    // Direct nav — simple tooltip
    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <button onClick={onClick} className={cn('rail-btn', isActive && 'rail-btn--active')}>
            <pillar.icon className="h-5 w-5" />
            {pillar.badge && <PillarBadge count={pillar.badge()} />}
          </button>
        </TooltipTrigger>
        <TooltipContent side="right">{pillar.label}</TooltipContent>
      </Tooltip>
    );
  }

  // Has sub-items — HoverCard flyout when panel is closed
  return (
    <HoverCard openDelay={150} closeDelay={100}>
      <HoverCardTrigger asChild>
        <button onClick={onClick} className={cn('rail-btn', isActive && 'rail-btn--active')}>
          <pillar.icon className="h-5 w-5" />
        </button>
      </HoverCardTrigger>
      <HoverCardContent side="right" className="w-48 p-2 glass">
        <p className="text-[11px] font-semibold uppercase text-zinc-400 px-2 pb-1">
          {pillar.label}
        </p>
        {pillar.items.map(item => (
          <a key={item.href} href={item.href} className="flyout-item">
            {item.label}
          </a>
        ))}
      </HoverCardContent>
    </HoverCard>
  );
}
```

---

## Responsive States

| State | Rail | Panel | Trigger | Persistence |
|:------|:-----|:------|:--------|:------------|
| Full | 64px | 220px (pinned) | Default ≥1280px | Zustand + localStorage |
| Rail only | 64px | Flyout on hover | Default ≥1024px or user unpins | Zustand + localStorage |
| Hidden | 0px | 0px | ≤768px | Responsive only |
| Overlay | 64px + 220px | Hamburger ≤768px | Temporary | Session only |

---

## Topbar

Height: **56px**, glass surface (`bg-white/5 backdrop-blur border-b border-white/10`).

| Element | Position | Behavior |
|:--------|:---------|:---------|
| Hamburger | Left (mobile ≤768px only) | Opens sidebar overlay |
| Breadcrumbs | Left (after hamburger) | Outfit 400, 13px, zinc-500 — auto-generated from route |
| Quick Search pill | Center | Opens Quick Search modal (`⌘K` / `Ctrl+K`) |
| Notification Bell | Right | FYI only — informational alerts, no actions required |
| User Avatar | Right | Profile, preferences, logout |

> **Bell vs Inbox distinction:** The Notification Bell is for **informational** updates (system events, FYI alerts). Items that require action go to **Inbox** (`/inbox`), surfaced via the Inbox pillar in the rail with an unresolved-count badge.

---

## Quick Search (⌘K)

Renamed from "Command Palette." A glass modal overlay, keyboard-navigable, with violet highlight on selection.

```tsx
function QuickSearch() {
  return (
    <CommandDialog>
      <CommandInput placeholder="Search employees, pages, actions..." />
      <CommandList>
        <CommandGroup heading="Navigation">
          <CommandItem onSelect={() => router.push('/people/employees')}>
            <Users className="h-4 w-4 mr-2" /> Employees
          </CommandItem>
          <CommandItem onSelect={() => router.push('/people/leave')}>
            <CalendarDays className="h-4 w-4 mr-2" /> Leave Requests
          </CommandItem>
          <CommandItem onSelect={() => router.push('/workforce/live')}>
            <Activity className="h-4 w-4 mr-2" /> Live Dashboard
          </CommandItem>
        </CommandGroup>
        <CommandGroup heading="Recent Employees">
          {recentEmployees.map(emp => (
            <CommandItem
              key={emp.id}
              onSelect={() => router.push(`/people/employees/${emp.id}`)}
            >
              <Avatar className="h-6 w-6 mr-2" /> {emp.name}
            </CommandItem>
          ))}
        </CommandGroup>
        <CommandGroup heading="Actions">
          <CommandItem onSelect={openCreateEmployee}>
            <Plus className="h-4 w-4 mr-2" /> Create Employee
          </CommandItem>
          <CommandItem onSelect={openSubmitLeave}>
            <Plus className="h-4 w-4 mr-2" /> Submit Leave Request
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
```

**Styling:** Glass modal (`bg-white/8 backdrop-blur border border-white/15`), active item `bg-violet-500/20 text-violet-200`.

---

## Notification Bell

FYI-only. Does not surface actionable items — those belong in Inbox.

```tsx
function NotificationBell() {
  const { data: unread } = useUnreadNotificationCount();

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unread > 0 && (
            <Badge className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-[10px]">
              {unread > 99 ? '99+' : unread}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0" align="end">
        <NotificationPanel />
        {/* NotificationPanel shows FYI items only.
            "View all actionable items" links to /inbox */}
      </PopoverContent>
    </Popover>
  );
}
```

---

## Breadcrumbs

Auto-generated from the current route. Dynamic segments (`[id]`) resolve to entity name via API/cache.

```tsx
// Examples:
// People > Employees > John Doe
// People > Leave > Calendar
// Workforce > Live Dashboard
// Settings > Alert Rules
```

Rules:
- Always show full path from pillar root
- Last breadcrumb is **not** a link (current page)
- Clicking any ancestor navigates to that level
- Font: Outfit 400, 13px, zinc-500; separator `/` zinc-600

---

## Tab Navigation

Used **sparingly** — only for truly separate concerns within a single page, not for primary navigation.

```tsx
// Example: Workforce Live Dashboard — tabs are separate concerns within one page
<Tabs defaultValue="activity">
  <TabsList>
    <TabsTrigger value="activity">Activity</TabsTrigger>
    <TabsTrigger value="insights">Work Insights</TabsTrigger>
    <TabsTrigger value="online-status">Online Status</TabsTrigger>
  </TabsList>
  <TabsContent value="activity"><ActivityTab /></TabsContent>
  <TabsContent value="insights"><WorkInsightsTab /></TabsContent>
  <TabsContent value="online-status"><OnlineStatusTab /></TabsContent>
</Tabs>
```

Tabs sync to URL hash for deep-linking: `/workforce/live#insights`

Do not use tabs to replicate pillar-level navigation. If a distinction warrants its own nav item, it belongs in the pillar config, not as a tab.

---

## Related

- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — page structure
- [[frontend/design-system/foundations/iconography|Iconography]] — nav icons
- [[frontend/architecture/routing|Routing]] — route guards
- [[frontend/cross-cutting/authorization|Authorization]] — permission gating
