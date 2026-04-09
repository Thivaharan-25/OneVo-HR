# SSO Authentication — End-to-End Logic

**Module:** Shared Platform
**Feature:** SSO Provider Management

---

## Configure SSO Provider

### Flow

```
POST /api/v1/sso/providers
  -> SsoController.Create(CreateSsoProviderCommand)
    -> [RequirePermission("settings:admin")]
    -> SsoProviderService.CreateAsync(command, ct)
      -> 1. Validate provider_type: google, microsoft, saml, oidc
      -> 2. Encrypt client_id and client_secret via IEncryptionService
      -> 3. INSERT into sso_providers
         -> domain_hint for auto-selecting provider by email domain
         -> auto_provision_users flag
      -> Return Result.Success(providerDto)
```

## SSO Login Flow

### Flow

```
User clicks "Login with Google/Microsoft":
  -> 1. Redirect to SSO provider with client_id, redirect_uri
  -> 2. User authenticates with provider
  -> 3. Provider redirects back with auth code
  -> 4. Backend exchanges code for tokens
  -> 5. Extract user info (email, name)
  -> 6. Find user by email in tenant:
     -> If exists: generate ONEVO JWT tokens
     -> If not exists AND auto_provision_users = true:
        -> Create user account
        -> Generate ONEVO JWT tokens
     -> If not exists AND auto_provision = false:
        -> Return error "Account not found"

```

## Related

- [[modules/shared-platform/sso-authentication/overview|Overview]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[modules/infrastructure/user-management/overview|User Management]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
