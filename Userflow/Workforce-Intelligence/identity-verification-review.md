# Identity Verification Review

**Area:** Workforce Intelligence  
**Required Permission(s):** `verification:view`  
**Related Permissions:** `exceptions:manage` (escalate confirmed mismatches)

---

## Preconditions

- Identity verification enabled and running → [[Userflow/Workforce-Intelligence/identity-verification-setup|Identity Verification Setup]]
- Failed verifications exist
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: View Flagged Sessions
- **UI:** Workforce → Verification → Flagged Sessions → list of failed verifications sorted by date
- **API:** `GET /api/v1/verification/flags`

### Step 2: Review Each Flag
- **UI:** Click flag → side-by-side view: captured photo vs enrolled profile photo → confidence score (e.g., 62% — below 85% threshold) → timestamp, employee name, device info

### Step 3: Take Action
- **UI:** Three options:
  - **Dismiss as False Positive** — lighting/angle issue → flag cleared → no further action
  - **Confirm Mismatch** — someone else at the desk → escalate to exception engine → [[Userflow/Exception-Engine/alert-review|Alert Review]]
  - **Request Re-verification** — ask employee to verify again
- **API:** `PUT /api/v1/verification/flags/{id}`
- **DB:** `verification_flags` — status updated, reviewer recorded

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Photo too dark/blurry | Low confidence | Flag with note "poor image quality" |
| Employee photo outdated | Frequent false positives | "Consider updating enrolled photo" |

## Events Triggered

- `VerificationMismatchConfirmed` → [[backend/messaging/event-catalog|Event Catalog]]
- Exception alert (if confirmed) → [[modules/exception-engine/overview|Exception Engine]]

## Related Flows

- [[Userflow/Workforce-Intelligence/identity-verification-setup|Identity Verification Setup]]
- [[Userflow/Exception-Engine/alert-review|Alert Review]]
- [[Userflow/Employee-Management/profile-management|Profile Management]] (update enrolled photo)

## Module References

- [[modules/identity-verification/overview|Identity Verification]]
- [[modules/exception-engine/overview|Exception Engine]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
