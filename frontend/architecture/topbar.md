# Topbar Architecture

## Layout

```
[■ Acme Malaysia Sdn Bhd  ▾]  |  [  Search...  ⌘K  ]  |  🔔  ☀  [Avatar ▾]
Left (fixed width ~200px)        Center (flex-grow)       Right (fixed width)
```

Height: 40px (`h-10`). Spans full width above both the icon rail and expansion panel.


## Responsive Behavior

The topbar must preserve entity context, navigation access, search, notifications, and profile access across all Phase 1 breakpoints.

| Viewport | Topbar behavior |
|:---------|:----------------|
| Mobile `<640px` | Show hamburger, concise page title, one primary action when present, and overflow menu. Company context and search move into the navigation drawer or icon triggers. |
| Tablet `640-1023px` | Show hamburger, active company in compact form, search icon, notifications, and avatar/overflow menu. Breadcrumbs collapse to current page or one parent. |
| Laptop `1024-1279px` | Show compact company context, short breadcrumb, search pill, notifications, theme, and avatar. Hide low-priority labels before actions. |
| Desktop `>=1280px` | Show full company context, breadcrumb, search, notification, theme, and avatar controls. |

Rules:

- Text must truncate safely with tooltips or accessible labels where needed.
- Critical actions cannot disappear; they move into the overflow menu or drawer.
- Search must remain reachable at every viewport, even when the full search pill is hidden.
- Hamburger controls the same permission-aware `MobileNavDrawer` used by tablet/mobile navigation.

## Left — Company Context

### What it shows
The company tenant the user is currently signed into. In ONEVO, company is the business-facing name for a tenant, and tenant remains the hard data, subscription, settings, branding, permission, and audit boundary.

### Why company context, not legal entity switching
Separate operating companies are separate tenants. The topbar must not make connected companies look like simple in-session legal entity switching. When a user has approved cross-company access, those connected companies appear only inside relevant cross-company views or workflows, and only after the backend validates the active connection, permission, scope, and audit requirements.

### Context dropdown anatomy

```
[■ Acme Malaysia Sdn Bhd  ▾]
─────────────────────────────────
✓  Acme Malaysia Sdn Bhd         ← current (checkmark)
   Connected companies           ← opens permission-scoped connected-company views
   Company profile               ← registration, billing, settings, branding
─────────────────────────────────
   Request company connection    ← only visible when enabled and permitted
```

Regular employees normally see only their current company label. Admins may see company profile and connected-company actions, but those actions do not switch the active tenant unless a future session-switching feature is explicitly designed.

### Connected-company behavior
When user opens a connected-company view:
1. Auth session remains anchored to the current company tenant.
2. Backend resolves active company connections and scoped grants.
3. Only approved projections, workflow evidence, or transfer actions are shown.
4. Every cross-company view, action, and export is audit logged with requester tenant and source tenant.

### Permission gating
| Permission | Behavior |
|---|---|
| Any authenticated user | User sees their current company name |
| `settings:read` or `org:read` | Dropdown can include Company Profile |
| `company-connections:read` | Dropdown can include Connected Companies entry |
| `company-connections:manage` | Dropdown can include request/manage connection actions |

### Component
`CompanyContextMenu` — lives in the topbar layout component.

### Data source
The current company comes from authenticated session metadata. Company registration/profile fields come from tenant detail and the retained primary registration profile. Connected-company entries come from company connection grants, not from registration profile records.

## Center — Search

Command palette trigger. Opens on click or keyboard shortcut (⌘K on Mac, Ctrl+K on Windows).

Shows: quick nav to any page, recent pages, global people search, global actions (create task, request leave, etc.).

## Right — Actions

**Notification Bell (`🔔`):** Badge count of unread inbox items. Click navigates to `/inbox`.

**Theme Toggle (`☀`):** Cycles system → light → dark.

**User Avatar Menu:** Dropdown showing user name, job title, link to their employee profile, and Sign Out.

## Pixel Specifications

