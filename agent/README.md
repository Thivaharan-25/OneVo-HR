# ONEVO Desktop Agent — Secondary Brain

This is the AI-optimized knowledge base for the ONEVO Desktop Agent development team.

## What is the Desktop Agent?

The Desktop Agent is a Windows application installed on employee laptops that captures workforce activity data and sends it to the ONEVO backend via the [[agent-gateway]]. It consists of two components:

1. **Background Service** (.NET 9 Windows Service) — always-on data collector
2. **Tray App** (.NET MAUI) — system tray icon for employee login, photo capture, status display

## Architecture

```
┌─────────────────────────────────────────────┐
│              Employee Laptop                 │
│                                              │
│  ┌──────────────────┐  ┌──────────────────┐ │
│  │  Windows Service  │  │   MAUI Tray App  │ │
│  │  (Background)     │◄─┤  (UI)            │ │
│  │                   │  │                   │ │
│  │  - Activity       │  │  - Employee login │ │
│  │  - App tracking   │  │  - Photo capture  │ │
│  │  - Idle detection │  │  - Status display │ │
│  │  - Meeting detect │  │  - Policy display │ │
│  │  - Device tracking│  └──────────────────┘ │
│  │                   │     IPC: Named Pipes   │
│  └────────┬──────────┘                       │
│           │                                   │
│   SQLite (offline buffer)                    │
│           │                                   │
└───────────┼───────────────────────────────────┘
            │ HTTPS (Device JWT)
            ▼
┌───────────────────────┐
│   ONEVO Agent Gateway │
│   /api/v1/agent/*     │
└───────────────────────┘
```

## Reading Order

1. `AI_CONTEXT/project-context.md` — what the agent does
2. `AI_CONTEXT/tech-stack.md` — technologies and dependencies
3. `AI_CONTEXT/rules.md` — coding standards and security rules
4. `AI_CONTEXT/known-issues.md` — gotchas
5. `docs/architecture/` — detailed architecture docs

## Relationship to Backend

The agent communicates ONLY with the [[agent-gateway]] module. See the backend brain's `docs/architecture/modules/agent-gateway.md` for the server-side contract.

| Agent Action | Backend Endpoint | Frequency |
|:-------------|:----------------|:----------|
| Register device | `POST /api/v1/agent/register` | Once at install |
| Employee login | `POST /api/v1/agent/login` | On employee login |
| Fetch policy | `GET /api/v1/agent/policy` | On login + hourly |
| Send heartbeat | `POST /api/v1/agent/heartbeat` | Every 60 seconds |
| Send activity data | `POST /api/v1/agent/ingest` | Every 2-3 minutes |
| Employee logout | `POST /api/v1/agent/logout` | On employee logout |
