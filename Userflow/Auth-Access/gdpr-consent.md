# Legal & Privacy Acceptance

**Area:** Auth & Access  
**Trigger:** First invitation acceptance, first login for existing users, legal document version change, or tenant monitoring policy change
**Required Permission(s):** Any authenticated or invitation-token user
**Related Permissions:** `monitoring:configure` controls which monitoring features can be enabled, but admin policy does not replace employee notice/consent.

---

## Purpose

This flow separates:

- Terms & Conditions acceptance
- Privacy Notice acknowledgement
- Employee monitoring/screenshot notices
- Biometric/photo verification consent
- Optional marketing consent

The UI may present these on one **Legal & Privacy** page, but the backend must store each accepted/acknowledged item separately by document type and version.

## Preconditions

- The tenant exists and has enabled modules/policies resolved for the user.
- Active legal/privacy document versions exist for the tenant/country/module combination.
- For invitation acceptance, the invitation token is valid and identifies the tenant/user.
- For existing users, the user has an authenticated session.

## Legal Item Types

| Item | User action | Required | When shown |
|:-----|:------------|:---------|:----------|
| Terms & Conditions | Accept | Yes | First account creation; again when terms version changes |
| Privacy Notice | Acknowledge | Yes | First account creation; again when privacy version changes |
| Activity monitoring notice | Acknowledge | Conditional | WorkPulse desktop app sign-in, only if enabled for this tenant/user |
| Screenshot capture notice | Acknowledge | Conditional | WorkPulse desktop app sign-in, only if enabled for this tenant/user |
| Photo/biometric verification | Consent or explicit acknowledgement, per legal decision | Conditional | WorkPulse desktop app sign-in, only if enabled for this tenant/user |
| Marketing communication | Consent | No | User-level optional preference |

Essential account and HR data processing is explained inside the Privacy Notice. Do not present it as a separate employee consent checkbox because the employee cannot realistically use ONEVO without that processing.

Do not collapse these into one database flag. A single page is acceptable; a single acceptance record is not.

## Flow A: First Invitation Acceptance

### Step 1: Invitation Preview Resolves Pending Legal Items
- **UI:** Accept-invite page loads tenant, invited email, allowed acceptance methods, and current web Legal & Privacy requirements.
- **API:** `GET /api/v1/auth/invitations/{token}`
- **Backend:** Invitation preview resolves pending web legal items using tenant, country, and invited user context.
- **DB:** `invitation_tokens`, `users`, legal document/version tables.

### Step 2: User Creates Account
- **UI:** Password or Google acceptance is shown with an inline Legal & Privacy section.

Example UI:

```text
Create your ONEVO account

Password
Confirm password

Legal & Privacy
[ ] I agree to the Terms & Conditions.
[ ] I acknowledge the Privacy Notice.

[Create account]
```

Do not show WorkPulse desktop monitoring, screenshot, or photo/biometric items in the web invite flow. Those are shown inside the WorkPulse desktop application after the employee signs in and before affected collection starts.

### Step 3: Submit Account Setup And Legal Decisions
- **API:** `POST /api/v1/auth/invitations/{token}/accept-password` or `POST /api/v1/auth/invitations/{token}/accept-google`
- **Backend:** Validates platform-required web Legal & Privacy decisions before activating the account or allowing dashboard access. Collection-required WorkPulse items are validated by the desktop app flow before affected collection starts.
- **DB:** Account activation updates auth tables; legal decisions are recorded as separate versioned acceptance records.

## Flow B: Existing User Or Later Change

### Step 1: Login Completes Authentication
- **UI:** Login page does not block the sign-in button with legal checkboxes. It only shows footer links to Terms and Privacy.
- **API:** `POST /api/v1/auth/login` or SSO callback.
- **Backend:** Creates/refreshes the session, then checks pending Legal & Privacy items before dashboard access.

### Step 2: Dynamic Legal & Privacy Notice
- **UI:** If platform-required items are missing or changed, route to a blocking Legal & Privacy screen before dashboard. If only collection-required monitoring/screenshot/biometric items are pending, the dashboard may load, but the affected collection category remains disabled until the user completes the item.
- **API:** `GET /api/v1/legal/pending`
- **Backend:** Returns only items pending for this user.

Example when Terms changed:

