# Spec: Sidebar Active State — Icon Bloom

**Date:** 2026-04-20

## Problem

The current active state (`bg-violet-600/20` + inset border ring + left accent bar) is a generic admin dashboard pattern. It uses hard rectangular geometry that conflicts with the premium, luminous feel of the rest of the ONEVO design language.

## Design

Replace all hard-edge active indicators with a pure-light bloom treatment. No background box. No border ring. No accent bar. The active icon becomes its own light source.

---

### 1. Active State (`IconRail.tsx`)

**Remove:**
- `bg-violet-600/20` background
- `shadow-[inset_0_0_0_1px_rgba(124,58,237,0.35),0_0_16px_rgba(124,58,237,0.15)]` box-shadow
- The left accent bar `<span>` element entirely

**Add — bloom overlay div:**
```tsx
{active && (
  <span className="bloom-active absolute rounded-[14px]" style={{ inset: '-8px' }} />
)}
```

**Add — dot indicator (render after `<Icon>` so it layers on top):**
```tsx
{active && (
  <span className="absolute -bottom-[7px] left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-violet-400/90 shadow-glow-violet z-10" />
)}
```

**Icon treatment (active):**
- Color: `text-violet-200` (no true gradient stroke — Lucide uses `currentColor`, adding per-icon SVG defs is out of scope)
- Filter: `[filter:drop-shadow(0_0_7px_rgba(196,181,253,0.8))]` via Tailwind arbitrary value
- `strokeWidth`: `2.25` (already correct)

**Button className (active branch):**
```tsx
active
  ? 'text-violet-200 [filter:drop-shadow(0_0_7px_rgba(196,181,253,0.8))]'
  : 'text-white/30 hover:text-white/65'
```

---

### 2. Hover State — Soft Bloom Preview (`IconRail.tsx`)

Add a hover bloom overlay to every button. Visible only on inactive buttons via the `group` class:

```tsx
<span className="bloom-hover absolute rounded-[14px] opacity-0 group-hover:opacity-100 transition-opacity duration-[180ms]" style={{ inset: '-4px' }} />
```

Place this before the `<Icon>` element. The `active` branch should NOT render `bloom-hover` (it has `bloom-active` instead).

---

### 3. CSS — Bloom Classes + Keyframe (`index.css`)

Add inside the `@layer utilities` block (or below `.rail-capsule`):

```css
/* Active bloom — place BEFORE the <Icon> in DOM so icon layers above naturally */
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

/* Hover bloom — place BEFORE the <Icon> in DOM */
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

---

## Files to Change

| File | Change |
|---|---|
| `demo/src/components/layout/IconRail.tsx` | Remove bg, shadow, left-bar span. Add `bloom-active` + dot spans. Add `bloom-hover` span. Update active className. |
| `demo/src/index.css` | Add `.bloom-active`, `.bloom-hover`, `@keyframes bloom-in` |

## What's Removed

- `bg-violet-600/20` class on active button
- `shadow-[inset_0_0_0_1px_rgba(124,58,237,0.35),0_0_16px_rgba(124,58,237,0.15)]` on active button
- `<span className="absolute left-0 top-3 bottom-3 w-[3px] ...">`

## What Stays

- Rail capsule shape, border, ambient glow
- Logo mark
- Icon layout, group gap (`mt-2` before utility icons)
- `transition-all duration-150` on the button element
- Inbox badge dot
- `strokeWidth` differences between active/inactive
