# Identity Verification Review

**Area:** Monitoring  
**Trigger:** System flags verification failure for review (system-triggered - anomaly detection)
**Required Permission(s):** `verification:view`  
**Related Permissions:** `monitoring:alerts:resolve` (resolve confirmed mismatches in Phase 1); `exceptions:manage` is Phase 2

---

## Preconditions

- Identity verification enabled and running -> [[Userflow/Monitoring/identity-verification-setup|Identity Verification Setup]]
- Failed verifications exist
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: View Flagged Sessions
- **UI:** Monitoring -> Verification -> Flagged Sessions -> list of failed verifications sorted by date
- **API:** `GET /api/v1/verification/records?status=failed,expired&review_status=pending`

### Step 2: Review Each Flag
- **UI:** Click flag -> side-by-side view: captured photo vs enrolled profile photo -> confidence score (e.g., 62% - below 85% threshold) -> timestamp, employee name, device info

### Step 3: Take Action
- **UI:** Three options:
  - **Dismiss as False Positive** - lighting/angle issue -> update `verification_records.review_status = dismissed_false_positive`, set `reviewed_by_id` and `reviewed_at` -> no further action
  - **Confirm Mismatch** - reviewer confirms someone else may be using the device/session. Phase 1: update `verification_records.review_status = confirmed_mismatch`, set `reviewed_by_id` and `reviewed_at`, keep/create the lightweight verification alert, and route follow-up through Notifications/Inbox to the recipient resolved by Monitoring Policy. Phase 2: may route confirmed mismatch into Exception Engine configurable rules.
  - **Request Re-verification** - ask employee to verify again
- **API:** `PUT /api/v1/verification/records/{id}/review`
- **DB:** `verification_records` — update `review_status`, `reviewed_by_id`, `reviewed_at`, and keep evidence linked through `verification_evidence_assets`

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Photo too dark/blurry | Low confidence | Flag with note "poor image quality" |
| Employee photo outdated | Frequent false positives | "Consider updating enrolled photo" |

## Events Triggered

- `VerificationMismatchConfirmed` -> [[backend/messaging/event-catalog|Event Catalog]]
- Phase 1: lightweight verification alert, recipient resolved by Monitoring Policy, via [[modules/notifications/overview|Notifications]]
- Phase 2: may route confirmed mismatch through [[modules/exception-engine/overview|Exception Engine]] configurable rules

## Related Flows

- [[Userflow/Monitoring/identity-verification-setup|Identity Verification Setup]]
- [[Userflow/Exception-Engine/alert-review|Alert Review]] (Phase 2)
- [[Userflow/Employee-Management/profile-management|Profile Management]] (update enrolled photo)

## Module References

- [[modules/identity-verification/overview|Identity Verification]]
- [[modules/notifications/overview|Notifications]] (Phase 1 alert delivery)
- [[modules/exception-engine/overview|Exception Engine]] (Phase 2)
- [[modules/auth/audit-logging/overview|Audit Logging]]