### Container

| Property | Light | Dark |
|:---------|:------|:-----|
| Height | **40px** | same |
| Background | `#FFFFFF` | `#17181F` |
| Border-radius | **10px** | same |
| Border | `1px solid #E2E3EA` | `1px solid rgba(255,255,255,0.06)` |
| Shadow | `0 1px 3px rgba(0,0,0,0.06)` | `0 2px 8px rgba(0,0,0,0.30)` |
| Padding | `0 10px` | same |
| Gap (between sections) | `8px` | same |

### Entity Switcher (Left)

| Property | Light | Dark |
|:---------|:------|:-----|
| Padding | `3px 7px` | same |
| Border-radius | 7px | same |
| Hover background | `#F4F5F8` | `rgba(255,255,255,0.07)` |
| Entity name font-size | **12px** | same |
| Entity name font-weight | **600** | same |
| Entity name color | `#1E2140` | `rgba(255,255,255,0.82)` |
| Chevron icon | `ChevronDown` 11×11px, stroke-width 2 | same |
| Chevron color | `#9499B0` | `rgba(255,255,255,0.28)` |

### Breadcrumb (Left, after Entity)

| Property | Light | Dark |
|:---------|:------|:-----|
| Separator (`/`) font-size | 14px | same |
| Separator color | `#C8CADC` | `rgba(255,255,255,0.15)` |
| Part font-size | **12px** | same |
| Part font-weight | **500** | same |
| Part color (default) | `#9499B0` | `rgba(255,255,255,0.35)` |
| Part hover color | `#1E2140` | `rgba(255,255,255,0.70)` |
| Part hover background | `#F4F5F8` | `rgba(255,255,255,0.06)` |
| Part border-radius | 5px | same |
| Part padding | `2px 5px` | same |
| Current part color | `#1E2140` | `rgba(255,255,255,0.85)` |
| Current part font-weight | **600** | same |

### Search Bar (Center)

| Property | Light | Dark |
|:---------|:------|:-----|
| flex | `1`, max-width `280px`, margin `0 auto` | same |
| Background | `#F4F5F8` | `rgba(255,255,255,0.07)` |
| Border | `1px solid #E2E3EA` | `1px solid rgba(255,255,255,0.07)` |
| Border-radius | **11px** (pill) | same |
| Padding | `4px 10px` | same |
| Hover border | `#C8CADC` | same |
| Search icon | `Search` 13×13px, stroke-width 1.75, color `#9499B0` | `rgba(255,255,255,0.22)` |
| Placeholder text | 12px, color `#9499B0` | `rgba(255,255,255,0.22)` |
| Kbd shortcut | `⌘K`, 10px, font-mono, color `#C8CADC` | `rgba(255,255,255,0.15)` |

### Right Action Buttons (Bell, Help, Theme)

| Property | Light | Dark |
|:---------|:------|:-----|
| Button size | **28×28px** | same |
| Border-radius | 6px | same |
| Default color | `#6B7194` | `rgba(255,255,255,0.30)` |
| Hover background | `#F4F5F8` | `rgba(255,255,255,0.07)` |
| Hover color | `#1E2140` | `rgba(255,255,255,0.70)` |
| Icon size | **14×14px** | same |
| Icon stroke-width | **1.75** | same |
| Icons used | `Bell`, `CircleHelp`, `Moon`/`Sun` (toggle) | same |
| Transition | `background 120ms, color 120ms` | same |

### Divider + Avatar (Right)

| Property | Light | Dark |
|:---------|:------|:-----|
| Divider width | 1px | same |
| Divider height | 16px | same |
| Divider color | `#E2E3EA` | `rgba(255,255,255,0.08)` |
| Divider margin | `0 3px` | same |
| Avatar size | **24×24px** | same |
| Avatar border-radius | 50% (circle) | same |
| Avatar background | `linear-gradient(135deg, #5B4FE8, #8C86F2)` | same |
| Avatar text color | `#FFFFFF` | same |
| Avatar font-size | 9px | same |
| Avatar font-weight | 700 | same |
| Avatar margin-left | 3px | same |

