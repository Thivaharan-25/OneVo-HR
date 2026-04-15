# Chatbot API Integration — Semantic Kernel

**Module:** Shared Platform
**Phase:** 1 (OAuth client registration + bridge key scoping)
**Purpose:** Enable the WMS team's Semantic Kernel chatbot to call ONEVO APIs on behalf of authenticated users, with all existing RBAC permissions enforced automatically.

> [!IMPORTANT]
> **ONEVO does NOT build the chatbot.** The WMS team builds it using Microsoft Semantic Kernel. ONEVO's responsibility is to expose a secure, permission-checked API that the chatbot can call. Every action the chatbot requests goes through the same `[RequirePermission]` attribute as any other ONEVO client — if the user doesn't have access, the API returns 403 and the chatbot tells the user they lack permission.

---

## Architecture

```
User (talking to WMS chatbot)
    │
    ▼
WMS Chatbot (Semantic Kernel)
    │  Uses ONEVO JWT on behalf of the user
    │  Authorization: Bearer <user_jwt>
    ▼
ONEVO REST API (/api/v1/*)
    │  [RequirePermission("leave:approve")] — user's own permissions checked
    │  Returns 403 if insufficient → chatbot says "You don't have access for that"
    ▼
Database (tenant-scoped, all existing RBAC rules apply)
```

No special chatbot endpoints. No bypasses. The chatbot is just another API consumer.

---

## How User Authentication Works

**Scenario: Chatbot embedded in ONEVO UI**

The chatbot widget runs inside the ONEVO frontend. The user is already authenticated with ONEVO. The chatbot JavaScript has access to the user's current JWT (access token in memory). It passes this JWT to the Semantic Kernel backend, which uses it as the Bearer token for all ONEVO API calls.

This is the simplest and most secure approach — no new auth flows, no new tokens.

**Scenario: Standalone WMS app calls ONEVO on behalf of user**

The user explicitly authorizes WMS to act on their behalf in ONEVO. This requires OAuth 2.0 Authorization Code + PKCE flow:

