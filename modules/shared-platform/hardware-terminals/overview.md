# Hardware Terminals

**Module:** Shared Platform  
**Feature:** Hardware Terminals

---

## Purpose

Physical terminal management (biometric scanners, RFID, kiosks).

## Database Tables

### `hardware_terminals`
Fields: `office_location_id`, `terminal_code`, `terminal_type` (`biometric`, `rfid`, `kiosk`), `webhook_url`, `api_key_encrypted`, `status`, `last_heartbeat_at`.

## Related

- [[modules/shared-platform/overview|Shared Platform Module]]
- [[modules/shared-platform/real-time-integrations/overview|Real Time Integrations]]
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]]
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
