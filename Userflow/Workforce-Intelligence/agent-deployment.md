# Desktop Agent Deployment

**Area:** Workforce Intelligence  
**Trigger:** Admin deploys the Windows agent package, employee signs in through TrayApp  
**Required Permission(s):** `agent:manage`  
**Related Permissions:** `settings:admin` (download package), `employees:read` (view linked agents)

---

## Preconditions

- Monitoring configuration set -> [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- Windows 10/11 machines available for employees
- WorkPulse Agent MSIX package is signed and available
- Required permissions configured -> [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Source of Truth

Phase 1 Windows deployment uses a generic signed MSIX package. The installer does not embed a tenant key. Employees do not enter an API key, tenant key, tenant ID, or server URL.

Tenant and employee identity are resolved after the user signs in through the TrayApp. The backend then enrolls the device, creates/updates `registered_agents`, creates an active `agent_sessions` row, and returns an internal device credential for the Service to store securely.

## Flow Steps

### Step 1: Download MSIX Package
- **UI:** Workforce -> Agent -> "Download Windows Agent" -> `.msixbundle` downloaded
- **API:** `GET /api/v1/agent/installer`
- **Backend:** Returns the signed generic WorkPulse Agent package and hash/signature metadata

### Step 2: Deploy to Machines
- **UI:** IT deploys the `.msixbundle` via Intune, Group Policy, SCCM, or manual admin install
- **Backend:** No tenant key is required during install
- **Device:** Package installs Windows Service + MAUI TrayApp

### Step 3: Employee Signs In
- **UI:** TrayApp shows "Sign in"
- **Device:** TrayApp opens system browser or secure embedded auth flow
- **API:** `POST /api/v1/agent/enroll/start`
- **Backend:** Creates short-lived enrollment challenge

### Step 4: Device Enrollment
- **Backend:** After successful auth, resolves tenant and employee from the login session
- **API:** `POST /api/v1/agent/enroll/complete`
- **DB:** `registered_agents` created/updated; previous active `agent_sessions` for the device ended; new active `agent_sessions` row created
- **Device:** Stores internal device credential with DPAPI / Windows Credential Manager

### Step 5: Policy Distribution
- **API:** `GET /api/v1/agent/policy`
- **Backend:** Sends effective monitoring policy from tenant toggles + role policies + employee overrides
- **Device:** If required WorkPulse notices/consents are missing, shows the desktop collection notice before any affected collection starts. Shows "Monitoring active" only when policy, required Legal & Privacy notice/consent, and Workforce Presence lifecycle allow collection
- Links: [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]

Desktop notice example:

```text
Your company has enabled WorkPulse for this device.

[ ] I acknowledge that activity monitoring is enabled.
[ ] I acknowledge that screenshots may be captured.
[ ] I consent to photo/biometric verification.
```

Only show the items enabled for this tenant/user. Store decisions centrally with `source = desktop-agent`.

### Step 6: Monitor Health
- **UI:** Agent -> Health Dashboard -> see all agents: online/offline status, last heartbeat, version, data sync status
- **API:** `POST /api/v1/agent/heartbeat`; `GET /api/v1/agents`
- **Real-time:** Agent heartbeats every 60 seconds; offline detection updates the dashboard via SignalR

## Variations

### IDE Extension Bootstrapper
- IDE extension may prompt entitled users to set up the monitoring agent.
- The extension only downloads/runs the signed installer after explicit user consent and backend entitlement check.
- Enrollment still happens through the same TrayApp login-based flow. The IDE extension does not own registration, policy, health, or telemetry.

### Agent Updates
- New version deployed -> agents auto-update on next check-in or assigned deployment ring.

### Agent Unregistration
- On employee offboarding -> agent session is ended and registration can be revoked -> [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Sign-in fails | Enrollment does not complete | "Sign in failed. Please try again." |
| Device credential revoked | Agent stops syncing and returns to sign-in/enrollment | "Device access revoked. Sign in again or contact admin." |
| Required Legal & Privacy item missing | Ingest rejected for affected category, collector pauses | "Monitoring paused - consent required." |
| Policy blocks collection | Agent remains enrolled but does not collect | "Monitoring paused by policy." |
| Agent goes offline | Dashboard shows offline | "Agent offline since [time] - check machine." |
| Duplicate device ID | Existing registration is updated or admin warning shown | "Device already registered." |

## Events Triggered

- `AgentRegistered` -> [[backend/messaging/event-catalog|Event Catalog]]
- `AgentSessionStarted` -> [[backend/messaging/event-catalog|Event Catalog]]
- `AgentOffline` -> [[backend/messaging/event-catalog|Event Catalog]]
- `PolicyDistributed` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Workforce-Intelligence/live-dashboard|Live Dashboard]]
- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]]
- [[Userflow/IDE-Extension/agent-install-flow|IDE Agent Install]]

## Module References

- [[modules/agent-gateway/agent-registration/overview|Agent Registration]]
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]]
- [[modules/agent-gateway/tray-app-ui|Tray App UI]]
- [[modules/agent-gateway/agent-installer|Agent Installer]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
- [[modules/agent-gateway/heartbeat-monitoring/overview|Heartbeat Monitoring]]
- [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]]
- [[modules/agent-gateway/overview|Agent Gateway]]
