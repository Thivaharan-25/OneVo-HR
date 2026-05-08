# Chatbot API Integration â€” Semantic Kernel

**Module:** Shared Platform
**Phase:** 1 (OAuth client registration + bridge key scoping)
**Purpose:** Enable the WMS team's Semantic Kernel chatbot to call ONEVO APIs on behalf of authenticated users, with all existing RBAC permissions enforced automatically.

> [!IMPORTANT]
> **ONEVO does NOT build the chatbot.** The WMS team builds it using Microsoft Semantic Kernel. ONEVO's responsibility is to expose a secure, permission-checked API that the chatbot can call. Every action the chatbot requests goes through the same `[RequirePermission]` attribute as any other ONEVO client â€” if the user doesn't have access, the API returns 403 and the chatbot tells the user they lack permission.

---

## Architecture

```
User (talking to WMS chatbot)
    â”‚
    â–¼
WMS Chatbot (Semantic Kernel)
    â”‚  Uses ONEVO delegated server-side session/bridge token
    -  ONEVO backend calls APIs with backend-held auth context
    â–¼
ONEVO REST API (/api/v1/*)
    â”‚  [RequirePermission("leave:approve")] â€” user's own permissions checked
    â”‚  Returns 403 if insufficient â†’ chatbot says "You don't have access for that"
    â–¼
Database (tenant-scoped, all existing RBAC rules apply)
```

No special chatbot endpoints. No bypasses. The chatbot is just another API consumer.

---

## How User Authentication Works

**Scenario: Chatbot embedded in ONEVO UI**

The chatbot widget runs inside the ONEVO frontend. The user is already authenticated with ONEVO through the HttpOnly cookie-backed web session. Chatbot JavaScript must not read or forward a user JWT. Instead, the widget calls a ONEVO backend chatbot bridge with `credentials: "include"`; the backend validates the session and invokes the Semantic Kernel backend or ONEVO APIs using backend-held auth context.

This keeps browser tokens hidden while still enforcing the user's ONEVO permissions.

**Scenario: Standalone WMS app calls ONEVO on behalf of user**

The user explicitly authorizes WMS to act on their behalf in ONEVO. This requires OAuth 2.0 Authorization Code + PKCE flow:

1. WMS registers as an OAuth client in ONEVO (`POST /api/v1/oauth/clients` â€” Admin only)
2. User clicks "Connect ONEVO" in WMS â†’ redirect to ONEVO OAuth authorize screen
3. User reviews requested scopes and approves
4. ONEVO issues a delegated access token (same JWT structure, contains user's permissions)
5. WMS chatbot uses this token for all subsequent ONEVO API calls

**Phase 1:** Backend chatbot bridge for the embedded scenario. **Phase 2:** Full OAuth 2.0 AS (standalone scenario â€” builds on top of the existing Auth module).

---

## Permission Enforcement â€” How It Works

All existing ONEVO API endpoints use `[RequirePermission("resource:action")]`. This attribute:
1. Resolves the user identity from the cookie-backed session or delegated backend-held token
2. Loads the user's effective permissions (role permissions + overrides)
3. Checks if the required permission is present
4. Returns `403 Forbidden` (RFC 7807 Problem Details) if not

The chatbot receives the 403 response. Semantic Kernel's function calling mechanism surfaces this as an error. The chatbot converts it to a user-facing message: **"You don't have permission to [action]. Contact your administrator if you need access."**

No extra permission logic is needed â€” the existing RBAC system handles everything.

### Examples

| User asks chatbot | ONEVO API call | User has permission? | Result |
|:-----------------|:---------------|:---------------------|:-------|
| "Approve this leave request" | `POST /api/v1/workflows/{id}/approve` | `leave:approve` âœ“ | Approved |
| "Create a calendar event" | `POST /api/v1/calendar/events` | `calendar:write` âœ— | "You don't have access to create calendar events" |
| "Show me John's attendance" | `GET /api/v1/attendance/{employeeId}` | `attendance:read-team` âœ“ | Returns data |
| "Run payroll" | `POST /api/v1/payroll/runs` | `payroll:run` âœ— | "You don't have permission to run payroll" |

---

## Semantic Kernel Integration Pattern

The WMS team uses Semantic Kernel to define ONEVO API functions as SK Kernel Functions (plugins). Two approaches:

**Option A: OpenAPI Plugin** (recommended â€” less maintenance)
- ONEVO exposes its OpenAPI/Swagger spec at `/api/v1/swagger.json`
- WMS loads it as an OpenApiKernelPlugin: `kernel.ImportPluginFromOpenApiAsync("ONEVO", new Uri("https://api.onevo.com/api/v1/swagger.json"), ...)`
- SK automatically discovers all endpoints as callable functions
- The backend-held auth context is applied by ONEVO server-side integration code

**Option B: Custom Kernel Functions**
- WMS team writes C# Kernel Functions that wrap specific ONEVO endpoints
- More control, more maintenance

ONEVO's existing Swagger/OpenAPI doc (`Swagger/OpenAPI 3.0`) is already generated â€” no changes needed for Option A.

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

2. **Scope definitions** â€” map ONEVO permissions to OAuth scopes:
   - `onevo.read` â†’ read-only permissions only
   - `onevo.hr.leave` â†’ leave-related permissions
   - `onevo.hr.approvals` â†’ approval permissions
   - `onevo.workforce` â†’ workforce intelligence permissions
   - `onevo.admin` â†’ admin-level permissions (requires explicit user consent)

3. **Token binding** â€” delegated tokens must include `azp` (authorized party) claim identifying the WMS OAuth client, so ONEVO audit logs show "action performed by [user] via [WMS chatbot]"

### For the WMS team to implement

1. Do not expose ONEVO user JWTs to browser JavaScript; embedded chatbot calls use the ONEVO HttpOnly session and backend bridge
2. Session refresh handling - rely on ONEVO cookie session refresh for embedded web use
3. Never log ONEVO API responses containing PII
4. Handle 403 gracefully â€” surface to user as "no permission" message, not as an error
5. Rate limit chatbot calls â€” respect ONEVO's `X-RateLimit-*` headers

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
| POST | `/api/v1/oauth/token` | Public | Token exchange (code â†’ JWT) |
| POST | `/api/v1/oauth/token/refresh` | Public | Refresh access token |
| POST | `/api/v1/oauth/clients` | `settings:admin` | Register new OAuth client (WMS) |
| GET | `/api/v1/oauth/clients` | `settings:admin` | List OAuth clients |
| DELETE | `/api/v1/oauth/clients/{id}` | `settings:admin` | Revoke OAuth client |

---

## Related

- [[modules/auth/overview|Auth Module]] â€” JWT infrastructure this builds on
- [[modules/shared-platform/overview|Shared Platform]] â€” Where OAuth client registration lives
- [[backend/external-integrations|External Integrations]] â€” External first-party integration conventions (separate from chatbot API)
- [[AI_CONTEXT/rules|Rules]] â€” `[RequirePermission]` convention



