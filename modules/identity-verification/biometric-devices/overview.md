# Biometric Devices

**Module:** Identity Verification  
**Feature:** Biometric Devices

---

## Purpose

Manages fingerprint terminal hardware. API key authenticated via HMAC-SHA256.

## Database Tables

### `biometric_devices`
Fields: `device_name`, `location_id`, `api_key_encrypted` (HMAC-SHA256), `model`, `is_active`, `last_heartbeat_at`.

### `biometric_audit_logs`
Tamper detection and device health: `event_type` (`heartbeat`, `tamper_detected`, `firmware_update`, `error`), `details_json`.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `BiometricDeviceOffline` | No heartbeat for 5+ min | [[notifications]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/biometric/devices` | `verification:view` | List devices |
| POST | `/api/v1/biometric/devices` | `verification:configure` | Register device |
| PUT | `/api/v1/biometric/devices/{id}` | `verification:configure` | Update device |

## Hangfire Jobs

| Job | Schedule | Purpose |
|:----|:---------|:--------|
| `CheckBiometricDeviceHealthJob` | Every 5 min | Flag devices with no heartbeat |

## Related

- [[identity-verification|Identity Verification Module]]
- [[biometric-devices/end-to-end-logic|Biometric Devices — End-to-End Logic]]
- [[biometric-devices/testing|Biometric Devices — Testing]]
- [[biometric-enrollment/overview|Biometric Enrollment]]
- [[verification-policies/overview|Verification Policies]]
- [[data-classification]]
- [[compliance]]
- [[auth-architecture]]
- [[multi-tenancy]]
- [[WEEK3-identity-verification]]
