# Landing Page

**Area:** Auth & Access  
**Trigger:** User navigates to `https://{tenantSlug}.onevo.com` (any unauthenticated visit â€” every session start)  
**Required Permission(s):** None (public endpoint, no auth)  
**Related Permissions:** All â€” after sign-in, the user's effective permissions determine what dashboard zones they see

---

## Preconditions

- Tenant exists and is active (resolved from subdomain)
- Tenant branding has been configured (optional â€” defaults to ONEVO brand if not set)
- User has NOT yet signed in (authenticated users are redirected to `/dashboard` on arrival)

---

## Flow Steps

### Step 1: Navigate to Landing Page

- **UI:** Browser navigates to `https://{tenantSlug}.onevo.com`. While branding loads: base dark background (`#09090b`), no flash of unstyled content (branding applied before first paint via server-side fetch). Navbar appears: tenant logo + name left, `System Live` status pill + `Sign In â†’` button right
- **API:** `GET /api/v1/tenants/current/branding`
  - Response: `{ logoUrl, name, primaryColor, tagline, publicStats: { activeNow, idleAway, alertCount, avgScore } }`
  - No auth required. Tenant resolved from `Host` header (subdomain)
  - Cache-Control: `public, max-age=300`
- **Backend:** `TenantBrandingController.GetBranding()` â†’ `TenantResolver.ResolveAsync()` â†’ `IBrandingRepository.GetByTenantIdAsync()`
- **Validation:** Tenant must exist. If subdomain not found: serve generic ONEVO landing, not an error page
- **DB:** `tenants`, `tenant_branding`

### Step 2: Tenant Branding Applied

- **UI:** `--primary` CSS variable overridden with `tenant.primaryColor` on `document.documentElement` (if set). Tenant logo displayed in navbar (32Ã—32, rounded). Tenant name shown in navbar and hero footer. If no `primaryColor`: falls back to default `#7c3aed` (Violet Electric)
- **API:** N/A (branding already in Step 1 response)
- **Backend:** N/A
- **Validation:** `primaryColor` must be valid 6-digit hex; if malformed, use default
- **DB:** None

### Step 3: Hero and 3D Scene Render

- **UI:** Hero renders with two columns:
  - **Left:** Eyebrow (`WORKFORCE INTELLIGENCE â”€â”€â”€â”€`), H1 headline ("See your / workforce. / Right now." â€” line 3 in brand gradient), subtitle paragraph, 2 CTA buttons (`Access Dashboard` â†’ opens sign-in modal, `Watch 2-min Demo` â†’ future), 4 live stat counters (Active Now, Idle/Away, Alerts, Avg Score)
  - **Right:** Three.js particle scene lazy-loaded after initial paint â€” 2,400 particles (800 on mobile or `prefers-reduced-motion`) scatter and assemble into a human figure over ~2.8s. Cyan scan line (`#00d4ff`) sweeps from feet to head every 4s. HUD overlay cards appear (Identity Verified, Productivity, Attendance, Exception Alert). Mouse parallax active (Â±0.3rad)
- **API:** Live stat counters use `publicStats` from Step 1 response (no separate call)
- **Backend:** `publicStats` returns aggregate counts â€” no PII, no employee names
- **Validation:** Three.js loaded via dynamic import (`import('three')`). If device memory < threshold or `prefers-reduced-motion` is set: particle scene is replaced with a static CSS/SVG fallback
- **DB:** None (stats are cached aggregates)

### Step 4: Stat Counters Animate

- **UI:** All 4 counters animate from 0 â†’ target value over ~1s using `requestAnimationFrame` (cubic ease-out). Counters separated by 1px vertical dividers. Colors: Active Now = `--status-active`, Idle/Away = `--status-warning`, Alerts = `--status-critical`, Avg Score = `--primary`
- **API:** N/A (data already loaded)
- **Backend:** N/A
- **Validation:** N/A
- **DB:** None

### Step 5: User Clicks "Sign In â†’" or "Access Dashboard"

- **UI:** Sign-in modal opens. Overlay: `rgba(0,0,0,0.75)` + `backdrop-filter: blur(10px)`. Modal (360px): tenant logo, tenant name, Work Email field, Password field, Remember me checkbox, Forgot password? link, Sign In â†’ button, or Continue with SSO button. No "Create account" â€” users are invited by admin only. Landing page remains visible behind overlay
- **API:** N/A (modal opens client-side)
- **Backend:** N/A
- **Validation:** Client-side: valid email format, password not empty
- **DB:** None

