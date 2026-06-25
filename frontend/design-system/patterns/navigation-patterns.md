# Navigation Patterns

## Navigation Hierarchy

```
+- Topbar -----------------------------------------------------------------+
|  [[menu]]  Breadcrumbs  ,,,  [CmdK Search]  [Entityv]  [theme][bell][Av] |
+------+------------------+------------------------------------------------+
| Rail | Expansion Panel  |  Page Content                                  |
| 64px | 220px            |                                                |
|      |                  |                                                |
|  [home]   |  People          |                                                |
|  People  |  + Employees     |                                                |
|  Reports |  + Time Off      |                                                |
|  Org     |                  |                                                |
|  Calendar|                  |                                                |
|  Inbox   |                  |                                                |
|  [settings]   |                  |                                                |
|  Tools   |                  |                                                |
|      |                  |                                                |
| [Av] |                  |                                                |
| [theme] |                  |                                                |
+------+------------------+------------------------------------------------+
```

---

## Sidebar - Pillar-Based Two-Level

### Architecture

The sidebar is split into two surfaces:

1. **Icon Rail** - always visible (64px wide), shows one icon per pillar. Clicking an icon either navigates directly (for single-destination pillars) or opens the Expansion Panel for that pillar.
2. **Expansion Panel** - slides in at 220px, shows the active pillar's sub-items. Pinnable on >=1280px; flies out on hover when rail-only.

### Icon Rail

| Property | Value |
|:---------|:------|
| Width | 64px |
| Surface | `bg-[var(--bg-surface)]` |
| Border | `border-r border-[var(--border)]` |
| Position | Flush left edge (`left-0`) |
| Active indicator | 4px neutral dot (`bg-[var(--fg-1)]`) below icon - visible only when active |
| Icon size | 16px (`size={16}`) |
| Active icon color | `text-[var(--fg-1)]` |
| Inactive icon color | `text-[var(--fg-3)]` |
| Hover | `text-[var(--fg-2)] bg-[var(--bg-hover)]` |

### Expansion Panel

| Property | Value |
|:---------|:------|
| Width | 220px |
| Surface | `bg-[var(--bg-surface)]` |
| Border | `border-r border-[var(--border)]` |
| Pillar header | Outfit 11px uppercase, `text-[var(--fg-3)]` |
| Sub-item font | Outfit 13px, `text-[var(--fg-3)]` |
| Active item | `bg-[var(--accent-subtle)] border border-[var(--accent-border)] text-[var(--fg-1)]` |
| Animation | `translateX` 200ms ease (unchanged) |
| Pinnable | Yes, on >=1280px (Zustand + localStorage) |
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
  // If `href` is set and `items` is absent -> direct navigation (no panel)
  href?: string;
  items?: PillarItem[];
  permission?: string;
  badge?: () => number;
}

