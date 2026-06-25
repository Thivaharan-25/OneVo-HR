# Biometric / Attendance Device Setup

**Area:** Time & Attendance / Monitoring
**Trigger:** Admin registers biometric/attendance device (user action: configuration)
**Required Permission(s):** `attendance:write` + `settings:admin`
**Related Permissions:** `agent:manage` (device-agent integration)

---

## Preconditions

- Physical attendance device available, such as face terminal, fingerprint reader, RFID/card reader, PIN terminal, or combined device
- Network access configured for device
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Register Device

- **UI:** Time & Attendance -> Devices -> "Register Device" -> enter: device code, name, Company/legal entity, vendor, model, connection method (`direct_webhook`, `vendor_middleware`, `local_gateway`, `polling_api`, or `manual_import`), and allowed punch methods (`Face`, `Fingerprint`, `Card`, `PIN`).
- **API:** `POST /api/v1/time-attendance/devices`
- **DB:** `biometric_devices` record created with required `legal_entity_id`, vendor/model, connection metadata, supported auth methods, and enabled auth methods. Billing remains tenant-level.

### Step 2: Configure Connection

- **UI:** Enter direct terminal webhook/API details, vendor middleware URL, local gateway URL, polling API details, or manual import settings -> set HMAC/API key -> test connection -> confirm communication
- **Backend:** TimeAttendanceDeviceService.RegisterAsync() -> [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]

### Step 3: Enroll Employees

- **UI:** Select device -> "Enroll Employees" -> employees physically enroll the configured biometric factor, such as fingerprint or face, at the device -> enrollment data stored
- **API:** `POST /api/v1/time-attendance/devices/{id}/enrollments`
- **DB:** `device_enrollments`: employee-device mapping

### Step 4: Activate

- **UI:** Toggle device to "Active" -> device starts sending clock-in/out events -> events create presence sessions automatically
- **Backend:** Webhook receives events -> PresenceService.ProcessClockEvent() -> [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]

## Biometric Outage Fallback

If a registered biometric device or Company has a verified attendance-device outage, an admin can enable a time-limited fallback:

- **API:** `POST /api/v1/time-attendance/biometric-outages`
- **Scope:** legal entity or device
- **Allowed fallback:** onsite employees may clock in/out through approved web or tray flow while the outage is active
- **Audit:** every fallback clock event records source, outage id, employee, timestamp, reason, and reviewer status
- **Restriction:** IDE extension and Work Management time logging cannot use this fallback to create presence records

When the outage is resolved, admins call `PUT /api/v1/time-attendance/biometric-outages/{id}/resolve`, and onsite employees return to the configured attendance-device clock-in method for their legal entity.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Device unreachable | Connection test fails | "Cannot connect to device; check network" |
| Enrollment fails | Biometric capture or device issue | "Enrollment failed; try again" |
| Unrecognized punch/scan | Event rejected | "Employee not enrolled on this device" |

## Events Triggered

- `DeviceRegistered` -> [[backend/messaging/event-catalog|Event Catalog]]
- `EmployeeEnrolled` -> [[backend/messaging/event-catalog|Event Catalog]]
- `ClockEventReceived` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Time-Attendance/presence-session-view|Presence Session View]]
- [[Userflow/Time-Attendance/shift-schedule-setup|Shift Schedule Setup]]
- [[Userflow/Monitoring/agent-deployment|Agent Deployment]]

## Module References

- [[modules/time-attendance/device-sessions/overview|Device Sessions]]
- [[modules/time-attendance/overview|Time & Attendance]]
- [[modules/agent-gateway/overview|Agent Gateway]]

