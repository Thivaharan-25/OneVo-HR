# Known Issues & Gotchas: Desktop Agent

## Gotchas

### Win32 API Hooks

- **`SetWindowsHookEx` for keyboard/mouse** — use `WH_KEYBOARD_LL` and `WH_MOUSE_LL` (low-level hooks). These work system-wide but require a message pump. The Windows Service must run a message loop on a dedicated thread.
- **Hook thread must be STA** — Win32 hooks require a Single-Threaded Apartment thread with `Application.Run()` or equivalent message loop.
- **Antivirus false positives** — keyboard hooks trigger some AV heuristics. MSIX signing with a trusted certificate mitigates this. Include exclusion documentation for IT teams.

### MAUI Tray App

- **MAUI doesn't natively support system tray** — use `CommunityToolkit.Maui` or `H.NotifyIcon.WinUI` for tray icon functionality.
- **MAUI app must NOT be the main entry point** — the Windows Service is the primary process. MAUI app launches separately and connects via Named Pipes.
- **Camera access** — requires `webcam` capability in `Package.appxmanifest`. User is prompted on first use.

### SQLite Buffer

- **WAL mode required** — use Write-Ahead Logging for concurrent read/write (Service writes, sync reads).
- **Buffer size limit** — if SQLite file exceeds 100MB, drop oldest unsent records. Log a warning.
- **Encryption** — use SQLCipher for data-at-rest encryption. Key derived from machine DPAPI.

### Network

- **Corporate proxies** — some companies route traffic through HTTP proxies. Agent must respect system proxy settings via `HttpClient.DefaultProxy`.
- **VPN disconnects** — common in remote work. Agent must handle sudden network loss gracefully (buffer locally).
- **Certificate pinning** — in production, pin to ONEVO's certificate to prevent MITM. In dev, allow self-signed.

### Device JWT

- **Token stored via DPAPI** — `ProtectedData.Protect()` with `DataProtectionScope.LocalMachine`. This means the token is tied to the machine, not the user.
- **Token refresh** — Device JWT has 24-hour expiry. Agent must refresh before expiry. If refresh fails (revoked), show error in tray app.
- **Multiple users on one machine** — edge case. Device is registered once, but different employees can log in/out. The `employee_id` changes on login, but `device_id` stays the same.

### Idle Detection

- **`GetLastInputInfo` quirk** — returns time since last keyboard/mouse input system-wide, NOT per-application. A user typing in Notepad counts as "active" even if they should be in Teams.
- **Screensaver/lock screen** — when the screen locks, `GetLastInputInfo` stops updating. Treat screen lock as idle.
- **Remote desktop** — RDP sessions have their own input state. Agent detects this via session change notifications (`WTSRegisterSessionNotification`).

### Meeting Detection

- **Phase 1: Process name matching only** — detect Teams.exe, zoom.exe, meet (Chrome tab — unreliable). This is basic and has false positives (Teams running in background ≠ in meeting).
- **Camera/mic detection** — check if camera/microphone devices are in use via Windows Multimedia API. Presence of camera activity during meeting app = likely in meeting.
- **Phase 2:** Microsoft Teams Graph API will provide accurate meeting data.

### Installation

- **MSIX requires Windows 10 1809+** — older Windows versions not supported.
- **Auto-start** — Windows Service set to `Automatic (Delayed Start)`. MAUI app auto-starts via registry `Run` key for logged-in user.
- **Uninstall** — MSIX uninstall removes both Service and MAUI app. SQLite buffer and logs are cleaned up.
- **Updates** — MSIX supports auto-update from a URL. Agent checks for updates on heartbeat response.

## Technical Debt

None yet — greenfield project.
