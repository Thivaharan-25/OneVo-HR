# Identity Verification Setup

**Area:** Workforce Intelligence
**Trigger:** Admin configures photo verification policy
**Required Permission(s):** `verification:configure`
**Related Permissions:** `monitoring:configure`

---

## Preconditions

- Monitoring enabled -> [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- Desktop agent deployed -> [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]]
- Employee Legal & Privacy notice/consent for monitoring and biometric/face reference processing -> [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]]
- Required permissions -> [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Enable Verification

- **UI:** Settings -> Monitoring -> Identity Verification -> toggle ON
- **API:** `PUT /api/v1/configuration/identity-verification`

### Step 2: Configure Settings

- **UI:** Set capture interval (every 15/30/60 min) -> set confidence threshold for face match (e.g., 85%) -> set action on failure: "Alert Only" or "Lock Session" -> set reference enrollment mode: "Manual Review" or "Trusted SSO Auto-Approve" -> choose whether monitoring waits until reference approval
- **Backend:** VerificationConfigService.UpdateAsync() -> [[modules/identity-verification/overview|Identity Verification]]
- **DB:** `verification_policies`

### Step 3: Assign Scope

- **UI:** Apply to all employees, specific roles/departments/teams, or individual employees. Employees without required WorkPulse photo/biometric notice or consent are automatically excluded until completed in the desktop app.

### Step 4: Save

- **Result:** When employees sign in to the TrayApp, any employee without an approved reference photo enters First Photo Enrollment. Future verification captures compare against the approved reference photo.

## First Agent Sign-In Reference Enrollment

Identity verification does not require photo capture during HR onboarding. The preferred Phase 1 flow is to collect the trusted reference photo when the employee first installs/opens the TrayApp and signs in.

Flow:

1. Employee signs in to the TrayApp with ONEVO/SSO.
2. Backend resolves tenant, employee, policy, consent, and device.
3. If identity verification is enabled and no approved `verification_reference_photos` row exists, TrayApp starts Reference Enrollment.
4. Employee sees consent/disclosure if needed and captures a reference photo.
5. Backend stores it as `pending_review`.
6. Configured identity-verification resolver approves it, or the system auto-approves only when the tenant explicitly allows trusted SSO/MFA auto-approval.
7. Future login/logout/interval verification compares captured photos against this approved reference.

The first captured photo is enrollment, not verification. It must not trigger a failed-verification alert.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No approved reference photo | First agent sign-in starts reference enrollment; verification is skipped until approved | "Reference photo enrollment required" |
| Reference photo pending review | Verification skipped; no failed-verification alert | "Reference photo pending review" |
| Reference photo rejected | Employee prompted to recapture or HR handles manually | "Reference photo rejected - recapture required" |
| Required Legal & Privacy item incomplete | Excluded | Employee auto-excluded from verification |

## Events Triggered

- `VerificationConfigUpdated` -> [[backend/messaging/event-catalog|Event Catalog]]
- `VerificationReferencePhotoSubmitted`
- `VerificationReferencePhotoApproved`
- `VerificationReferencePhotoRejected`

## Related Flows

- [[Userflow/Workforce-Intelligence/identity-verification-review|Identity Verification Review]]
- [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]]

## Module References

- [[modules/identity-verification/overview|Identity Verification]]
- [[modules/identity-verification/photo-capture|Photo Capture]]
- [[modules/identity-verification/photo-verification/overview|Photo Verification]]
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
