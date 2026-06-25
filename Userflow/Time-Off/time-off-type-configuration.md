# Time Off Type Configuration

**Area:** Time Off
**Trigger:** Authorized management user creates or edits a time off type (configuration)
**Required Permission(s):** `time_off:manage`

---

## Purpose

Time Off Types define what kinds of time off exist for the tenant, such as Annual Time Off, Sick Time Off, Maternity Time Off, Compassionate Time Off, or Unpaid Time Off.

Time Off Type is not where entitlement, carry-forward, approval, notice-period, document, or assignment rules are configured. Those belong to [[Userflow/Time-Off/time-off-policy-setup|Time Off Policy Setup]].

## Preconditions

- Tenant has been provisioned and is active.
- User has `time_off:manage`.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Open Time Off Types
- **UI:** Authorized user opens the Time Off management area and selects **Time Off Types**.
- **API:** `GET /api/v1/time-off/types`
- **Backend:** `TimeOffTypeService.GetAllAsync()` -> [[modules/time-off/overview|Time Off]]
- **DB:** `time_off_types` filtered by tenant.

Avoid obsolete navigation wording that implies a separate old shell. Describe the active Time Off management screen ownership instead.

### Step 2: Create Time Off Type
- **UI:** Click "Create Time Off Type".
- **Fields:**
  - Name
  - Code, auto-generated and editable before save
  - Description
  - Paid or unpaid classification, if supported as a type-level classification
  - Whether supporting document is required
  - Active status

Time Off types do not control full-day, half-day, or hourly request modes in Phase 1. Phase 1 Time Off requests are duration-based — every request stores `request_duration_minutes`. If full-day or half-day UI shortcuts are added later, they are UI-only helpers and must convert to explicit minutes before saving.
- **API:** `POST /api/v1/time-off/types`
- **Backend:** `TimeOffTypeService.CreateAsync()`
- **DB:** `time_off_types`, `audit_logs`

Do not add a separate `category` field when it duplicates the time off type itself. Do not add approval, carry-forward, document threshold, notice-period, max-consecutive, or entitlement fields here.

### Step 3: Edit or Deactivate Time Off Type
- **UI:** Open an existing time off type -> Edit or deactivate.
- **API:** `PUT /api/v1/time-off/types/{timeOffTypeId}` or status update endpoint as implemented.
- **Rules:** Code is normally immutable after creation. Deactivated types remain visible for historical requests and balances but are not available for new requests.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate time off type code | `409 Conflict` | "A time off type with this code already exists" |
| Duplicate time off type name | `409 Conflict` | "A time off type with this name already exists" |
| Missing required permission | `403 Forbidden` | "You do not have permission to manage time off types" |

## Events Triggered

- `TimeOffTypeCreatedEvent` -> [[backend/messaging/event-catalog|Event Catalog]]
- `TimeOffTypeUpdatedEvent` -> [[backend/messaging/event-catalog|Event Catalog]]
- `AuditLogEntry` (action: `time_off_type.created`) -> audit logging

## Related Flows

- [[Userflow/Time-Off/time-off-policy-setup|Time Off Policy Setup]] - rules and assignment scope for time off types
- [[Userflow/Time-Off/time-off-entitlement-assignment|Time Off Entitlement Assignment]] - employee-level output from policies
- [[Userflow/Time-Off/time-off-request-submission|Time Off Request Submission]] - employees request configured time off types

## Module References

- [[modules/time-off/overview|Time Off]]
- [[modules/time-off/time-off-types/overview|Time Off Types]]
