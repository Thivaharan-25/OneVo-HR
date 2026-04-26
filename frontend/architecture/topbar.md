# Topbar Architecture

## Layout

```
[■ Acme Malaysia Sdn Bhd  ▾]  |  [  Search...  ⌘K  ]  |  🔔  ☀  [Avatar ▾]
Left (fixed width ~200px)        Center (flex-grow)       Right (fixed width)
```

Height: 48px (`h-12`). Spans full width above both the icon rail and expansion panel.

## Left — Legal Entity Switcher

### What it shows
The legal entity the user currently operates within — the registered company or business unit their data access is scoped to. Not a generic "workspace" or "tenant" name.

### Why legal entity, not workspace name
ONEVO's permission model is hierarchy-scoped. A Super Admin may govern multiple entities (e.g., "Acme Malaysia Sdn Bhd", "Acme Singapore Pte Ltd", "Acme Group"). Their data access changes depending on which entity they are operating in. The topbar makes this context explicit and switchable.

### Switcher dropdown anatomy

```
[■ Acme Malaysia Sdn Bhd  ▾]
─────────────────────────────────
✓  Acme Malaysia Sdn Bhd         ← current (checkmark)
   Acme Group                    ← parent entity (if user has access)
   Acme Singapore Pte Ltd        ← sibling entity (if user has access)
─────────────────────────────────
   + Add Entity                  ← only visible with org:manage permission
```

Only entities within the user's hierarchy-scoped access appear. A regular employee sees only their own entity — the label is static, no dropdown triggered.

### Entity switching behavior
When user selects a different entity:
1. Auth session updates the active entity context
2. All scoped data re-fetches (employees, projects, reports visible in this entity)
3. App redirects to `/` (Home) — prevents showing stale data on the current page
4. Active entity persists in session across page refreshes

### Permission gating
| Permission | Behavior |
|---|---|
| `org:read` | User sees their own entity name as a static label — no dropdown |
| Any user with access to 2+ entities | Switcher dropdown is active |
| `org:manage` | Dropdown includes "+ Add Entity" option |

### Component
`EntitySwitcher` — lives in the topbar layout component.

### Data source
Entities are created and managed at Org → Legal Entities (`/org/legal-entities`). The switcher reads from this list filtered to the user's hierarchy access scope.

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

  {/* Entity switcher */}
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
- Org → Legal Entities (`/org/legal-entities`) — where entities are created and managed
