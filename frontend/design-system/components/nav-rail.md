# Nav Rail

The icon rail is the narrow dark navigation strip on the far left of the shell. It is always rendered — it never collapses or hides. It is a standalone floating card with a dark background that does not change in dark mode.

## Dimensions & Shape

| Property | Value |
|:---------|:------|
| Width | **52px** (fixed, never changes) |
| Height | 100% of the bottom row |
| Background | `#17181F` — always dark, light and dark mode identical |
| Border-radius | **12px** on all corners |
| Border | none |
| Shadow | `0 2px 16px rgba(0,0,0,0.20)` |
| Padding | `10px 0` top and bottom |
| flex-shrink | 0 (never compresses) |

## Internal Structure

```
┌── rail (52px) ─────────────────┐
│  ┌── rail-nav (flex:1) ──────┐ │   ← 5px horizontal padding, overflow hidden
│  │  [item 42px wide]         │ │
│  │  [item]                   │ │
│  │  [item]  ← 9 pillars total│ │
│  │  [item]                   │ │
│  │  [item]                   │ │
│  │  [item]                   │ │
│  │  [item]                   │ │
│  │  ─── separator ───        │ │   ← 24px wide, 1px, between Chat and Admin
│  │  [item]                   │ │
│  │  [item]                   │ │
│  └───────────────────────────┘ │
│  ─── separator ───             │   ← above avatar
│  [avatar 26px circle]          │
└────────────────────────────────┘
```

## Rail Item

| Property | Default | Hover | Active |
|:---------|:--------|:------|:-------|
| Width | 42px | 42px | 42px |
| Padding | `7px 0 6px` | same | same |
| Border-radius | 8px | 8px | 8px |
| Background | transparent | `rgba(255,255,255,0.07)` | `rgba(255,255,255,0.10)` |
| Color | `rgba(255,255,255,0.28)` | `rgba(255,255,255,0.72)` | `rgba(255,255,255,0.95)` |
| Transition | `background 120ms, color 120ms` | — | — |

### Icon (inside rail item)

| Property | Value |
|:---------|:------|
| Size | **16×16px** (`size={16}` in Lucide) |
| Stroke-width | **1.6** — same in all states, never changes on active |
| Color | inherited from rail item |

### Label (below icon)

| Property | Value |
|:---------|:------|
| Font-size | **9px** |
| Font-weight | **500** |
| Line-height | 1 |
| Text-align | center |
| White-space | nowrap |
| Color | inherited from rail item |

## Separator

```css
width: 24px;
height: 1px;
background: rgba(255,255,255,0.07);
margin: 4px 0;
flex-shrink: 0;
```

One separator appears between the Chat and Admin items. A second separator appears above the avatar.

## Avatar (Bottom of Rail)

| Property | Value |
|:---------|:------|
| Size | 26×26px |
| Shape | Full circle (`border-radius: 50%`) |
| Background | `linear-gradient(135deg, #C9A96E, #E8C98A)` — gold gradient |
| Font-size | 10px |
| Font-weight | 700 |
| Text color | `#1a1208` — near-black brown |
| Margin-top | 4px |
| Hover | `opacity: 0.85` |

## Pillar Map — Exact Icon Names (Lucide React)

Display order top to bottom. Pillars marked **No Panel** navigate directly without opening the expansion panel.

| Position | Pillar | Lucide Import Name | Has Panel | Default Route | Permission |
|:---------|:-------|:------------------|:----------|:--------------|:-----------|
| 1 | Home | `House` | **No** | `/` | Any authenticated |
| 2 | Inbox | `Inbox` | **No** | `/inbox` | Any authenticated |
| 3 | People | `Users` | Yes | `/people/employees` | `employees:read` OR `leave:read` |
| 4 | Workforce | `LayoutDashboard` | Yes | `/workforce` | `workforce:read` |
| 5 | Org | `Network` | Yes | `/org` | `org:read` |
| 6 | Calendar | `Calendar` | Yes | `/calendar` | `calendar:read` |
| 7 | Chat | `MessageCircle` | **No** | `/chat` | `chat:read` |
| — | *separator* | — | — | — | — |
| 8 | Admin | `Shield` | Yes | `/admin/users` | `admin:read` |
| 9 | Settings | `Settings` | Yes | `/settings/general` | `settings:read` |

> **Critical:** Home, Inbox, and Chat have **no panel**. Clicking them closes any open panel and navigates directly. Do not render a panel for these three.

## Tailwind Implementation

