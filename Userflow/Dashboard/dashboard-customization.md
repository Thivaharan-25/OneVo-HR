# Dashboard Customization

**Area:** Dashboard  
**Trigger:** User clicks "Customize" button in the dashboard topbar (user action â€” on demand)  
**Required Permission(s):** Any authenticated user (customization is within the user's own permission ceiling â€” they cannot add zones or widgets they don't have access to)  
**Related Permissions:** `workforce:view`, `employees:read`, `leave:read`, `settings:system`, `grievance:read` â€” each gates specific widgets in the Widget Library

---

## Preconditions

- User is signed in with a valid JWT
- User is on the `/dashboard` page
- Dashboard has already rendered (customization modifies an existing layout)

---

## Flow Steps

### Step 1: Enter Edit Mode

- **UI:** User clicks "Customize" button (top-right area of topbar, ghost button). The `CustomizeBar` slides in below the topbar with instruction text: "Drag to reorder zones Â· Click Ã— to hide Â· Add widgets from the library". Save and Reset to Default buttons appear in the bar (right-aligned). Each rendered zone gains:
  - A drag handle icon `â ¿` in the zone header (cursor: grab)
  - A Ã— remove button in the zone header
  - Dashed zone borders with hover highlight
  Zone 1 (Exception Alert Strip) shows `ðŸ“Œ pinned` badge instead of drag/remove â€” it cannot be moved or hidden
- **API:** N/A (edit mode is purely client-side UI state change)
- **Backend:** N/A
- **Validation:** N/A
- **DB:** None

### Step 2: Widget Library Panel Opens

- **UI:** 240px panel slides in from the right edge (`width: 0` â†’ `240px`, `transition: width 200ms ease-out`). Panel header: "Add Widgets". Panel lists only widgets the user's permissions support â€” no locked/blurred widgets shown. Available widgets shown with icon, name, + button. Already-added widgets shown with checkmark (cannot add twice)
- **API:** N/A (widget list is computed client-side from current backend session permissions)
- **Backend:** N/A
- **Validation:** Permission check using `useAuth() permission metadata` â€” widget only appears in list if user has required permission. `hierarchy_scope` also checked (e.g., "My Team Quick Stats" requires scope â‰  `self`)
- **DB:** None

**Widget Library â€” permission-gated list:**

| Widget | Permission Required | Scope Restriction |
|:-------|:--------------------|:-----------------|
| Top Performers | `workforce:view` + WI module | None |
| Dept Headcount Breakdown | `employees:read` | None |
| Leave Calendar Preview | `leave:read` | None |
| Recent Audit Log | `settings:system` | None |
| Grievance Summary | `grievance:read` | None |
| Contract Renewals (30d) | `employees:read` | None |
| My Team Quick Stats | `employees:read` | `hierarchy_scope` â‰  `self` |

### Step 3: User Reorders Zones

- **UI:** User drags a zone by its `â ¿` handle to a new position. Other zones shift to make room (animated, spring easing via `@dnd-kit/core`). Zone 1 is excluded from the drag context â€” it stays pinned above all other zones regardless of drag operations. Reorder is reflected immediately in the layout (optimistic UI). Change is NOT saved yet â€” only saved on "Save" click
- **API:** N/A (reorder is local state only until Save)
- **Backend:** N/A
- **Validation:** Zone 1 cannot be dragged. Other zones can be promoted or demoted freely â€” including promoting Zone 5 (Charts) above Zone 2 (KPIs)
- **DB:** None

### Step 4: User Hides a Zone

- **UI:** User clicks Ã— on a zone header. Zone animates out (`opacity 0`, `height â†’ 0`, 150ms ease-out). Zone disappears from layout. Zone is added to a hidden zones list (local state). Change is NOT saved yet â€” visible when user clicks Save
- **API:** N/A (local state)
- **Backend:** N/A
- **Validation:** Zone 1 has no Ã— button â€” cannot be hidden
- **DB:** None

### Step 5: User Adds a Widget

- **UI:** User clicks + next to a widget in the Widget Library panel. Widget appears at the bottom of the zone list (after all default zones). Widget's + button changes to a checkmark in the panel. Widget can be repositioned using drag handles (same as zones). Change is NOT saved yet
- **API:** N/A (local state)
- **Backend:** N/A
- **Validation:** Widget already in list cannot be added again (+ button disabled). Widget is permission-gated at render time â€” if permission changes between sessions, widget silently drops from saved prefs on next load
- **DB:** None

