# Identity Verification Setup

**Area:** Monitoring
**Trigger:** Admin configures photo verification policy
**Required Permission(s):** `verification:configure`
**Related Permissions:** `monitoring:configure`

---

## Preconditions

- Monitoring enabled -> [[Userflow/Monitoring/monitoring-configuration|Monitoring Configuration]]
- Desktop agent deployed -> [[Userflow/Monitoring/agent-deployment|Agent Deployment]]
- Employee Legal & Privacy notice/consent for monitoring and biometric/face reference processing -> [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]]
- Required permissions -> [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Enable Verification

- **UI:** Monitoring -> Identity Verification -> toggle ON
- **API:** `PUT /api/v1/configuration/identity-verification`

### Step 2: Configure Settings

- **UI:** Configure photo at clock-in, photo at clock-out, `photo_capture_context_scope` (`remote_only`, `onsite_only`, `remote_and_onsite`, `disabled`), on-demand camera photo, and absence-detected camera photo -> set confidence threshold for face match (e.g., 85%) -> set action on failure: "Alert Only" or "Lock Session" -> set reference enrollment mode: "Manual Review" or "Trusted SSO Auto-Approve" -> choose whether monitoring waits until reference approval
- **Backend:** VerificationConfigService.UpdateAsync() -> [[modules/identity-verification/overview|Identity Verification]]
- **DB:** `verification_policies`

### Step 3: Assign Scope


### Step 4: Save

- **Result:** When employees sign in to the TrayApp, any employee without an approved reference photo enters First Photo Enrollment. Future verification captures compare against the approved reference photo.

## First TrayApp Reference Enrollment

Identity verification does not require photo capture during HR onboarding. The preferred Phase 1 flow is to collect the trusted reference photo when the employee first installs/opens the TrayApp and signs in.

Flow:

1. Employee signs in to the TrayApp with ONEVO/SSO.
2. Backend resolves tenant, employee, policy, consent, and device.
3. If identity verification is enabled and no approved `verification_reference_photos` row exists, TrayApp starts Reference Enrollment.
4. Employee sees consent/disclosure if needed and captures a reference photo.
5. Backend stores it as `pending_review`.
6. Configured identity-verification resolver approves it, or the system auto-approves only when the tenant explicitly allows trusted SSO/MFA auto-approval.
7. Future clock-in, clock-out, on-demand, and absence-detected verification compares captured photos against this approved reference.

The first captured photo is enrollment, not verification. It must not trigger a failed-verification alert.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No approved reference photo | First TrayApp enrollment starts reference enrollment; verification is skipped until approved | "Reference photo enrollment required" |
| Reference photo pending review | Verification skipped; no failed-verification alert | "Reference photo pending review" |
| Reference photo rejected | Employee prompted to recapture or HR handles manually | "Reference photo rejected - recapture required" |
| Required Legal & Privacy item incomplete | Excluded | Employee auto-excluded from verification |

## Events Triggered

- `VerificationConfigUpdated` -> [[backend/messaging/event-catalog|Event Catalog]]
- `VerificationReferencePhotoSubmitted`
- `VerificationReferencePhotoApproved`
- `VerificationReferencePhotoRejected`

## Related Flows

- [[Userflow/Monitoring/identity-verification-review|Identity Verification Review]]
- [[Userflow/Monitoring/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]]

## Module References

- [[modules/identity-verification/overview|Identity Verification]]
- [[modules/identity-verification/photo-capture|Photo Capture]]
- [[modules/identity-verification/photo-verification/overview|Photo Verification]]
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
