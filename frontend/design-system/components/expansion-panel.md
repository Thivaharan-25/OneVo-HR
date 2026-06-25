# Expansion Panel

The expansion panel is the secondary navigation layer that slides out to the right of the rail when a pillar with sub-navigation is selected. It is an independent floating card - not attached to the rail or the content area.

**Pillars with no panel (Home, Inbox, Chat):** Clicking these closes the panel entirely and navigates directly.

## Dimensions & Shape

| Property | Value |
|:---------|:------|
| Width (open) | **210px** |
| Height | 100% of the bottom row |
| Border-radius | **12px** on all corners |
| flex-shrink | 0 |

### Light Mode

| Property | Value |
|:---------|:------|
| Background | `#FAF9F6` - warm off-white, not pure white |
| Border | `1px solid #E8E8EC` |
| Shadow | `0 2px 12px rgba(0,0,0,0.08)` |

### Dark Mode

| Property | Value |
|:---------|:------|
| Background | `#000000` - pure black |
| Border | `1px solid rgba(255,255,255,0.06)` |
| Shadow | `0 2px 12px rgba(0,0,0,0.40)` |

## Open / Close Animation

The panel animates by **width + opacity simultaneously**. It does NOT use `transform: translateX`.

| State | Width | Opacity | Overflow |
|:------|:------|:--------|:---------|
| Open | 210px | 1 | visible |
| Closed | 0 | 0 | hidden |

```css
.panel-shell {
  transition: width 220ms cubic-bezier(0.16, 1, 0.3, 1),
              opacity 220ms cubic-bezier(0.16, 1, 0.3, 1);
}
.panel-shell.closed {
  width: 0;
  overflow: hidden;
  opacity: 0;
}
```

In Tailwind:
```tsx
<div className={cn(
  'transition-[width,opacity] duration-[220ms] [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] shrink-0',
  isOpen ? 'w-[210px] opacity-100' : 'w-0 opacity-0 overflow-hidden'
)}>
```

> Easing: `cubic-bezier(0.16,1,0.3,1)` - the `ease-out` spring curve. See [[frontend/design-system/foundations/motion|Motion]].

## Panel Head

Height: **44px**

| Property | Light | Dark |
|:---------|:------|:-----|
| Bottom border | `1px solid #EEEDE9` | `1px solid rgba(255,255,255,0.05)` |
| Padding | `0 10px 0 14px` | same |
| Title font-size | **12.5px** | same |
| Title font-weight | **600** | same |
| Title color | `#1E2140` | `rgba(255,255,255,0.88)` |

### Head Buttons (+ and close)

Size: **22x22px**, border-radius: **5px**

| State | Light bg | Light color | Dark bg | Dark color |
|:------|:---------|:------------|:--------|:-----------|
| Default | transparent | `#9499B0` | transparent | `rgba(255,255,255,0.25)` |
| Hover | `#EEECEA` | `#4C5278` | `rgba(255,255,255,0.07)` | `rgba(255,255,255,0.60)` |

- Close (`X`) icon: **12x12px**, stroke-width **1.75**
- Plus (`+`) icon: **14x14px**, stroke-width **2**

### + Create Dropdown

Triggered by the `+` button. Positioned absolutely below the button.

```
position: absolute
top: calc(100% + 4px)   right: 0
width: 200px            border-radius: 10px
padding: 5px
```

Light: bg `#FFFFFF`, border `1px solid #E2E3EA`, shadow `0 8px 24px rgba(0,0,0,0.10), 0 2px 6px rgba(0,0,0,0.06)`
Dark: bg `#1C1D27`, border `rgba(255,255,255,0.08)`

Entry animation: `opacity 0 -> 1`, `translateY(-6px) scale(0.97) -> translateY(0) scale(1)` over `140ms cubic-bezier(0.16,1,0.3,1)`

**Dropdown item:**
- Padding: `7px 9px`, border-radius: `7px`
- Font-size: 12.5px, color: `#4C5278` / `rgba(255,255,255,0.55)` dark
- Hover bg: `#F4F5F8` / `rgba(255,255,255,0.06)` dark
- Hover color: `#1E2140` / `rgba(255,255,255,0.90)` dark
- Icon: 13x13px, default `#9499B0`, hover turns `#5B4FE8`

**Separator inside dropdown:** `height: 1px`, bg `#F0F0F4` / `rgba(255,255,255,0.07)` dark

Close dropdown on: item click OR click outside.

## Panel Body

```css
padding: 6px 6px 10px;
overflow-y: auto;
flex: 1;
```

Scrollbar: `width: 3px`, thumb `#DDDBD5` (light) / `rgba(255,255,255,0.08)` (dark)

## Panel Item

| Property | Default | Hover | Active |
|:---------|:--------|:------|:-------|
| Padding | `5px 8px` | same | same |
| Border-radius | 6px | - | - |
| Font-size | **12.5px** | same | same |
| Font-weight | 400 | 400 | **500** |
| Color (light) | `#6B7194` | `#1E2140` | `#5B4FE8` |
| Background (light) | transparent | `#EEECEA` | `#ECEAFD` |
| Color (dark) | `rgba(255,255,255,0.38)` | `rgba(255,255,255,0.72)` | `#8C86F2` |
| Background (dark) | transparent | `rgba(255,255,255,0.05)` | `rgba(91,79,232,0.20)` |
| Icon size | **13x13px** (`size={13}`) | same | same |
| Icon stroke-width | **1.6** | same | same |
| Gap (icon + text) | 8px | - | - |
| Transition | `background 120ms, color 120ms` | - | - |