// Permission model: hasPermission() checks both role permissions AND
// employee-level overrides. Never hardcode role names.
const pillars: Pillar[] = [
  { id: 'home', icon: LayoutDashboard, label: 'Home', href: '/' },
  {
    id: 'people', icon: Users, label: 'People', permission: 'employees:read',
    items: [
      { label: 'Employees', href: '/people/employees', permission: 'employees:read' },
      { label: 'Onboarding', href: '/people/onboarding', permission: 'employees:write' },
      { label: 'Offboarding', href: '/people/offboarding', permission: 'employees:write' },
      { label: 'Checklist Templates', href: '/people/checklist-templates', permission: 'employees:write' },
    ],
  },
  {
    id: 'time-off', icon: CalendarRange, label: 'Time Off', permission: 'time_off:read',
    items: [
      { label: 'My Time Off', href: '/time-off', permission: 'time_off:read-own' },
      { label: 'Team Time Off', href: '/time-off/team', permission: 'time_off:approve' },
      { label: 'Types', href: '/time-off/types', permission: 'time_off:manage' },
      { label: 'Policies', href: '/time-off/policies', permission: 'time_off:manage' },
      { label: 'Entitlements', href: '/time-off/entitlements', permission: 'time_off:manage' },
    ],
  },
  {
    id: 'time-attendance', icon: Activity, label: 'Time & Attendance', permission: 'attendance:read',
    items: [
      { label: 'Attendance', href: '/time-attendance/attendance', permission: 'attendance:read-own' },
      { label: 'Schedules', href: '/time-attendance/schedules', permission: 'attendance:read' },
      { label: 'Clock-in Policy', href: '/time-attendance/clock-in-policy', permission: 'attendance:write' },
      { label: 'Overtime Rules', href: '/time-attendance/overtime-rules', permission: 'attendance:write' },
    ],
  },
  {
    id: 'work', icon: BriefcaseBusiness, label: 'Work', permission: 'projects:read',
    items: [
      { label: 'Projects', href: '/work/projects', permission: 'projects:read' },
      { label: 'Work Items', href: '/work/items', permission: 'tasks:read' },
      { label: 'Documents', href: '/work/documents', permission: 'documents:read' },
      { label: 'Project Members', href: '/work/members', permission: 'projects:read' },
      { label: 'Worklogs', href: '/work/worklogs', permission: 'time:read' },
    ],
  },
  { id: 'calendar', icon: CalendarRange, label: 'Calendar', href: '/calendar', permission: 'calendar:read' },
  { id: 'inbox', icon: Inbox, label: 'Inbox', href: '/inbox', permission: 'inbox:read', badge: () => useUnresolvedInboxCount() },
  {
    id: 'monitoring', icon: Activity, label: 'Monitoring', permission: 'monitoring:view',
    items: [
      { label: 'Live Status', href: '/monitoring', permission: 'monitoring:view' },
      { label: 'Alerts', href: '/monitoring/alerts', permission: 'monitoring:alerts:read' },
      { label: 'Device Health', href: '/monitoring/devices', permission: 'agent:view-health' },
    ],
  },
  {
    id: 'settings', icon: Settings, label: 'Settings', permission: 'settings:read',
    items: [
      { label: 'General', href: '/settings/general', permission: 'settings:read' },
      { label: 'Branding', href: '/settings/branding', permission: 'settings:branding' },
      { label: 'Users', href: '/settings/users', permission: 'users:manage' },
      { label: 'Roles & Permissions', href: '/settings/roles', permission: 'roles:manage' },
      { label: 'Notifications', href: '/settings/notifications', permission: 'notifications:configure' },
      { label: 'Billing', href: '/settings/billing', permission: 'billing:read' },
      { label: 'Devices', href: '/settings/devices', permission: 'settings:device' },
      { label: 'Audit Log', href: '/settings/audit', permission: 'audit:read' },
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
    // Direct nav - simple tooltip
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

  // Has sub-items - HoverCard flyout when panel is closed
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

## Responsive Navigation

Navigation is responsive from Phase 1 and must preserve the same route, badge, active-state, and permission behavior at every breakpoint.

| Viewport | Navigation model | Behavior |
|:---------|:-----------------|:---------|
| Mobile `<640px` | Hamburger + `MobileNavDrawer` | Drawer contains entity context, search entry, all visible pillars, sub-items, badges, and profile/settings access. It closes after navigation. |
| Tablet `640-1023px` | Hamburger + drawer | Same route map as desktop. Drawer may use two-level accordion groups for pillar items. |
| Desktop `>=1024px` | Rail + expansion panel | Rail visible; expansion panel pinnable. At 1024-1279px the panel may default to collapsed/flyout mode; at >=1280px it can be pinned open. |

State rules:

- The active route must highlight the same pillar/item in rail, panel, and drawer.
- Badges, unread counts, and permission filters must be computed once from the shared pillar config.
- The drawer is temporary UI state and should not persist across sessions.
- Pinned desktop panel state may persist in Zustand/localStorage, but must not force a panel on tablet or mobile.
- Keyboard navigation and focus trapping are required inside the mobile/tablet drawer.

## Topbar

Height: **48px**, glass surface (`bg-white/5 backdrop-blur border-b border-white/10`).

Full element order (left -> right):

```
[menu Hamburger]  [Breadcrumbs]  ,,,spacer,,,  [CmdK Search]  [Entity v]  [Theme]  [Bell]  [Avatar]
```

| Element | Position | Visibility | Behaviour |
|:--------|:---------|:-----------|:----------|
| Hamburger `menu` | Left | Mobile/tablet only (`< 1024px`) | Opens responsive navigation drawer |
| Breadcrumbs | Left (after hamburger) | Always | Outfit 400, 13px, zinc-500 - auto-generated from route |
| Quick Search pill | Center/right | Always | Opens Quick Search modal (`CmdK` / `Ctrl+K`) |
| Entity chip `[Entity v]` | Right (before theme toggle) | Only when tenant has **more than one** legal entity and user has access to **more than one** | Compact dropdown - see [[frontend/design-system/patterns/app-entity-switcher\|Entity Context Pattern]] |
| Theme Toggle | Right (before bell) | Always | Sun/Moon/Monitor - cycles system->light->dark |
| Notification Bell | Right | Always | FYI-only informational alerts |
| User Avatar | Right | Always | Profile, preferences, logout |

For legal-entity context behaviour, states, and responsive rules see [[frontend/design-system/patterns/app-entity-switcher|Entity Context Pattern]]. There is no customer-facing app switcher in Phase 1.

---

## Quick Search (CmdK)

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
          <CommandItem onSelect={() => router.push('/time-off')}>
            <CalendarDays className="h-4 w-4 mr-2" /> Time Off Requests
          </CommandItem>
          <CommandItem onSelect={() => router.push('/monitoring')}>
            <Activity className="h-4 w-4 mr-2" /> Live Status
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
            <Plus className="h-4 w-4 mr-2" /> Submit Time Off Request
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

FYI-only. Does not surface actionable items - those belong in Inbox.

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
// Time Off > Team Time Off
// Monitoring > Live Status
// Settings > Notifications
```

Rules:
- Always show full path from pillar root
- Last breadcrumb is **not** a link (current page)
- Clicking any ancestor navigates to that level
- Font: Outfit 400, 13px, zinc-500; separator `/` zinc-600

---

## Tab Navigation

Used **sparingly** - only for truly separate concerns within a single page, not for primary navigation.

```tsx
// Example: Monitoring Live Status - tabs are separate concerns within one page
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

Tabs sync to URL hash for deep-linking: `/monitoring#insights`

Do not use tabs to replicate pillar-level navigation. If a distinction warrants its own nav item, it belongs in the pillar config, not as a tab.

---

## Related

- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] - page structure
- [[frontend/design-system/foundations/iconography|Iconography]] - nav icons
- [[frontend/architecture/routing|Routing]] - route guards
- [[frontend/cross-cutting/authorization|Authorization]] - permission gating
