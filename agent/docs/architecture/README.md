# Desktop Agent Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    ONEVO Desktop Agent                       │
│                                                              │
│  ┌─────────────────────────────────────────────┐            │
│  │         Windows Service (Background)         │            │
│  │                                              │            │
│  │  ┌────────────┐  ┌────────────┐             │            │
│  │  │  Activity   │  │   App      │             │            │
│  │  │  Collector  │  │   Tracker  │             │            │
│  │  └──────┬──────┘  └──────┬─────┘             │            │
│  │         │                │                    │            │
│  │  ┌──────┴────┐  ┌───────┴────┐              │            │
│  │  │   Idle    │  │  Meeting   │              │            │
│  │  │  Detector │  │  Detector  │              │            │
│  │  └──────┬────┘  └──────┬─────┘              │            │
│  │         │               │                    │            │
│  │         ▼               ▼                    │            │
│  │  ┌──────────────────────────┐               │            │
│  │  │    SQLite Buffer         │               │            │
│  │  │    (encrypted, WAL)      │               │            │
│  │  └────────────┬─────────────┘               │            │
│  │               │                              │            │
│  │  ┌────────────▼─────────────┐               │            │
│  │  │    Data Sync Service     │               │            │
│  │  │    (batch every 2-3 min) │               │            │
│  │  └────────────┬─────────────┘               │            │
│  │               │                              │            │
│  │  ┌────────────▼─────────────┐               │            │
│  │  │    Heartbeat Service     │               │            │
│  │  │    (every 60 sec)        │               │            │
│  │  └──────────────────────────┘               │            │
│  │               │ Named Pipes                  │            │
│  └───────────────┼──────────────────────────────┘            │
│                  │                                            │
│  ┌───────────────▼──────────────────────────────┐            │
│  │         MAUI Tray App (UI)                    │            │
│  │                                               │            │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │            │
│  │  │  Login   │ │  Photo   │ │   Status     │ │            │
│  │  │  Window  │ │  Capture │ │   Popup      │ │            │
│  │  └──────────┘ └──────────┘ └──────────────┘ │            │
│  └───────────────────────────────────────────────┘            │
│                  │                                            │
└──────────────────┼────────────────────────────────────────────┘
                   │ HTTPS (Device JWT)
                   ▼
         ┌─────────────────────┐
         │  Agent Gateway      │
         │  /api/v1/agent/*    │
         └─────────────────────┘
```

## Detailed Architecture Docs

- [[data-collection]] — how each data type is captured (Win32 APIs, timing, hashing)
- [[agent-server-protocol]] — full API contract with Agent Gateway
- [[tamper-resistance]] — detection and reporting of service manipulation
- [[photo-capture]] — camera access, photo quality, verification flow
