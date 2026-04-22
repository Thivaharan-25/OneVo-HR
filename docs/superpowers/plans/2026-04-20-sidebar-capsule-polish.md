# Sidebar Capsule Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tighten the centered `IconRail` capsule: compact icons, remove orphaned spacer, add violet-tinted border and ambient glow, and visually group utility icons.

**Architecture:** Two targeted file edits — CSS class update in `index.css` and JSX cleanup in `IconRail.tsx`. No logic changes, no new components.

**Tech Stack:** React, Tailwind CSS, custom CSS class `.rail-capsule`

---

## File Map

| File | Change |
|---|---|
| `demo/src/index.css` | Update `.rail-capsule` border + box-shadow |
| `demo/src/components/layout/IconRail.tsx` | Remove spacer div, `h-10`→`h-8`, add `mt-2` before Admin |

---

### Task 1: Update `.rail-capsule` CSS

**Files:**
- Modify: `demo/src/index.css` (lines 98–104)

- [ ] **Step 1: Edit the `.rail-capsule` block**

Replace:
```css
  /* Floating rail capsule */
  .rail-capsule {
    background: rgba(13, 13, 24, 0.92);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06);
  }
```

With:
```css
  /* Floating rail capsule */
  .rail-capsule {
    background: rgba(13, 13, 24, 0.92);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(124,58,237,0.18);
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 30px rgba(124,58,237,0.07), inset 0 1px 0 rgba(255,255,255,0.07);
  }
```

- [ ] **Step 2: Commit**

```bash
git add demo/src/index.css
git commit -m "style: violet-tinted border and ambient glow on rail capsule"
```

---

### Task 2: Compact icons, remove spacer, group utility

**Files:**
- Modify: `demo/src/components/layout/IconRail.tsx`

- [ ] **Step 1: Change icon button height and add utility gap**

In the `button` inside the `.map()` (around line 57), update the `className` in the `cn()` call:

Replace the first positional class string:
```tsx
'w-full h-10 rounded-xl flex items-center justify-center relative transition-all duration-150 group',
```

With:
```tsx
'w-full h-8 rounded-xl flex items-center justify-center relative transition-all duration-150 group',
pillarKey === 'admin' && 'mt-2',
```

The full `cn()` call should look like:
```tsx
className={cn(
  'w-full h-8 rounded-xl flex items-center justify-center relative transition-all duration-150 group',
  pillarKey === 'admin' && 'mt-2',
  active
    ? 'bg-violet-600/20 text-violet-300 shadow-[inset_0_0_0_1px_rgba(124,58,237,0.35),0_0_16px_rgba(124,58,237,0.15)]'
    : 'text-white/30 hover:text-white/65 hover:bg-white/[0.05]'
)}
```

- [ ] **Step 2: Remove the bottom spacer div**

Delete this entire line (around line 81):
```tsx
      {/* Bottom spacer */}
      <div className="shrink-0 w-7 h-[1px] bg-white/[0.07] mb-1" />
```

- [ ] **Step 3: Start dev server and visually verify**

```bash
cd demo && npm run dev
```

Open the app and confirm:
- Capsule is vertically centered, no trailing line at the bottom
- Icons are visibly more compact (tighter height)
- A small gap appears between the Inbox icon and the Admin icon
- Capsule border has a faint violet tint
- Capsule has a soft violet ambient glow (visible against the dark background)

- [ ] **Step 4: Commit**

```bash
git add demo/src/components/layout/IconRail.tsx
git commit -m "style: compact h-8 icons, remove spacer, group utility icons in rail"
```
