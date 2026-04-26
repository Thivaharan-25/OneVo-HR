# Shell Layout

The OneVo shell uses a **floating-cards** layout. Every chrome element — topbar, rail, panel, content area — is a separate rounded card floating on a tinted base with consistent gaps. Nothing is flush to the viewport edge.

## Visual Structure

```
┌─ body: bg #EDEEF2 / #0A0A0D dark ── padding: 8px ── gap: 6px ─────────────────────┐
│                                                                                     │
│  ┌─────────────────────────────────────────── topbar (40px h, radius 10px) ──────┐ │
│  │  [Acme Malaysia ▾]  /  Workforce  /  Presence     [Search ⌘K]   🔔  ☀  [A]  │ │
│  └─────────────────────────────────────────────────────────────────────────────── ┘ │
│                                                                                     │
│  ┌─ rail ─┐  ┌─── panel ────────┐  ┌─── content ──────────────────────────────┐   │
│  │ 52px   │  │ 210px            │  │ flex: 1                                  │   │
│  │ r:12px │  │ r:12px           │  │ r:10px                                   │   │
│  │#17181F │  │ #FAF9F6 (light)  │  │ white (light) / #111118 (dark)           │   │
│  │ always │  │ #000000 (dark)   │  │                                          │   │
│  │  dark  │  │ slides in/out    │  │ padding: 24px                            │   │
│  └────────┘  └──────────────────┘  └──────────────────────────────────────────┘   │
│              ← gap: 6px between every card                                          │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Body

```css
body {
  background: #EDEEF2;   /* light — neutral-100 */
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 8px;          /* gap from viewport edge on all sides */
  gap: 6px;              /* gap between topbar and bottom-row */
  overflow: hidden;
  font-family: var(--font-body);
  -webkit-font-smoothing: antialiased;
}

body.dark {
  background: #0A0A0D;
}
```

Tailwind: `flex flex-col h-screen p-2 gap-1.5 overflow-hidden bg-[#EDEEF2] dark:bg-[#0A0A0D]`

## Bottom Row

The flex row that holds the rail, optional panel, and content area:

```css
.bottom-row {
  flex: 1;
  display: flex;
  gap: 6px;
  min-height: 0;   /* REQUIRED — prevents flex child from overflowing */
}
```

Tailwind: `flex-1 flex gap-1.5 min-h-0`

## Content Area

```css
.content {
  flex: 1;
  min-width: 0;          /* REQUIRED — prevents flex child overflow */
  background: #FFFFFF;
  border-radius: 10px;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dark .content {
  background: #111118;
  color: #C8CADC;
}
```

Tailwind: `flex-1 min-w-0 bg-white dark:bg-[#111118] rounded-[10px] p-6 overflow-y-auto flex flex-col gap-3`

### Content Typography

| Element | Size | Weight | Color (light) | Color (dark) |
|:--------|:-----|:-------|:--------------|:-------------|
| Page title | 18px | 600 | `#1A1D28` | `#E8E9F0` |
| Page subtitle | 12px | 400 | `#9499B0` | `#6B7194` |

```tsx
<h1 className="text-[18px] font-semibold text-[#1A1D28] dark:text-[#E8E9F0] tracking-[-0.02em]">
  Calendar · Schedules
</h1>
<p className="text-[12px] text-[#9499B0]">Subtitle text</p>
```

## Next.js Implementation

```
src/app/
├── layout.tsx                   # Root: <html data-theme> + font vars + providers
└── (dashboard)/
    └── layout.tsx               # Shell: topbar → bottom-row → rail + panel + main
```

```tsx
// src/app/(dashboard)/layout.tsx
import { NavRail } from '@/components/layout/rail';
import { ExpansionPanel } from '@/components/layout/panel';
import { Topbar } from '@/components/layout/topbar';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col h-screen p-2 gap-1.5 overflow-hidden bg-[#EDEEF2] dark:bg-[#0A0A0D]">
      <Topbar />
      <div className="flex-1 flex gap-1.5 min-h-0">
        <NavRail />
        <ExpansionPanel />
        <main className="flex-1 min-w-0 bg-white dark:bg-[#111118] rounded-[10px] p-6 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
```

## What Makes This Layout Different from a Traditional Sidebar

A traditional sidebar is flush left, edge to edge, full height. This is **not that**.

| Traditional sidebar | OneVo floating-cards |
|:--------------------|:---------------------|
| Flush to viewport edge | `8px` gap on all sides |
| Continuous surface | Each element is an independent card |
| No gap between sidebar and content | `6px` gap between every card |
| Border separates sections | Shadow + rounded corners separate sections |
| Full-height continuous panel | Rail, panel, content are separate rounded rectangles |

An AI building a traditional sidebar layout will produce the wrong result. The `p-2 gap-1.5` on the body and `rounded-[12px]` on the rail are what define this design.

## Related

- [[frontend/design-system/components/nav-rail|Nav Rail]] — icon rail (52px, dark, floating)
- [[frontend/design-system/components/expansion-panel|Expansion Panel]] — slide-out sub-nav panel
- [[frontend/architecture/topbar|Topbar]] — topbar component spec
- [[frontend/architecture/sidebar-nav|Sidebar Nav Map]] — pillar structure, routes, permissions
- [[Userflow/Dashboard/shell-navigation|Shell Navigation]] — how users interact with the shell
