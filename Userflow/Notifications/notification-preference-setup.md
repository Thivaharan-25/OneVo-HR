# Notification Preference Setup

**Area:** Notifications  
**Trigger:** User configures notification channels (user action — self-service)
**Required Permission(s):** `notifications:read` (own preferences)  
**Related Permissions:** `notifications:manage` (org-wide defaults)

---

## Preconditions

- User has an active account
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Preferences
- **UI:** Settings (user menu) → Notifications
- **API:** `GET /api/v1/notifications/preferences`

### Step 2: Configure per Category
- **UI:** List of notification categories:
  - **Leave:** requests, approvals, balance alerts
  - **Performance:** review deadlines, feedback requests
  - **Attendance:** late alerts, correction requests
  - **Exceptions:** anomaly alerts (severity-based)
  - **Documents:** new docs, acknowledgement requests
  - **Payroll:** payslip available, payroll run
  - **General:** announcements, recognitions
- For each: toggle channels → In-App (always on), Email (on/off), Push (on/off)
- **Backend:** NotificationPreferenceService.UpdateAsync() → Notification Preferences
- **DB:** `notification_preferences`

### Step 3: Set Quiet Hours
- **UI:** Set do-not-disturb period (e.g., 20:00-08:00) → no push/email during quiet hours (in-app still stored)

### Step 4: Set Digest Mode
- **UI:** For non-urgent notifications: Immediate or Daily Digest (batched summary email)

### Step 5: Save
- **Result:** Future notifications follow preferences → critical/system notifications always delivered regardless

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Disable all channels | Warning | "You'll still receive critical system notifications" |

## Events Triggered

- `NotificationPreferencesUpdated` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Notifications/notification-view|Notification View]]
- [[Userflow/Auth-Access/login-flow|Login Flow]]

## Module References

- Notification Preferences
- [[modules/notifications/notification-channels/overview|Notification Channels]]
- [[modules/notifications/overview|Notifications]]
