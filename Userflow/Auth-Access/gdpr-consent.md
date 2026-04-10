# GDPR Consent Collection

**Area:** Auth & Access  
**Trigger:** System presents consent prompt on first login or policy change (system-triggered — reaction)
**Required Permission(s):** Any authenticated user  
**Related Permissions:** `monitoring:configure` (determines which consent categories appear)

---

## Preconditions

- User has an active account
- Consent policy configured by admin → [[security/compliance|Compliance]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Consent Dialog Triggered
- **UI:** On first login or when policy is updated → modal dialog appears (cannot be dismissed without action)
- **API:** `GET /api/v1/consent/pending`
- **Backend:** ConsentService.GetPendingConsentsAsync() → [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- **DB:** `consent_records` — checks for missing or outdated consents

### Step 2: Review Consent Categories
- **UI:** User sees consent categories with descriptions:
  - **Essential Data Processing** — required, cannot opt out
  - **HR Data Processing** — payroll, leave, performance data
  - **Activity Monitoring** — app usage, screenshots, idle tracking (if monitoring enabled)
  - **Biometric Data** — face recognition for identity verification
- Each category shows: purpose, data collected, retention period, third-party sharing

### Step 3: Accept/Decline Each Category
- **UI:** Toggle accept/decline per category → mandatory categories pre-checked
- **API:** `POST /api/v1/consent`
- **Backend:** ConsentService.RecordConsentAsync() → [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- **Validation:** Essential categories must be accepted, optional categories can be declined
- **DB:** `consent_records` — consent recorded with timestamp, IP, version

### Step 4: Consequences of Declining
- If monitoring consent declined → activity tracking disabled for this employee → [[modules/configuration/employee-overrides/overview|Employee Overrides]]
- If biometric consent declined → identity verification skipped → [[modules/identity-verification/overview|Identity Verification]]
- All other features remain accessible

## Variations

### When policy is updated
- All users see consent dialog again on next login with only changed categories highlighted
- Previous consents for unchanged categories carry forward

### When user withdraws consent later
- Navigate to Settings → Privacy → Withdraw Consent → select category → confirm → data processing stops → existing data subject to retention policy

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Essential consent declined | Cannot proceed | "This consent is required to use the platform" |
| Consent service unavailable | Deferred | "We'll ask for your consent on next login" |

## Events Triggered

- `ConsentRecorded` → [[backend/messaging/event-catalog|Event Catalog]]
- `ConsentWithdrawn` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Auth-Access/login-flow|Login Flow]]
- [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Configuration/retention-policy-setup|Retention Policy Setup]]

## Module References

- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- [[security/compliance|Compliance]]
- [[security/data-classification|Data Classification]]
- [[modules/configuration/employee-overrides/overview|Employee Overrides]]
