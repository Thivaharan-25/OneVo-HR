# Desktop Agent Deployment

**Area:** Workforce Intelligence  
**Required Permission(s):** `agent:manage`  
**Related Permissions:** `settings:admin` (download installer), `employees:read` (map agents to employees)

---

## Preconditions

- Monitoring configuration set → [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- Windows machines available for employees
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Download Installer
- **UI:** Workforce → Agent → "Download Installer" → .msi file downloaded with embedded tenant key
- **API:** `GET /api/v1/agent/installer`

### Step 2: Deploy to Machines
- **UI:** IT deploys .msi via Group Policy, SCCM, or manual install on employee Windows machines
- **Backend:** Agent installs as Windows Service + MAUI tray app

### Step 3: Agent Auto-Registration
- **Backend:** On first run: agent sends registration request with machine ID + tenant key → server validates → agent registered
- **API:** `POST /api/v1/agent/register` (agent-to-server)
- **DB:** `agent_registrations` — agent_id, machine_id, employee_id (mapped)

### Step 4: Map Agent to Employee
- **UI:** Agent → Registrations → list of registered agents → map each to employee (auto-matched by logged-in Windows user if possible, manual otherwise)
- **API:** `PUT /api/v1/agent/registrations/{id}/map`

### Step 5: Policy Distribution
- **Backend:** Server sends monitoring policy to agent (what to track, intervals, screenshot settings) → agent starts collecting data
- Links: [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]

### Step 6: Monitor Health
- **UI:** Agent → Health Dashboard → see all agents: online/offline status, last heartbeat, version, data sync status
- **API:** `GET /api/v1/agent/health`
- **Real-time:** Agent heartbeats every 60 seconds → offline detection via SignalR

## Variations

### Agent updates
- New version deployed → agents auto-update on next check-in

### Agent unregistration
- On employee offboarding → agent automatically unregistered → [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Registration key invalid | Agent rejected | "Invalid tenant key — regenerate installer" |
| Agent goes offline | Dashboard shows offline | "Agent offline since [time] — check machine" |
| Duplicate machine ID | Warning | "Agent already registered for this machine" |

## Events Triggered

- `AgentRegistered` → [[backend/messaging/event-catalog|Event Catalog]]
- `AgentOffline` → [[backend/messaging/event-catalog|Event Catalog]]
- `PolicyDistributed` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Workforce-Intelligence/live-dashboard|Live Dashboard]]
- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]]

## Module References

- [[modules/agent-gateway/agent-registration/overview|Agent Registration]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
- [[modules/agent-gateway/heartbeat-monitoring/overview|Heartbeat Monitoring]]
- [[modules/agent-gateway/overview|Agent Gateway]]
