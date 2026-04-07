# Biometric Devices — End-to-End Logic

**Module:** Identity Verification
**Feature:** Biometric Device Management

---

## Register Biometric Device

### Flow

```
POST /api/v1/biometric/devices
  -> BiometricDeviceController.Register(RegisterDeviceCommand)
    -> [RequirePermission("verification:configure")]
    -> BiometricDeviceService.RegisterAsync(command, ct)
      -> 1. Validate: device_name, model, location_id
      -> 2. Generate API key for device
         -> Encrypt via IEncryptionService -> store api_key_encrypted
      -> 3. INSERT into biometric_devices
         -> status = 'active', last_heartbeat_at = now
      -> Return Result.Success(deviceDto with plaintext API key — shown once only)
```

## Receive Biometric Events (Webhook)

### Flow

```
POST /api/v1/biometric/webhook
  -> BiometricWebhookController.ReceiveEvent(payload, signature)
    -> Auth: HMAC-SHA256 signature verification (not JWT)
    -> BiometricEventService.ProcessEventAsync(payload, ct)
      -> 1. Verify HMAC signature against device api_key
      -> 2. Validate employee fingerprint match (verified = true/false)
      -> 3. INSERT into biometric_events
         -> event_type: clock_in, clock_out, break_start, break_end
      -> 4. Route to workforce-presence for session reconciliation
      -> Return 200 OK
```

### Key Rules

- **Webhook auth uses HMAC-SHA256**, not JWT. Each device has its own API key.
- **Device heartbeat checked** by `CheckBiometricDeviceHealthJob` every 5 min.

## Related

- [[identity-verification|Identity Verification Module]]
- [[biometric-devices/overview|Biometric Devices Overview]]
- [[biometric-enrollment/end-to-end-logic|Biometric Enrollment — End-to-End Logic]]
- [[verification-policies/end-to-end-logic|Verification Policies — End-to-End Logic]]
- [[event-catalog]]
- [[error-handling]]
- [[auth-architecture]]
- [[multi-tenancy]]
- [[WEEK3-identity-verification]]