### Tailwind Reference

```tsx
// src/components/layout/topbar.tsx
<header className="h-10 bg-white dark:bg-[#17181F] rounded-[10px] border border-[#E2E3EA] dark:border-white/[0.06] shadow-[0_1px_3px_rgba(0,0,0,0.06)] dark:shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex items-center px-[10px] gap-2 shrink-0">

  {/* Company context */}
  <div className="flex items-center gap-1.5 px-[7px] py-[3px] rounded-[7px] cursor-pointer hover:bg-[#F4F5F8] dark:hover:bg-white/[0.07] shrink-0">
    <span className="text-[12px] font-semibold text-[#1E2140] dark:text-white/[0.82] whitespace-nowrap">
      Acme Malaysia Sdn Bhd
    </span>
    <ChevronDown size={11} strokeWidth={2} className="text-[#9499B0] dark:text-white/[0.28]" />
  </div>

  {/* Breadcrumb */}
  <div className="flex items-center gap-[3px] shrink-0">
    <span className="text-[14px] text-[#C8CADC] dark:text-white/[0.15]">/</span>
    <span className="text-[12px] font-medium text-[#9499B0] dark:text-white/[0.35] px-[5px] py-[2px] rounded-[5px] cursor-pointer hover:text-[#1E2140] hover:bg-[#F4F5F8] dark:hover:text-white/[0.70] dark:hover:bg-white/[0.06] whitespace-nowrap">
      Workforce
    </span>
    <span className="text-[14px] text-[#C8CADC] dark:text-white/[0.15]">/</span>
    <span className="text-[12px] font-semibold text-[#1E2140] dark:text-white/[0.85] px-[5px] py-[2px] whitespace-nowrap">
      Presence
    </span>
  </div>

  {/* Search */}
  <div className="flex-1 max-w-[280px] mx-auto flex items-center gap-[7px] bg-[#F4F5F8] dark:bg-white/[0.07] border border-[#E2E3EA] dark:border-white/[0.07] rounded-[11px] px-[10px] py-1 hover:border-[#C8CADC] cursor-pointer">
    <Search size={13} strokeWidth={1.75} className="text-[#9499B0] dark:text-white/[0.22] shrink-0" />
    <span className="text-[12px] text-[#9499B0] dark:text-white/[0.22]">Search…</span>
    <kbd className="ml-auto text-[10px] font-mono text-[#C8CADC] dark:text-white/[0.15]">⌘K</kbd>
  </div>

  {/* Right actions */}
  <div className="flex items-center gap-px ml-auto">
    {[Bell, CircleHelp, Moon].map((Icon, i) => (
      <button key={i} className="w-7 h-7 rounded-[6px] flex items-center justify-center text-[#6B7194] dark:text-white/[0.30] hover:bg-[#F4F5F8] dark:hover:bg-white/[0.07] hover:text-[#1E2140] dark:hover:text-white/[0.70] transition-[background,color] duration-[120ms] border-none cursor-pointer">
        <Icon size={14} strokeWidth={1.75} aria-hidden="true" />
      </button>
    ))}
    <div className="w-px h-4 bg-[#E2E3EA] dark:bg-white/[0.08] mx-[3px]" />
    <div className="w-6 h-6 rounded-full bg-gradient-to-br from-[#5B4FE8] to-[#8C86F2] flex items-center justify-center text-[9px] font-bold text-white cursor-pointer ml-[3px]">
      A
    </div>
  </div>
</header>
```

## Related

- [[frontend/architecture/sidebar-nav|Sidebar Nav Map]] — full pillar and permission reference
- [[frontend/design-system/components/shell-layout|Shell Layout]] — overall layout this topbar sits in
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — brand + shell color values
- [[modules/shared-platform/company-connections/overview|Company Connections]] — permission-scoped cross-company views and workflows
