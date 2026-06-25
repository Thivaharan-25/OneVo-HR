# Hardware Terminals - End-to-End Logic

**Module:** Shared Platform  
**Feature:** Compatibility Redirect

---

## Canonical Flow

Do not implement a Shared Platform terminal-registration route or write to a separate hardware-terminal table. Physical attendance/biometric terminal registration uses the canonical device flow:

```
POST /api/v1/time-attendance/devices
  -> Register attendance/biometric terminal
  -> INSERT into biometric_devices
  -> Configure direct webhook, vendor middleware, local gateway, polling API, or manual import
  -> Terminal/gateway authenticates with HMAC/API key
```

## Key Rules

- `biometric_devices` is the canonical physical terminal table.
- Card/PIN are attendance credentials, not biometric modalities.
- `legal_entity_id` is required. Phase 1 does not assign terminals to a separate office-location table.
- Physical terminals and vendor middleware/local gateways use HMAC/API-key authentication, not WorkPulse Device JWT.
- WorkPulse desktop agents remain separate and are stored in `registered_agents`.

## Related

- [[modules/identity-verification/biometric-devices/overview|Biometric Devices]]
- [[modules/identity-verification/biometric-devices/end-to-end-logic|Biometric Devices - End-to-End Logic]]
- [[database/schemas/identity-verification#`biometric_devices`|biometric_devices]]
