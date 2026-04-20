# Sidebar Active State — Icon Bloom Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the sidebar's flat-tinted active state (background box + inset ring + left accent bar) with a pure-light Icon Bloom treatment — a radial glow behind the active icon with an animated entrance, a glowing dot indicator, and a soft hover preview bloom on inactive icons.

**Architecture:** Two-file change. CSS classes + keyframe go into `index.css` inside the existing `@layer utilities` block. `IconRail.tsx` replaces the active button's className and child elements to use those classes. No new components, no new files.

**Tech Stack:** React, Tailwind CSS, Lucide icons, plain CSS keyframe animation

---

## File Map

| File | Change |
|---|---|
| `demo/src/index.css` | Add `.bloom-active`, `.bloom-hover`, `@keyframes bloom-in` inside `@layer utilities` |
| `demo/src/components/layout/IconRail.tsx` | Replace active button className + children (remove bg/shadow/left-bar, add bloom spans + dot) |

---

## Task 1: Add bloom CSS to `index.css`

**Files:**
- Modify: `demo/src/index.css:104` (insert before closing `}` of `@layer utilities`)

- [ ] **Step 1: Open `demo/src/index.css` and insert the following block on a new line after line 104 (after `.rail-capsule { ... }`) and before the closing `}` of `@layer utilities` on line 105:**

```css
  /* Icon bloom — active + hover states */
  .bloom-active {
    background: radial-gradient(circle at center,
      rgba(139, 92, 246, 0.28) 0%,
      rgba(168, 85, 247, 0.12) 42%,
      rgba(124, 58, 237, 0.04) 65%,
      transparent 80%
    );
    animation: bloom-in 220ms cubic-bezier(0.34, 1.4, 0.64, 1) forwards;
    pointer-events: none;
  }

  .bloom-hover {
    background: radial-gradient(circle at center,
      rgba(124, 58, 237, 0.13) 0%,
      rgba(168, 85, 247, 0.05) 55%,
      transparent 75%
    );
    pointer-events: none;
  }

  @keyframes bloom-in {
    from { opacity: 0; transform: scale(0.55); }
    to   { opacity: 1; transform: scale(1); }
  }
```

The result: `@layer utilities { ... .rail-capsule { ... } .bloom-active { ... } .bloom-hover { ... } @keyframes bloom-in { ... } }`

- [ ] **Step 2: Commit**

```bash
git add demo/src/index.css
git commit -m "feat: add bloom-active, bloom-hover css classes and keyframe"
```

---

## Task 2: Update `IconRail.tsx` button rendering

**Files:**
- Modify: `demo/src/components/layout/IconRail.tsx`

The current button render block looks like this (inside the `.map()`):

```tsx
return (
  <button
    key={pillarKey}
    onClick={() => handleClick(pillarKey, defaultPath)}
    title={label}
    className={cn(
      'w-full flex items-center justify-center py-3 rounded-xl relative transition-all duration-150 group',
      active
        ? 'bg-violet-600/20 text-violet-300 shadow-[inset_0_0_0_1px_rgba(124,58,237,0.35),0_0_16px_rgba(124,58,237,0.15)]'
        : 'text-white/30 hover:text-white/65 hover:bg-white/[0.05]'
    )}
  >
    {active && (
      <span className="absolute left-0 top-3 bottom-3 w-[3px] rounded-r-full bg-gradient-to-b from-violet-400 to-purple-500 shadow-glow-violet" />
    )}
    <Icon size={24} strokeWidth={active ? 2 : 1.75} />
    {pillarKey === 'inbox' && inboxCount > 0 && (
      <span className="absolute top-2 right-2 w-[6px] h-[6px] rounded-full bg-violet-400 shadow-glow-violet" />
    )}
  </button>
)
```

- [ ] **Step 1: Replace the entire `return (...)` block inside the `.map()` with:**

```tsx
return (
  <button
    key={pillarKey}
    onClick={() => handleClick(pillarKey, defaultPath)}
    title={label}
    className={cn(
      'w-full flex items-center justify-center py-3 rounded-xl relative transition-all duration-150 group',
      active
        ? 'text-violet-200 [filter:drop-shadow(0_0_7px_rgba(196,181,253,0.8))]'
        : 'text-white/30 hover:text-white/65'
    )}
  >
    {active ? (
      <span className="bloom-active absolute rounded-[14px]" style={{ inset: '-8px' }} />
    ) : (
      <span className="bloom-hover absolute rounded-[14px] opacity-0 group-hover:opacity-100 transition-opacity duration-[180ms]" style={{ inset: '-4px' }} />
    )}
    <Icon size={24} strokeWidth={active ? 2.25 : 1.75} />
    {active && (
      <span className="absolute -bottom-[7px] left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-violet-400/90 shadow-glow-violet z-10" />
    )}
    {pillarKey === 'inbox' && inboxCount > 0 && (
      <span className="absolute top-2 right-2 w-[6px] h-[6px] rounded-full bg-violet-400 shadow-glow-violet" />
    )}
  </button>
)
```

Key changes:
- `className` active branch: removed `bg-violet-600/20`, removed `shadow-[...]`, added `text-violet-200` + drop-shadow filter
- `className` inactive branch: removed `hover:bg-white/[0.05]` (replaced by bloom-hover span)
- Removed: left accent bar `<span className="absolute left-0 top-3 bottom-3 w-[3px] ...">`
- Added: `bloom-active` span (when active) OR `bloom-hover` span (when inactive) — both before `<Icon>` so icon layers above
- Added: dot indicator `<span>` after `<Icon>` (when active)
- `strokeWidth` active: `2` → `2.25`

- [ ] **Step 2: Verify the dev server is running and open the demo in the browser**

```bash
cd demo && npm run dev
```

Navigate to any page. Check:
- Active icon has a soft radial glow with no box/bar — clicking a new icon re-triggers the bloom animation
- Hovering inactive icons shows a faint glow preview that fades in
- Inbox badge dot still appears in the top-right corner when there are notifications
- No layout shift — the dot indicator sits below the capsule without pushing other icons

- [ ] **Step 3: Commit**

```bash
git add demo/src/components/layout/IconRail.tsx
git commit -m "feat: replace sidebar active state with icon bloom treatment"
```

---

## Done

The sidebar now uses a pure-light bloom as the active indicator. No hard geometry. The active icon glows with an animated radial haze and a tiny glowing dot beneath it. Inactive icons preview the bloom softly on hover.
