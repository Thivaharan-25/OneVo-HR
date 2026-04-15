# Browser Extension — Domain Activity Tracking

**Phase:** Phase 2 (optional add-on, tenant-configurable)
**Supported Browsers:** Chrome, Microsoft Edge, Firefox
**Controlled by:** `browser_extension_enabled` in agent policy

---

## Purpose

The browser extension provides domain-level visibility into how employees spend time in the browser. It captures only the **domain name** and time spent — never the URL path, page content, search queries, or any personal data within the page.

This is the only way to reliably detect:
- Google Meet sessions (no desktop process — fully browser-based)
- Time in Google Docs/Sheets/Slides
- Research time on work-relevant domains (GitHub, Confluence, Jira)
- Work vs personal browsing ratio

---

## What It Captures

| Signal | Captured | Never Captured |
|:-------|:---------|:---------------|
| Domain name | `github.com` | URL path (`/org/repo/pull/123`) |
| Time on domain | Seconds active | Page content or text |
| Domain classification | `work` / `personal` / `meeting` | Search query |
| Browser name | `chrome`, `edge`, `firefox` | Browsing history list |
| Meeting detection | `meet.google.com` → meeting start/end | Call content or participants |

---

## Architecture

The extension is a standard browser extension (Manifest V3) that communicates with the WorkPulse Agent service via a **native messaging host**.

```
Browser Extension (JS)
    ↓  chrome.tabs.onActivated / onUpdated
    ↓  domain extracted from tab.url (hostname only)
    ↓  Native Messaging API
Native Messaging Host (C# console app, registered per-browser)
    ↓  Named Pipe → ONEVO.Agent.Service
WorkPulse Agent Service
    ↓  Buffers to SQLite
    ↓  Syncs to Agent Gateway API
```

### Native Messaging Host

```csharp
// ONEVO.Agent.BrowserBridge/Program.cs
// Registered as native messaging host in browser extension manifest.
// Receives domain events from the browser extension via stdin/stdout (Native Messaging protocol).

public class BrowserBridgeHost
{
    public async Task RunAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            var message = await ReadNativeMessageAsync(ct);
            if (message?.Domain == null) continue;

            // Forward to Agent Service via Named Pipe
            await _pipeClient.SendAsync(new BrowserDomainEvent
            {
                Domain = new Uri($"https://{message.Domain}").Host, // hostname only
                DurationSeconds = message.DurationSeconds,
                Browser = message.Browser
            }, ct);
        }
    }
}
```

### Browser Extension (Manifest V3)

```json
// manifest.json
{
  "manifest_version": 3,
  "name": "WorkPulse Activity Tracker",
  "version": "1.0.0",
  "description": "Tracks domain-level work activity for ONEVO WorkPulse.",
  "permissions": ["tabs", "nativeMessaging"],
  "background": {
    "service_worker": "background.js"
  },
  "host_permissions": ["<all_urls>"]
}
```

```javascript
// background.js — domain tracking only
let activeTabDomain = null;
let sessionStart = null;

function getDomain(url) {
  try {
    return new URL(url).hostname; // domain only — path stripped
  } catch {
    return null;
  }
}

chrome.tabs.onActivated.addListener(async ({ tabId }) => {
  const tab = await chrome.tabs.get(tabId);
  flushCurrentSession();
  activeTabDomain = getDomain(tab.url);
  sessionStart = Date.now();
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) {
    flushCurrentSession();
    activeTabDomain = getDomain(changeInfo.url);
    sessionStart = Date.now();
  }
});

function flushCurrentSession() {
  if (!activeTabDomain || !sessionStart) return;
  const duration = Math.round((Date.now() - sessionStart) / 1000);
  if (duration < 5) return; // ignore very short visits

  chrome.runtime.sendNativeMessage('com.onevo.workpulse', {
    domain: activeTabDomain,
    duration_seconds: duration,
    browser: 'chrome'
  });
  activeTabDomain = null;
  sessionStart = null;
}
```

---

## Domain Classification

Domains are classified by a configurable lookup engine on the server. The tenant admin can add custom rules.

| Domain | Default Classification |
|:-------|:----------------------|
| `github.com`, `gitlab.com`, `bitbucket.org` | `work` |
| `confluence.*.com`, `jira.*.com`, `atlassian.net` | `work` |
| `docs.google.com`, `sheets.google.com`, `slides.google.com` | `work` |
| `meet.google.com` | `meeting` |
| `teams.microsoft.com` | `meeting` |
| `zoom.us` | `meeting` |
| `youtube.com`, `netflix.com`, `reddit.com` | `personal` |
| Unknown domain | `unknown` (admin can classify) |

Classification is applied server-side during `ProcessRawBufferJob`. The agent sends the raw domain and the server applies the tenant's classification rules.

---

## Consent & Privacy

The browser extension **requires explicit separate consent** from the employee beyond the base WorkPulse consent:

1. The base HRMS consent flow includes a dedicated screen: "Enable browser domain tracking" — employee can accept or decline this specific feature independently.
2. If the employee declines browser tracking, `browser_extension_enabled: false` is set in their policy — the extension installs but collects nothing.
3. The extension icon in the browser toolbar shows green (active) or grey (paused/disabled) status at all times.
4. Employee can view all recorded domains in their personal ONEVO dashboard.

---

## Installation

The browser extension is installed separately from the MSIX package. Options:

| Method | How |
|:-------|:----|
| Admin push (Chrome/Edge) | Google Workspace Admin Console or Microsoft Intune Extension Policy |
| Manual install | Employee installs from Chrome Web Store / Edge Add-ons store using a company-shared extension ID |
| HRMS onboarding gate | After MSIX install, HRMS onboarding prompts for browser extension install (optional step) |

### Native Messaging Host Registration

The native messaging host (`ONEVO.Agent.BrowserBridge.exe`) is registered during MSIX install:

```json
// com.onevo.workpulse.json — placed in browser's native messaging registry
{
  "name": "com.onevo.workpulse",
  "description": "WorkPulse Browser Bridge",
  "path": "C:\\Program Files\\ONEVO\\WorkPulse\\ONEVO.Agent.BrowserBridge.exe",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://<extension-id>/"
  ]
}
```

---

## Data Flow

```
Browser tab change
  → extension extracts domain (hostname only)
  → sends to native messaging host via chrome.runtime.sendNativeMessage
  → BrowserBridge.exe receives via stdin
  → forwards to ONEVO.Agent.Service via Named Pipe
  → buffered in SQLite as type: "browser_domain"
  → synced to Agent Gateway /api/v1/agent/ingest
  → ProcessRawBufferJob writes to browser_activity table
  → activity_daily_summary.browser_active_minutes updated
```

---

## Related

- [[modules/agent-gateway/agent-overview|Agent Overview]] — WorkPulse Agent architecture
- [[modules/agent-gateway/data-collection|Data Collection]] — All 7 collectors
- [[database/schemas/activity-monitoring|Activity Monitoring Schema]] — `browser_activity` table
- [[modules/configuration/monitoring-toggles/overview|Configuration]] — `browser_extension_enabled` toggle
- [[modules/auth/gdpr-consent/overview|GDPR Consent]] — separate consent required for browser tracking
