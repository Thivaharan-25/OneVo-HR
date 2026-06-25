# Biometric Devices

**Module:** Identity Verification
**Feature:** Biometric Devices

---

## Purpose

Manages biometric/attendance terminal hardware. Devices can support face, fingerprint, RFID/card, PIN, or combined punch methods. Device webhook/API authentication uses HMAC-SHA256.

## Database Tables

### `biometric_devices`

Fields: `device_code`, `legal_entity_id`, `device_name`, `vendor`, `model`, `connection_method` (`direct_webhook`, `vendor_middleware`, `local_gateway`, `polling_api`, `manual_import`), optional `webhook_url`, optional `vendor_middleware_url`, `external_device_ref`, `supported_auth_methods`, `enabled_auth_methods`, `api_key_encrypted` (HMAC/API key), `status`, `last_heartbeat_at`.

`biometric_devices` is the canonical table for physical attendance/biometric terminals. `legal_entity_id` is the required policy boundary. Phase 1 does not assign terminals to a separate office-location table. Physical terminals and their vendor middleware/local gateways use HMAC/API-key authentication, not WorkPulse Device JWT. Department-level reporting is derived from employees and org structure, not device placement.

### `biometric_audit_logs`

Tamper detection and device health: `event_type` (`heartbeat`, `tamper_detected`, `firmware_update`, `error`), `details_json`.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `BiometricDeviceOffline` | No heartbeat for 5+ min | [[modules/notifications/overview|Notifications]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/time-attendance/devices` | `verification:view` | List devices |
| POST | `/api/v1/time-attendance/devices` | `verification:configure` | Register device |
| PUT | `/api/v1/time-attendance/devices/{id}` | `verification:configure` | Update device |

## Hangfire Jobs

| Job | Schedule | Purpose |
|:----|:---------|:--------|
| `CheckBiometricDeviceHealthJob` | Every 5 min | Flag devices with no heartbeat |

## Related

- [[modules/identity-verification/overview|Identity Verification Module]]
- [[modules/identity-verification/biometric-devices/end-to-end-logic|Biometric Devices - End-to-End Logic]]
- [[modules/identity-verification/biometric-devices/testing|Biometric Devices - Testing]]
- [[frontend/architecture/overview|Biometric Enrollment]]
- [[frontend/architecture/overview|Verification Policies]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
