# Data Collection Architecture

## Collection Pipeline

Each collector runs on its own timer. Data flows: Collector → SQLite Buffer → Sync Service → Agent Gateway.

## Collectors

### 1. Activity Collector (`ActivityCollector.cs`)

**What:** Keyboard and mouse event counts per snapshot interval.

**How:**
```csharp
// Low-level keyboard hook (WH_KEYBOARD_LL)
private IntPtr _keyboardHookId;
private int _keyboardCount = 0;

_keyboardHookId = SetWindowsHookEx(WH_KEYBOARD_LL, KeyboardProc, IntPtr.Zero, 0);

private IntPtr KeyboardProc(int nCode, IntPtr wParam, IntPtr lParam)
{
    if (nCode >= 0 && (wParam == WM_KEYDOWN || wParam == WM_SYSKEYDOWN))
        Interlocked.Increment(ref _keyboardCount);
    return CallNextHookEx(_keyboardHookId, nCode, wParam, lParam);
}
```

**Output per snapshot:**
```json
{
  "keyboard_events_count": 342,
  "mouse_events_count": 128,
  "active_seconds": 140,
  "idle_seconds": 10
}
```

**Frequency:** Captured continuously, flushed every `snapshot_interval_seconds` (default 150s / 2.5 min).

**Privacy:** Counts only. NEVER log which keys were pressed.

### 2. App Tracker (`AppTracker.cs`)

**What:** Foreground application name and window title (hashed).

**How:**
```csharp
var hwnd = GetForegroundWindow();
var processId = 0u;
GetWindowThreadProcessId(hwnd, out processId);
var process = Process.GetProcessById((int)processId);
var appName = process.ProcessName; // e.g., "chrome"

var title = new StringBuilder(256);
GetWindowText(hwnd, title, 256);
var titleHash = SHA256.HashData(Encoding.UTF8.GetBytes(title.ToString()));
```

**Output:**
```json
{
  "application_name": "Google Chrome",
  "window_title_hash": "a1b2c3d4...",
  "duration_seconds": 45
}
```

**Frequency:** Polled every 5 seconds. Aggregated per app per snapshot interval.

**Privacy:** Window title is SHA-256 hashed BEFORE buffering. Raw title never touches disk.

### 3. Idle Detector (`IdleDetector.cs`)

**What:** Detects when user has no keyboard/mouse input.

**How:**
```csharp
[DllImport("user32.dll")]
static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);

var lastInput = new LASTINPUTINFO { cbSize = (uint)Marshal.SizeOf<LASTINPUTINFO>() };
GetLastInputInfo(ref lastInput);
var idleMs = Environment.TickCount - lastInput.dwTime;
var isIdle = idleMs > _policy.IdleThresholdSeconds * 1000;
```

**Idle threshold:** Configurable via policy (default 300 seconds / 5 min).

**Break detection:** If idle exceeds threshold, mark as break candidate. Server-side reconciliation in [[workforce-presence]] creates the break record.

### 4. Meeting Detector (`MeetingDetector.cs`)

**What:** Detects active video/audio meeting applications.

**How (Phase 1 — process name matching):**
```csharp
private static readonly string[] MeetingProcesses = { "Teams", "Zoom", "zoom", "meet" };

var processes = Process.GetProcesses();
var meetingProcess = processes.FirstOrDefault(p => MeetingProcesses.Any(m => 
    p.ProcessName.Contains(m, StringComparison.OrdinalIgnoreCase)));

if (meetingProcess != null)
{
    // Check if camera is active (Windows Multimedia API)
    var cameraActive = await _cameraService.IsCameraInUseAsync();
    // Check if microphone is active
    var micActive = await _audioService.IsMicrophoneInUseAsync();
}
```

**Output:**
```json
{
  "platform": "teams",
  "meeting_start": "2026-04-05T10:00:00Z",
  "had_camera_on": true,
  "had_mic_activity": true
}
```

**Limitations:** Process name matching has false positives (Teams running in background). Phase 2 uses Teams Graph API.

### 5. Device Tracker (`DeviceTracker.cs`)

**What:** Tracks device active vs idle cycles for `device_sessions` on the server.

**How:** Combines idle detector state with session tracking:
- Session starts when first input detected after boot/login
- Session splits when idle exceeds threshold
- Session ends on logout/shutdown

## SQLite Buffer Schema

```sql
CREATE TABLE activity_buffer (
    id TEXT PRIMARY KEY,
    data_type TEXT NOT NULL,  -- 'snapshot', 'app_usage', 'meeting', 'device_session'
    payload TEXT NOT NULL,     -- JSON
    captured_at TEXT NOT NULL,
    sent INTEGER DEFAULT 0,
    sent_at TEXT
);

CREATE INDEX idx_buffer_unsent ON activity_buffer (sent, captured_at);
```

## Batch Format

Data is batched into the ingestion payload format expected by Agent Gateway:

```json
{
  "device_id": "uuid",
  "employee_id": "uuid",
  "timestamp": "2026-04-05T10:30:00Z",
  "batch": [
    {"type": "activity_snapshot", "data": {...}},
    {"type": "app_usage", "data": {...}},
    {"type": "device_session", "data": {...}},
    {"type": "meeting", "data": {...}}
  ]
}
```

See `agent/AI_CONTEXT/rules.md` for privacy rules and `docs/architecture/modules/agent-gateway.md` in the backend brain for the server-side contract.