```tsx
// src/components/layout/rail.tsx
'use client';

import { House, Inbox, Users, LayoutDashboard, Network, Calendar,
         MessageCircle, Shield, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useNavStore } from '@/stores/use-nav-store';

const PILLARS = [
  { key: 'home',      label: 'Home',      Icon: House,           hasPanel: false, route: '/' },
  { key: 'inbox',     label: 'Inbox',     Icon: Inbox,           hasPanel: false, route: '/inbox' },
  { key: 'people',    label: 'People',    Icon: Users,           hasPanel: true,  route: '/people/employees' },
  { key: 'workforce', label: 'Workforce', Icon: LayoutDashboard, hasPanel: true,  route: '/workforce' },
  { key: 'org',       label: 'Org',       Icon: Network,         hasPanel: true,  route: '/org' },
  { key: 'calendar',  label: 'Calendar',  Icon: Calendar,        hasPanel: true,  route: '/calendar' },
  { key: 'chat',      label: 'Chat',      Icon: MessageCircle,   hasPanel: false, route: '/chat' },
  // separator here
  { key: 'admin',     label: 'Admin',     Icon: Shield,          hasPanel: true,  route: '/admin/users' },
  { key: 'settings',  label: 'Settings',  Icon: Settings,        hasPanel: true,  route: '/settings/general' },
];

const SEPARATOR_BEFORE = new Set(['admin']); // separator rendered before these keys

export function NavRail() {
  const { activePillar, setActivePillar } = useNavStore();

  return (
    <nav className="w-[52px] h-full bg-[#17181F] rounded-[12px] flex flex-col items-center py-[10px] shadow-[0_2px_16px_rgba(0,0,0,0.20)] shrink-0 select-none">

      {/* Pillar items */}
      <div className="flex-1 flex flex-col items-center gap-0.5 w-full px-[5px] overflow-hidden">
        {PILLARS.map(pillar => (
          <>
            {SEPARATOR_BEFORE.has(pillar.key) && (
              <div key={`sep-${pillar.key}`} className="w-6 h-px bg-white/[0.07] my-1 shrink-0" />
            )}
            <button
              key={pillar.key}
              onClick={() => setActivePillar(pillar.key, pillar.hasPanel)}
              className={cn(
                'w-[42px] flex flex-col items-center justify-center gap-1 py-[7px] pb-[6px] rounded-[8px] cursor-pointer transition-[background,color] duration-[120ms] border-none',
                activePillar === pillar.key
                  ? 'bg-white/10 text-white/95'
                  : 'text-white/[0.28] hover:bg-white/[0.07] hover:text-white/[0.72]'
              )}
            >
              <pillar.Icon size={16} strokeWidth={1.6} aria-hidden="true" />
              <span className="text-[9px] font-medium leading-none text-center whitespace-nowrap text-inherit">
                {pillar.label}
              </span>
            </button>
          </>
        ))}
      </div>

      {/* Avatar */}
      <div className="flex flex-col items-center gap-0.5 w-full px-[5px]">
        <div className="w-6 h-px bg-white/[0.07] my-1 shrink-0" />
        <div className="w-[26px] h-[26px] rounded-full bg-gradient-to-br from-[#C9A96E] to-[#E8C98A] flex items-center justify-center text-[10px] font-bold text-[#1a1208] cursor-pointer hover:opacity-85 mt-1">
          A
        </div>
      </div>
    </nav>
  );
}
```

## Dark Mode

The rail background (`#17181F`) does **not change** in dark mode. It is always this dark tone. The dark mode body background (`#0A0A0D`) makes the rail slightly more prominent by contrast but the rail surface color never changes.

## Zustand Store

```tsx
// src/stores/use-nav-store.ts
interface NavStore {
  activePillar: string;
  isPanelOpen: boolean;
  setActivePillar: (key: string, hasPanel: boolean) => void;
}

export const useNavStore = create<NavStore>((set) => ({
  activePillar: 'workforce',
  isPanelOpen: true,
  setActivePillar: (key, hasPanel) =>
    set({ activePillar: key, isPanelOpen: hasPanel }),
}));
```

## Related

- [[frontend/design-system/components/shell-layout|Shell Layout]] — overall layout this rail sits in
- [[frontend/design-system/components/expansion-panel|Expansion Panel]] — the panel this rail controls
- [[frontend/architecture/sidebar-nav|Sidebar Nav Map]] — canonical pillar + permission reference
- [[frontend/design-system/foundations/iconography|Iconography]] — Lucide icon system, sizes
- [[Userflow/Dashboard/shell-navigation|Shell Navigation]] — interaction flow
