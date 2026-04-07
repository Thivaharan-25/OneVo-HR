# Identity Verification Review

**Area:** Workforce Intelligence  
**Required Permission(s):** `verification:view`  
**Related Permissions:** `exceptions:manage` (escalate confirmed mismatches)

---

## Preconditions

- Identity verification enabled and running → [[identity-verification-setup]]
- Failed verifications exist
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: View Flagged Sessions
- **UI:** Workforce → Verification → Flagged Sessions → list of failed verifications sorted by date
- **API:** `GET /api/v1/verification/flags`

### Step 2: Review Each Flag
- **UI:** Click flag → side-by-side view: captured photo vs enrolled profile photo → confidence score (e.g., 62% — below 85% threshold) → timestamp, employee name, device info

### Step 3: Take Action
- **UI:** Three options:
  - **Dismiss as False Positive** — lighting/angle issue → flag cleared → no further action
  - **Confirm Mismatch** — someone else at the desk → escalate to exception engine → [[alert-review]]
  - **Request Re-verification** — ask employee to verify again
- **API:** `PUT /api/v1/verification/flags/{id}`
- **DB:** `verification_flags` — status updated, reviewer recorded

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Photo too dark/blurry | Low confidence | Flag with note "poor image quality" |
| Employee photo outdated | Frequent false positives | "Consider updating enrolled photo" |

## Events Triggered

- `VerificationMismatchConfirmed` → [[event-catalog]]
- Exception alert (if confirmed) → [[exception-engine]]

## Related Flows

- [[identity-verification-setup]]
- [[alert-review]]
- [[profile-management]] (update enrolled photo)

## Module References

- [[identity-verification]]
- [[exception-engine]]
- [[audit-logging]]
