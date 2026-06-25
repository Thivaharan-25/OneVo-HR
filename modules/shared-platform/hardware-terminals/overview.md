# Hardware Terminals

**Module:** Shared Platform  
**Feature:** Compatibility Redirect

---

## Purpose

Shared Platform does not own a separate hardware-terminal table or terminal-management service. Physical attendance/biometric terminals are stored in [[database/schemas/identity-verification#`biometric_devices`|biometric_devices]] and managed through the Identity Verification / Time & Attendance device flows.

Use `biometric_devices` for:

- Face and fingerprint terminals
- RFID/card readers
- PIN/kiosk devices
- Combined punch devices
- Direct webhook, vendor middleware, local gateway, polling API, and manual import connection modes

## Boundary

Shared Platform may expose navigation, integration catalog metadata, dashboards, or cross-module links for terminal integrations, but it must not duplicate physical terminal rows. The canonical policy boundary is `biometric_devices.legal_entity_id`. Phase 1 does not assign terminals to a separate office-location table. Physical terminals and their vendor middleware/local gateways use HMAC/API-key authentication, not WorkPulse Device JWT.

## Related

- [[database/schemas/identity-verification#`biometric_devices`|biometric_devices]]
- [[modules/identity-verification/biometric-devices/overview|Biometric Devices]]
- [[modules/identity-verification/overview|Identity Verification Module]]
- [[modules/time-attendance/overview|Time & Attendance]]