```text
Legal & Privacy Update

ONEVO Terms & Conditions were updated.

[ ] I agree to the updated Terms & Conditions.

[Continue]
```

If only WorkPulse collection items are pending, the web app should show an install/setup task or status banner, not the desktop collection checkboxes:

```text
WorkPulse setup required

Install and sign into the desktop app to complete monitoring setup.
```

### Step 3: Record Decisions
- **API:** `POST /api/v1/legal/acceptances`
- **Backend:** Records each item/version separately and returns whether dashboard access or agent collection is now allowed.
- **Validation:** Required items must be accepted/acknowledged. Optional marketing consent can be declined.

## Flow C: WorkPulse Agent Gate

### Step 1: Agent Fetches Policy
- **UI:** WorkPulse TrayApp starts after desktop sign-in.
- **API:** Agent Gateway policy fetch.
- **Backend:** Resolves tenant policy + employee overrides + legal/consent status.

### Step 2: Show Desktop Collection Notice
- **UI:** If required desktop collection items are missing, WorkPulse shows the enabled collection notice before starting collection.

```text
Your company has enabled WorkPulse for this device.

[ ] I acknowledge that activity monitoring is enabled.
[ ] I acknowledge that screenshots may be captured.
[ ] I consent to photo/biometric verification.
```

Only show the items enabled for this tenant/user.

### Step 3: Block Missing Categories
- If activity monitoring notice is missing, the agent does not collect activity data.
- If screenshot notice is missing, the agent does not capture screenshots.
- If biometric/photo consent is missing, the agent does not capture photo/biometric data.
- The agent records completed desktop decisions through the backend with `source = desktop-agent`.

## Acceptance Record Requirements

Each decision stores:

```text
tenant_id
user_id
document_type
document_version
decision: accepted | acknowledged | declined
required
decided_at
ip_address
user_agent
source: invite | web | desktop-agent
```

## Consequences

- Missing Terms acceptance blocks platform access.
- Missing Privacy Notice acknowledgement blocks platform access.
- Missing monitoring/screenshot acknowledgement blocks the affected desktop collection category for that employee.
- Missing or declined biometric/photo consent blocks biometric/photo verification for that employee unless an alternate verification path is configured.
- Marketing consent is optional and must not block product access.

## Variations

### Legal document version changed
- Show only changed documents on next login.
- Previous decisions for unchanged versions remain valid.

### Company enabled a new monitoring feature
- Affected users are marked pending for the new WorkPulse notice/consent item.
- Existing dashboard access may continue, but affected agent collection must stay disabled until the user completes the new item inside WorkPulse.

### User withdraws optional consent later
- User navigates to Settings -> Privacy & Consent.
- Optional consent can be withdrawn.
- Processing stops for that category; existing data follows retention/legal hold policy.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Required Terms or Privacy item not accepted | Account activation or dashboard access is blocked | "This item is required to use ONEVO." |
| Required WorkPulse collection item not completed | Dashboard may load, but the affected desktop collection or verification category is blocked | WorkPulse shows the required notice/consent before that category starts. |
| Monitoring notice incomplete | Dashboard may load, but affected desktop collection is blocked | WorkPulse: "Monitoring notice must be acknowledged before collection starts." |
| Biometric consent declined | Biometric/photo verification is skipped or alternate verification is required | "Photo/biometric verification is not enabled for your account." |
| Legal service unavailable | Login succeeds but dashboard/agent collection waits if required items cannot be verified | "Legal & Privacy status could not be verified. Please try again." |

## Events Triggered

- `LegalAcceptanceRecorded`
- `LegalAcceptanceDeclined`
- `ConsentWithdrawn`
- `EmployeeCollectionGateChanged`

## Related Flows

- [[Userflow/Auth-Access/login-flow|Login Flow]]
- [[Userflow/Auth-Access/user-invitation|User Invitation]]
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- [[Userflow/Configuration/employee-override|Employee Override]]
- [[Userflow/Configuration/retention-policy-setup|Retention Policy Setup]]

## Module References

- [[security/compliance|Compliance]]
- [[security/data-classification|Data Classification]]
- [[modules/configuration/overview|Configuration]]
- [[modules/configuration/employee-overrides/overview|Employee Overrides]]
- [[modules/identity-verification/overview|Identity Verification]]
