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

- [[shared-platform|Shared Platform Module]]
- [[real-time-integrations]]
- [[notification-infrastructure]]
- [[gdpr-consent]]
- [[multi-tenancy]]
- [[authorization]]
- [[migration-patterns]]
- [[WEEK1-shared-platform]]
