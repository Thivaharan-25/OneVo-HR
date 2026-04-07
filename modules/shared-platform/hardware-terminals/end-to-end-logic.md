# Hardware Terminals — End-to-End Logic

**Module:** Shared Platform
**Feature:** Hardware Terminal Management

---

## Register Terminal

### Flow

```
POST /api/v1/hardware/terminals
  -> HardwareController.Register(RegisterTerminalCommand)
    -> [RequirePermission("settings:admin")]
    -> HardwareTerminalService.RegisterAsync(command, ct)
      -> 1. Validate: terminal_code unique, terminal_type valid
      -> 2. Encrypt API key via IEncryptionService
      -> 3. INSERT into hardware_terminals
         -> status = 'active'
      -> Return Result.Success(terminalDto)
```

### Key Rules

- **Terminal types:** biometric, rfid, kiosk — each connects via webhook.
- **Health monitoring:** `last_heartbeat_at` checked by scheduled job.

## Related

- [[hardware-terminals|Overview]]
- [[real-time-integrations]]
- [[notification-infrastructure]]
- [[gdpr-consent]]
- [[event-catalog]]
- [[error-handling]]
