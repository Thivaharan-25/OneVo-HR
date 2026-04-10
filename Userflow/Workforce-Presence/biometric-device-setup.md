# Biometric Device Setup

**Area:** Workforce Presence  
**Trigger:** Admin registers biometric device (user action — configuration)
**Required Permission(s):** `attendance:write` + `settings:admin`  
**Related Permissions:** `agent:manage` (device-agent integration)

---

## Preconditions

- Physical biometric device available (fingerprint reader, face recognition camera, NFC card reader)
- Network access configured for device
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Register Device
- **UI:** Workforce → Devices → "Register Device" → enter: device ID, name, location (e.g., "Main Entrance"), type (fingerprint/face/NFC)
- **API:** `POST /api/v1/workforce/devices`
- **DB:** `biometric_devices` — record created

### Step 2: Configure Connection
- **UI:** Enter device webhook URL or API endpoint → set authentication key → test connection → confirm bi-directional communication
- **Backend:** DeviceService.RegisterAsync() → [[modules/workforce-presence/device-sessions/overview|Device Sessions]]

### Step 3: Enroll Employees
- **UI:** Select device → "Enroll Employees" → employees physically scan fingerprint/face at device → enrollment data stored
- **API:** `POST /api/v1/workforce/devices/{id}/enrollments`
- **DB:** `device_enrollments` — employee-device mapping

### Step 4: Activate
- **UI:** Toggle device to "Active" → device starts sending clock-in/out events → events create presence sessions automatically
- **Backend:** Webhook receives events → PresenceService.ProcessClockEvent() → [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Device unreachable | Connection test fails | "Cannot connect to device — check network" |
| Enrollment fails | Biometric capture issue | "Enrollment failed — try again" |
| Unrecognized scan | Event rejected | "Employee not enrolled on this device" |

## Events Triggered

- `DeviceRegistered` → [[backend/messaging/event-catalog|Event Catalog]]
- `EmployeeEnrolled` → [[backend/messaging/event-catalog|Event Catalog]]
- `ClockEventReceived` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]]
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]
- [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]]

## Module References

- [[modules/workforce-presence/device-sessions/overview|Device Sessions]]
- [[modules/workforce-presence/overview|Workforce Presence]]
- [[modules/agent-gateway/overview|Agent Gateway]]