### Step 6: User Submits Sign-In Form

- **UI:** Loading spinner on Sign In â†’ button. Errors displayed inline below the form
- **API:** `POST /api/v1/auth/login` â€” see [[Userflow/Auth-Access/login-flow|Login Flow]] for full detail
- **Backend:** `AuthService.LoginAsync()` â€” validates credentials, checks lockout, issues JWT or MFA challenge
- **Validation:** Email exists in tenant. Password matches. Account active and not locked
- **DB:** `users`, `login_attempts`

### Step 7: Redirect to Dashboard

- **UI:** On successful login: modal closes, user redirected to `/dashboard`. Dashboard loads based on backend session metadata (permissions, granted_modules, hierarchy_scope)
- **API:** `GET /api/v1/dashboard` â€” see [[Userflow/Dashboard/dashboard-overview|Dashboard Overview]]
- **Backend:** `DashboardService.GetEnabledZonesAsync()` â€” assembles enabled zones based on effective permissions
- **Validation:** HttpOnly session cookie validated on every subsequent request via middleware
- **DB:** Various (dashboard widget queries)

---

## Variations

### When user is already signed in
- Valid HttpOnly session cookie triggers session refresh on page load
- `POST /api/v1/auth/refresh` â†’ refreshed session metadata â†’ redirect to `/dashboard` immediately
- Landing page is never fully rendered for authenticated users

### When SSO is configured for the tenant
- "Continue with SSO" button visible in sign-in modal
- Clicking redirects to tenant's configured identity provider (Google / Azure AD)
- On IDP callback: `AuthService.HandleSsoCallbackAsync()` issues ONEVO JWT â†’ redirect to `/dashboard`
- MFA step skipped (handled by IDP)

### When tenant has no branding configured
- `logo_url` is null: ONEVO wordmark shown in navbar and modal
- `primary_color` is null: default `#7c3aed` used throughout
- `tagline` is null: default hero subtitle used
- Page is still fully functional â€” branding fields are all optional

### When tenant subdomain is not found
- `GET /api/v1/tenants/current/branding` returns 404
- User sees generic ONEVO landing page with no tenant branding and a tenant selector input
- Tenant selector submits to `https://{enteredSubdomain}.onevo.com`

### When Three.js particle scene fails to load
- Dynamic import failure caught silently
- Static fallback renders: CSS gradient background + SVG human silhouette (no animation)
- All other landing page elements unaffected

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Sign-in with wrong credentials | `401 Unauthorized` | "Invalid email or password" (no hint which field is wrong) |
| Account locked after 5 failed attempts | `423 Locked` | "Account temporarily locked. Try again in 15 minutes or contact your administrator" |
| Account disabled | `403 Forbidden` | "Your account has been disabled. Contact your administrator" |
| Tenant inactive | `403 Forbidden` | "This organization's account is currently inactive" |
| SSO provider error | Redirect back with error param | "Single sign-on failed. Please try again or contact your administrator" |
| Branding API timeout | Fallback to defaults | Landing page renders with default ONEVO branding, no error shown |

---

## Events Triggered

- `UserLoggedInEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]] â€” on successful sign-in
- `LoginFailedEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]] â€” on failed sign-in attempt
- `SessionCreatedEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]] â€” on JWT issuance

---

## Related Flows

- [[Userflow/Auth-Access/login-flow|Login Flow]] â€” full credential validation and JWT issuance detail
- [[Userflow/Auth-Access/password-reset|Password Reset]] â€” triggered from "Forgot password?" link
- [[Userflow/Auth-Access/mfa-setup|MFA Setup]] â€” MFA challenge if enabled for the user
- [[Userflow/Platform-Setup/sso-configuration|SSO Configuration]] â€” how SSO is set up for the tenant
- [[Userflow/Platform-Setup/tenant-branding|Tenant Branding]] â€” how logo, colors, tagline are configured
- [[Userflow/Dashboard/dashboard-overview|Dashboard Overview]] â€” what the user lands on after sign-in

---

## Module References

- [[modules/infrastructure/overview|Infrastructure]] â€” tenant resolution from subdomain
- [[frontend/cross-cutting/authentication|Authentication]] â€” JWT issuance, session handling
- [[frontend/cross-cutting/authorization|Authorization]] â€” effective permissions after login
- [[modules/auth/session-management/overview|Session Management]] â€” session creation and silent refresh





