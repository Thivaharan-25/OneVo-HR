# Shell Navigation

**Area:** Shell — Icon Rail + Expansion Panel + Topbar  
**Trigger:** User is authenticated and the dashboard layout is mounted  
**Required Permission:** Any authenticated user (individual pillars gated per permission — see [[frontend/design-system/components/nav-rail|Nav Rail]])

---

## Preconditions

- User is authenticated (valid JWT)
- Dashboard layout is rendered: topbar, rail, optional panel, content area
- Active pillar is set (defaults to `workforce` on first load)

---

## Flow 1 — Clicking a Pillar WITH a Panel

**Example:** User clicks "Workforce" on the rail

### Step 1: Rail Item Becomes Active

- **UI:** Clicked pillar item background → `rgba(255,255,255,0.10)`, text color → `rgba(255,255,255,0.95)`. Previously active item returns to default state.
- **State change:** `activePillar = 'workforce'`, `isPanelOpen = true`

### Step 2: Expansion Panel Opens

- **UI:** Panel shell animates from `width: 0, opacity: 0` → `width: 210px, opacity: 1` over `220ms cubic-bezier(0.16,1,0.3,1)`. Panel title updates to "Workforce". Panel body renders the pillar's sub-navigation items.
- **Default active item:** First item in the list is pre-highlighted in accent color (`#ECEAFD` bg, `#5B4FE8` text). Navigation routes to that item's route.
- **API:** None — panel content is static config, not fetched.

### Step 3: Breadcrumb Updates

- **UI:** Topbar breadcrumb updates to: `[Entity Name] / Workforce / Presence` (pillar + first active panel item)

### Step 4: Content Area Navigates

- **UI:** Content area renders the default route for the pillar (e.g., `/workforce` → Presence page)

---

## Flow 2 — Clicking a Panel Item

**Example:** User clicks "Projects" under Workforce

### Step 1: Panel Item Becomes Active

- **UI:** Clicked item → `bg-[#ECEAFD] text-[#5B4FE8] font-medium`. Previous active item returns to default.

### Step 2: Breadcrumb and Content Update

- **UI:** Breadcrumb → `[Entity Name] / Workforce / Projects`. Content area navigates to `/workforce/projects`.
- **Rail:** Workforce item remains active (clicking a panel item does not change the active pillar).

---

## Flow 3 — Clicking a Pillar WITHOUT a Panel

**Pillars with no panel:** Home (`/`), Inbox (`/inbox`), Chat (`/chat`)

### Step 1: Rail Item Becomes Active

- **UI:** Clicked item highlighted. Previous item returns to default.
- **State change:** `activePillar = 'home'`, `isPanelOpen = false`

### Step 2: Panel Closes

- **UI:** If a panel was open: animates to `width: 0, opacity: 0` over `220ms`. No panel renders for no-panel pillars.
- **Breadcrumb:** Updates to `[Entity Name] / Home` — only two levels (no third level without a panel).

### Step 3: Content Navigates Directly

- **UI:** Content area navigates to the pillar's direct route.

---

## Flow 4 — + Create Dropdown

**Trigger:** User clicks the `+` button in the panel head

### Step 1: Dropdown Opens

- **UI:** Dropdown appears absolutely positioned below the `+` button (`top: calc(100% + 4px), right: 0`). Entry animation: fade + `translateY(-6px) scale(0.97)` → normal over `140ms`. Lists contextual create actions for the current pillar.

### Step 2: User Selects an Action or Dismisses

- **Select action:** Dropdown closes, action is triggered (open create modal / navigate to create page).
- **Click outside:** `document` click listener closes the dropdown.

---

## Flow 5 — Entity Switcher in Topbar

**Trigger:** User clicks the entity name in the topbar (only visible if user has access to 2+ entities)

### Step 1: Dropdown Opens

- **UI:** Dropdown shows accessible entities. Current entity has a checkmark. Includes "+ Add Entity" if user has `org:manage`.

### Step 2: User Selects an Entity

- **Auth:** Session updates to new entity context.
- **Data:** All scoped data re-fetches.
- **Navigation:** App redirects to `/` (Home). Active pillar resets.

### Step 3: No Dropdown for Single-Entity Users

- **UI:** Entity name renders as a static label (no chevron, no click behavior) for users with access to only one entity.

---

## Active State Rules

| Element | Active condition |
|:--------|:----------------|
| Rail item | Current URL is within that pillar's route segment |
| Panel item | Current URL exactly matches that item's route |
| Both rail + panel | When a sub-page is active, both the pillar AND the specific panel item are highlighted |

---

## Error Scenarios

| Scenario | Behaviour |
|:---------|:----------|
| User navigates directly to a URL (e.g., `/workforce/projects`) | Rail highlights Workforce, panel opens with Projects active — state is derived from URL |
| Permission revoked mid-session | On next navigation, pillar is hidden and user is redirected to first accessible route |
| Pillar has no items the user can see (all permission-gated) | Panel still opens but body is empty — no items render |

---

## Related

- [[frontend/design-system/components/nav-rail|Nav Rail]] — icon rail spec (dimensions, icons, states)
- [[frontend/design-system/components/expansion-panel|Expansion Panel]] — panel spec (dimensions, animation, items)
- [[frontend/architecture/topbar|Topbar]] — topbar spec including breadcrumb and entity switcher
- [[frontend/architecture/sidebar-nav|Sidebar Nav Map]] — all pillar routes and permission keys
- [[Userflow/Dashboard/dashboard-overview|Dashboard Overview]] — what renders in the content area on load