```tsx
<a className={cn(
  'flex items-center gap-2 px-2 py-[5px] rounded-[6px] text-[12.5px] whitespace-nowrap no-underline cursor-pointer transition-[background,color] duration-[120ms]',
  isActive
    ? 'bg-[#ECEAFD] text-[#5B4FE8] font-medium dark:bg-[rgba(91,79,232,0.20)] dark:text-[#8C86F2]'
    : 'font-normal text-[#6B7194] hover:bg-[#EEECEA] hover:text-[#1E2140] dark:text-white/[0.38] dark:hover:bg-white/[0.05] dark:hover:text-white/[0.72]'
)}>
  <Icon size={13} strokeWidth={1.6} aria-hidden="true" />
  {label}
</a>
```

## Panel Items Per Pillar

All panel items, exact Lucide icon names, routes, and permission keys:

### People
| Label | Lucide Icon | Route | Permission |
|:------|:------------|:------|:-----------|
| Employees | `UserCheck` | `/people/employees` | `employees:read` |
| Onboarding | `UserPlus` | `/people/onboarding` | `employees:write` |
| Offboarding | `UserMinus` | `/people/offboarding` | `employees:write` |
| Checklist Templates | `ListChecks` | `/people/checklist-templates` | `employees:write` |

Create actions: `UserPlus` Add employee , `Upload` Bulk onboarding/import

### Time Off
| Label | Lucide Icon | Route | Permission |
|:------|:------------|:------|:-----------|
| My Time Off | `CalendarCheck` | `/time-off` | `time_off:create` OR `time_off:read-own` |
| Team Time Off | `UsersRound` | `/time-off/team` | `time_off:approve` OR `time_off:read` |
| Time Off Types | `Tags` | `/time-off/types` | `time_off:manage` |
| Time Off Policies | `ClipboardList` | `/time-off/policies` | `time_off:manage` |
| Entitlements | `WalletCards` | `/time-off/entitlements` | `time_off:manage` |

Create actions: `PlaneTakeoff` Apply time off

### Time & Attendance
| Label | Lucide Icon | Route | Permission |
|:------|:------------|:------|:-----------|
| Attendance | `UserCheck2` | `/time-attendance/attendance` | `attendance:read-own` OR `attendance:read` |
| Schedules | `CalendarClock` | `/time-attendance/schedules` | `attendance:read` |
| Clock-in Policy | `Clock` | `/time-attendance/clock-in-policy` | `attendance:write` |
| Overtime Rules | `Timer` | `/time-attendance/overtime-rules` | `attendance:write` |

Create actions: row-level correction actions , overtime request actions

### Work
| Label | Lucide Icon | Route | Permission |
|:------|:------------|:------|:-----------|
| Projects | `FolderKanban` | `/work/projects` | `projects:read` |
| Work Items | `CircleCheck` | `/work/items` | `tasks:read` |
| Documents | `FileText` | `/work/documents` | `documents:read` |
| Project Members | `UsersRound` | `/work/members` | `projects:read` |
| Worklogs | `Clock` | `/work/worklogs` | `time:read` |

Create actions: `FolderPlus` New project , `CirclePlus` New work item , `Clock` Log work

### Calendar
Calendar is a direct main sidebar item at `/calendar` with `calendar:read`. It does not open a Time & Attendance setup panel and must not contain separate setup links for schedules, holiday calendars, or attendance rules.

Create actions: `CalendarPlus` New event , `Send` Send invite

### Monitoring
| Label | Lucide Icon | Route | Permission |
|:------|:------------|:------|:-----------|
| Live Status | `Activity` | `/monitoring` | `monitoring:view` |
| Alerts | `Bell` | `/monitoring/alerts` | `monitoring:alerts:read` |
| Device Health | `Monitor` | `/monitoring/devices` | `agent:view-health` |

### Settings
| Label | Lucide Icon | Route | Permission |
|:------|:------------|:------|:-----------|
| General | `Sliders` | `/settings/general` | `settings:read` |
| Branding | `Palette` | `/settings/branding` | `settings:branding` |
| Users | `Users` | `/settings/users` | `users:manage` |
| Roles & Permissions | `Lock` | `/settings/roles` | `roles:manage` |
| Notifications | `BellRing` | `/settings/notifications` | `settings:notifications` |
| Billing | `CreditCard` | `/settings/billing` | `settings:billing` |
| Devices | `Monitor` | `/settings/devices` | `settings:device` |
| Audit Log | `ScrollText` | `/settings/audit` | `audit:read` |

Create actions: `UserPlus` Add user , `Lock` New role , `Monitor` Add device
## Related

- [[frontend/design-system/components/shell-layout|Shell Layout]] - overall layout this panel sits in
- [[frontend/design-system/components/nav-rail|Nav Rail]] - rail that triggers this panel
- [[frontend/architecture/sidebar-nav|Sidebar Nav Map]] - canonical nav reference
- [[frontend/design-system/foundations/motion|Motion]] - animation timing, `ease-out` curve
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] - brand accent color values
- [[Userflow/Dashboard/shell-navigation|Shell Navigation]] - interaction flow

