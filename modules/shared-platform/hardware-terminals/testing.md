# Hardware Terminals - Testing

**Module:** Shared Platform  
**Feature:** Compatibility Redirect

---

There are no Shared Platform hardware-terminal service tests because Shared Platform does not own a terminal table or terminal write flow.

Test physical terminal registration, HMAC/API-key validation, heartbeat/offline detection, and punch-method normalization under [[modules/identity-verification/biometric-devices/testing|Biometric Devices - Testing]] and Time & Attendance device ingestion tests.

## Related

- [[modules/identity-verification/biometric-devices/testing|Biometric Devices - Testing]]
- [[database/schemas/identity-verification#`biometric_devices`|biometric_devices]]