### Step 6: User Saves

- **UI:** User clicks "Save" in the CustomizeBar. Loading state on button. On success: edit mode exits, `CustomizeBar` hides, Widget Library panel closes, zones render in their new saved order. Success toast: "Dashboard saved" (auto-dismiss 3s)
- **API:** `PATCH /api/v1/users/me/dashboard-prefs`
  ```json
  {
    "zones": [
      { "id": "exception-alert", "visible": true, "order": 0 },
      { "id": "trends-charts", "visible": true, "order": 1 },
      { "id": "kpi-cards", "visible": true, "order": 2 },
      { "id": "pending-actions", "visible": true, "order": 3 },
      { "id": "workforce-live", "visible": false, "order": 4 },
      { "id": "workforce-events", "visible": true, "order": 5 }
    ],
    "addedWidgets": ["dept-headcount", "leave-calendar-preview"]
  }
  ```
- **Backend:** `UserDashboardPrefsController.PatchPrefs()` â€” upserts `user_dashboard_prefs` row. `updated_at` set to `NOW()`. No merge â€” full replace of `zones_json` and `added_widgets_json`
- **Validation:** `zones` array must only reference valid zone IDs. Zone 1 `visible` field is ignored if `false` (server overrides to `true`). `addedWidgets` IDs validated against the known widget list; unknown IDs silently dropped
- **DB:** `user_dashboard_prefs` (upsert)

### Step 7: Prefs Persist Across Devices

- **UI:** When user logs in on a different device, the same layout and widget order loads. Dashboard shell fetches `GET /api/v1/users/me/dashboard-prefs` on mount â€” preferences are server-side, not localStorage
- **API:** `GET /api/v1/users/me/dashboard-prefs` (called on every dashboard mount)
- **Backend:** Returns saved `DashboardPreference` or `DashboardPreference.Default()` if none
- **Validation:** N/A
- **DB:** `user_dashboard_prefs`

---

## Variations

### Reset to Default
- User clicks "Reset to Default" in CustomizeBar
- Confirmation dialog: "This will restore the default layout. Your customizations will be lost." with Cancel / Reset buttons
- On confirm: `PATCH /api/v1/users/me/dashboard-prefs` with `DashboardPreference.Default()` payload
- Default: all server-enabled zones visible, in spec priority order (1â†’6), no added widgets
- Edit mode exits after reset completes

### Cancel Without Saving
- User clicks outside CustomizeBar area or presses Escape
- Confirmation dialog if any changes were made: "You have unsaved changes. Discard them?"
- On confirm: local state reverts to last saved prefs, edit mode exits
- If no changes were made: edit mode exits immediately with no confirmation

### Permission Revoked Between Sessions
- User had "Top Performers" widget added when they had `workforce:view`
- Permission is revoked by admin
- On next dashboard load: `addedWidgets` contains "top-performers" but permission check fails
- Widget silently dropped from rendered layout (no error shown to user)
- Saved prefs are NOT modified automatically â€” widget reappears if permission is restored

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| PATCH fails (network error) | Prefs not saved; edit mode stays open | Error toast: "Could not save. Check your connection and try again." |
| PATCH fails (server error 5xx) | Same as above | Error toast with same message |
| User adds widget then loses permission before saving | Widget visible in local state during edit mode; dropped on Save validation | Save succeeds, widget silently excluded |
| Zone order PATCH with invalid zone IDs | Server drops unknown IDs; saves rest | Layout may differ slightly from what user set |

---

## Events Triggered

- `DashboardPrefsUpdatedEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]] â€” consumed by audit log (low-priority, audit action: `dashboard.prefs.updated`)

---

## Related Flows

- [[Userflow/Dashboard/dashboard-overview|Dashboard Overview]] â€” the page this customization applies to
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] â€” permissions that gate widget availability

---

## Module References

- [[frontend/cross-cutting/authorization|Authorization]] â€” `useAuth() permission metadata` for widget permission gating
- [[modules/shared-platform/overview|Shared Platform]] â€” `UserDashboardPrefsRepository`, `DashboardPreference.Default()` (no separate Dashboard module; prefs housed in SharedPlatform)
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] â€” drag-and-drop zone reordering via `@dnd-kit/core` sortable context

