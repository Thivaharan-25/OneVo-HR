# Biometric Devices - End-to-End Logic

**Module:** Identity Verification
**Feature:** Biometric Device Management

---

## Register Attendance/Biometric Device

### Flow

```
POST /api/v1/time-attendance/devices
  -> BiometricDeviceController.Register(RegisterDeviceCommand)
    -> [RequirePermission("verification:configure")]
    -> BiometricDeviceService.RegisterAsync(command, ct)
      -> 1. Validate: device_code, device_name, legal_entity_id, vendor/model, connection_method, supported_auth_methods, enabled_auth_methods
         -> legal_entity_id is the policy boundary; Phase 1 has no separate office-location table assignment
         -> connection_method is direct_webhook, vendor_middleware, local_gateway, polling_api, or manual_import
      -> 2. Generate API key for device
         -> Encrypt via IEncryptionService -> store api_key_encrypted
      -> 3. INSERT into biometric_devices
         -> status = 'active', last_heartbeat_at = now
      -> Return Result.Success(deviceDto with plaintext API key - shown once only)
```

## Receive Attendance/Biometric Events (Webhook)

### Flow

```
POST /api/v1/time-attendance/biometric/webhook
  -> BiometricWebhookController.ReceiveEvent(payload, signature)
    -> Auth: HMAC-SHA256 signature verification (not JWT)
    -> BiometricEventService.ProcessEventAsync(payload, ct)
      -> 1. Verify HMAC signature against device api_key
      -> 2. Normalize auth_method (face, fingerprint, rfid_card, pin, combined method, or manual)
      -> 3. Validate biometric modality only when the auth_method includes a biometric factor
      -> 4. INSERT into biometric_events
         -> biometric_device_id = resolved device
         -> event_type: clock_in, clock_out, break_start, break_end
      -> 5. Route to time-attendance for session reconciliation
      -> Return 200 OK
```

### Key Rules

- **Webhook auth uses HMAC-SHA256**, not JWT. Each device has its own API key.
- **Device heartbeat checked** by `CheckBiometricDeviceHealthJob` every 5 min.
- **Card/PIN are attendance credentials, not biometric modalities.** Store them in `auth_method`; set `modality` only for biometric factors such as face or fingerprint.

## Related

- [[modules/identity-verification/overview|Identity Verification Module]]
- [[frontend/architecture/overview|Biometric Devices Overview]]
- [[modules/identity-verification/biometric-enrollment/end-to-end-logic|Biometric Enrollment - End-to-End Logic]]
- [[modules/identity-verification/verification-policies/end-to-end-logic|Verification Policies - End-to-End Logic]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