1. WMS registers as an OAuth client in ONEVO (`POST /api/v1/oauth/clients` — Admin only)
2. User clicks "Connect ONEVO" in WMS → redirect to ONEVO OAuth authorize screen
3. User reviews requested scopes and approves
4. ONEVO issues a delegated access token (same JWT structure, contains user's permissions)
5. WMS chatbot uses this token for all subsequent ONEVO API calls

**Phase 1:** JWT pass-through (embedded scenario). **Phase 2:** Full OAuth 2.0 AS (standalone scenario — builds on top of the existing Auth module).

---

## Permission Enforcement — How It Works

All existing ONEVO API endpoints use `[RequirePermission("resource:action")]`. This attribute:
1. Extracts the user identity from the Bearer JWT
2. Loads the user's effective permissions (role permissions + overrides)
3. Checks if the required permission is present
4. Returns `403 Forbidden` (RFC 7807 Problem Details) if not

The chatbot receives the 403 response. Semantic Kernel's function calling mechanism surfaces this as an error. The chatbot converts it to a user-facing message: **"You don't have permission to [action]. Contact your administrator if you need access."**

No extra permission logic is needed — the existing RBAC system handles everything.

### Examples

| User asks chatbot | ONEVO API call | User has permission? | Result |
|:-----------------|:---------------|:---------------------|:-------|
| "Approve this leave request" | `POST /api/v1/workflows/{id}/approve` | `leave:approve` ✓ | Approved |
| "Create a calendar event" | `POST /api/v1/calendar/events` | `calendar:write` ✗ | "You don't have access to create calendar events" |
| "Show me John's attendance" | `GET /api/v1/attendance/{employeeId}` | `attendance:read-team` ✓ | Returns data |
| "Run payroll" | `POST /api/v1/payroll/runs` | `payroll:run` ✗ | "You don't have permission to run payroll" |

---

## Semantic Kernel Integration Pattern

The WMS team uses Semantic Kernel to define ONEVO API functions as SK Kernel Functions (plugins). Two approaches:

**Option A: OpenAPI Plugin** (recommended — less maintenance)
- ONEVO exposes its OpenAPI/Swagger spec at `/api/v1/swagger.json`
- WMS loads it as an OpenApiKernelPlugin: `kernel.ImportPluginFromOpenApiAsync("ONEVO", new Uri("https://api.onevo.com/api/v1/swagger.json"), ...)`
- SK automatically discovers all endpoints as callable functions
- The JWT is passed via `HttpClientFactory` with the Bearer header pre-set

**Option B: Custom Kernel Functions**
- WMS team writes C# Kernel Functions that wrap specific ONEVO endpoints
- More control, more maintenance

ONEVO's existing Swagger/OpenAPI doc (`Swagger/OpenAPI 3.0`) is already generated — no changes needed for Option A.

---

## Security Requirements

### For ONEVO to implement

1. **OAuth client registration table** (Phase 2 if standalone scenario needed):
   ```
   oauth_clients
   - id, tenant_id, client_name, client_id (public), client_secret_hash
   - redirect_uris (text[])
   - allowed_scopes (text[])
   - is_active
   ```

2. **Scope definitions** — map ONEVO permissions to OAuth scopes:
   - `onevo.read` → read-only permissions only
   - `onevo.hr.leave` → leave-related permissions
   - `onevo.hr.approvals` → approval permissions
   - `onevo.workforce` → workforce intelligence permissions
   - `onevo.admin` → admin-level permissions (requires explicit user consent)

3. **Token binding** — delegated tokens must include `azp` (authorized party) claim identifying the WMS OAuth client, so ONEVO audit logs show "action performed by [user] via [WMS chatbot]"

### For the WMS team to implement

1. Store ONEVO user JWTs securely — never in localStorage, use HttpOnly cookie or in-memory
2. Refresh token handling — intercept 401 responses and refresh before retrying
3. Never log ONEVO API responses containing PII
4. Handle 403 gracefully — surface to user as "no permission" message, not as an error
5. Rate limit chatbot calls — respect ONEVO's `X-RateLimit-*` headers

---

## Chatbot-Accessible Features (Phase 1)

Actions the chatbot can perform on behalf of a user (all subject to user's permissions):

**Leave:**
- View pending leave requests (manager: all team, employee: own)
- Approve / reject leave request with note
- Show conflict summary for a leave request (uses `conflict_snapshot_json`)
- Check employee leave balance

**Calendar:**
- View calendar events for date range
- Create calendar event (if `calendar:write` permission)

**Employee:**
- Look up employee profile (if `employees:read` or `employees:read-team`)
- Check who is on leave today

**Workforce:**
- Check employee attendance status (if `attendance:read-team`)
- View exception alerts (if `exceptions:view`)

**Notifications:**
- List unread notifications for the current user

---

## API Endpoints for Chatbot OAuth (Phase 2)

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/oauth/authorize` | Public | OAuth authorization screen |
| POST | `/api/v1/oauth/token` | Public | Token exchange (code → JWT) |
| POST | `/api/v1/oauth/token/refresh` | Public | Refresh access token |
| POST | `/api/v1/oauth/clients` | `settings:admin` | Register new OAuth client (WMS) |
| GET | `/api/v1/oauth/clients` | `settings:admin` | List OAuth clients |
| DELETE | `/api/v1/oauth/clients/{id}` | `settings:admin` | Revoke OAuth client |

---

## Related

- [[modules/auth/overview|Auth Module]] — JWT infrastructure this builds on
- [[modules/shared-platform/overview|Shared Platform]] — Where OAuth client registration lives
- [[backend/external-integrations|External Integrations]] — Bridge endpoints (separate from chatbot API)
- [[AI_CONTEXT/rules|Rules]] — `[RequirePermission]` convention
