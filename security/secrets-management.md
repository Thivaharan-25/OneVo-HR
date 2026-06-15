# Secrets Management

**Platform:** Railway (staging + production)
**Principle:** All secrets are environment variables — never committed to git, never in code.

---

## Secret Inventory

| Secret | Env Var | Format | Used For |
|:-------|:--------|:-------|:---------|
| JWT RSA private key | `JWT_PRIVATE_KEY` | PEM, base64-encoded | RS256 JWT signing |
| JWT RSA public key | `JWT_PUBLIC_KEY` | PEM, base64-encoded | RS256 JWT verification |
| JWT scoped token secret | `JWT_SCOPED_TOKEN_SECRET` | Base64-encoded 32 bytes minimum | Password-change and MFA pending token signing |
| AES-256 encryption key | `ENCRYPTION_KEY` | Base64-encoded 32 bytes | `bytea` encrypted columns (bank details, SSO creds, API keys) |
| PostgreSQL connection | `DATABASE_URL` | Railway auto-injects | EF Core data source |
| Redis connection | `REDIS_URL` | Optional/future | Distributed permission versioning, rate limiting, and caching if a multi-instance deployment enables Redis |
| Resend API key | `RESEND_API_KEY` | Opaque string | Email delivery |
| Email sender address | `EMAIL_FROM` | Verified email address/domain | Transactional and notification emails |
| App base URL | `APP_BASE_URL` | Absolute URL | Invite, password reset, and account setup links |
| Stripe secret key | `STRIPE_SECRET_KEY` | `sk_live_...` / `sk_test_...` | Stripe billing gateway |
| Stripe webhook secret | `STRIPE_WEBHOOK_SECRET` | `whsec_...` | Stripe webhook signature verification |
| PayHere merchant ID | `PAYHERE_MERCHANT_ID` | Merchant identifier | PayHere billing gateway |
| PayHere merchant secret | `PAYHERE_MERCHANT_SECRET` | Opaque secret | PayHere signature/hash verification |
| Bridge client secrets | Hashed in DB | BCrypt hash | Service-to-service auth - plaintext only at issuance, never stored |

---

## Storage — Railway Environment Variables

All secrets are set in Railway's **Environment Variables** panel per service per environment (staging, production). Railway injects them as process environment variables at runtime.

**Never put secrets in:**
- Source code or config files
- Application services/classes (services must read secrets through configuration/environment only)
- Docker Compose (dev Compose uses dummy values only — `dev_password`, `admin`)
- `.env` files committed to git
- Application logs

**Local development:** real local secret values may be stored only in git-ignored env files such as `OneVo-backend/.env`, generated from templates/scripts. Template files such as `.env.example` may contain variable names and placeholders only, never real keys.

**Environment promotion rule:** switching from Development to Staging/Production must not silently generate fallback keys. The app must fail fast during startup if required secret env vars are missing or invalid. This prevents tokens from being signed with throwaway in-memory keys after deployment.

---

## Key Details

### RSA Key Pair (JWT Signing)

- Algorithm: RS256, 2048-bit minimum
- Private key stored as `JWT_PRIVATE_KEY` (PEM, base64-encoded, newlines replaced with `\n`)
- Public key stored as `JWT_PUBLIC_KEY` for verification
- **Rotation:** 24-hour dual-key window — generate new pair, sign new tokens with new key, verify with both keys, retire old key after 24 hours. Users do not need to re-login.
- **Key ID (`kid`):** Embed in JWT header so the verifier knows which key to use during rotation

### JWT Runtime Environment

Tenant API issuer and audience are non-secret labels:

```text
JWT_ISSUER=onevo
JWT_AUDIENCE=onevo-api
```

Tenant access tokens are signed with `JWT_PRIVATE_KEY`. Internal scoped tokens for password-change and MFA-pending flows are signed with `JWT_SCOPED_TOKEN_SECRET`.

Required tenant auth environment block:

```text
JWT_PRIVATE_KEY=<base64 PEM private key>
JWT_SCOPED_TOKEN_SECRET=<base64 32+ random bytes>
JWT_ISSUER=onevo
JWT_AUDIENCE=onevo-api
```

`JWT_SCOPED_TOKEN_SECRET` must decode to at least 32 random bytes and is required before staging or production startup.

Do not store `JWT_PRIVATE_KEY` or `JWT_SCOPED_TOKEN_SECRET` inside token services, source files, committed appsettings files, or database seed data. Token services must only consume these values from the runtime configuration provider. Development may load them from a git-ignored `.env`; staging and production must load them from Railway environment variables.

### AES-256 Encryption Key

- Used by `IEncryptionService` for columns: `account_number_encrypted`, `client_id_encrypted`, `client_secret_encrypted`, `api_key_encrypted`, `credentials_encrypted`
- 32 random bytes, base64-encoded
- **Warning — rotation requires data migration:** Rotating this key requires re-encrypting every `bytea` encrypted column. Use key versioning: store `{version}:{ciphertext}` in the column so the decryption service knows which key version to use.
- Generate: `openssl rand -base64 32`

### Database Connection

- Railway injects `DATABASE_URL` automatically for linked PostgreSQL services
- Use `NpgsqlDataSourceBuilder` to parse the connection string
- Internal Railway networking (private IP) — DB port is NOT exposed externally in production
- PgBouncer sits in front of PostgreSQL in production (session pooling)

### Redis Connection

- Phase 1 does not require Redis; permission versioning, rate limiting, and policy caching use in-memory services.
- If a future distributed/multi-instance deployment enables Redis, Railway may inject `REDIS_URL` for linked Redis services.
- Redis must use internal Railway networking only; the Redis port must not be exposed externally.
- Future Redis usage: distributed permission version counters, rate limiting token buckets, and policy caching.

### Resend Email Delivery

- `RESEND_API_KEY` is required before Phase 1 customer release for all email notification channels and auth-related transactional emails.
- `EMAIL_FROM` must use a Resend-verified sender domain/address.
- `APP_BASE_URL` must be environment-specific so password reset, invite, and account setup links point to the correct web app.
- Logger-only email stubs are acceptable only for local development and automated tests.

### Payment Gateway Secrets

ONEVO Phase 1 primarily supports Stripe and PayHere. Production gateway secrets are provided through environment variables or encrypted gateway configuration records; never hardcode them in source code or committed appsettings files.

Global/default gateway env vars:

```text
STRIPE_SECRET_KEY=<sk_live or sk_test>
STRIPE_WEBHOOK_SECRET=<whsec>
PAYHERE_MERCHANT_ID=<merchant id>
PAYHERE_MERCHANT_SECRET=<merchant secret>
```

Payment gateway credentials are platform-managed in System Config. Tenant-specific gateway credentials are not supported; tenant billing uses the active country route for the tenant country. Store credentials encrypted with `IEncryptionService` and expose only safe metadata such as provider, mode, public key/merchant ID, and active state.

### Bridge Client Secrets

- Stored as BCrypt hash in `bridge_clients.client_secret_hash`
- Plaintext secret is returned ONCE at creation and never stored again
- Admins see `key_prefix` (first 8 chars) for identification only
- Treat like a password — if lost, regenerate

---

## Access Pattern in Code

`ISecretsService` reads all secrets from environment variables at application startup and caches them in memory. No scattered `Environment.GetEnvironmentVariable()` calls in business logic.

```csharp
public interface ISecretsService
{
    RsaSecurityKey GetJwtSigningKey();
    RsaSecurityKey GetJwtVerificationKey();
    byte[] GetEncryptionKey();
    string GetPasswordPepper();
}
```

Registered as singleton — reads env vars once on `Configure()`, validates all required vars are present (fail-fast at startup if missing).

---

## Local Development

Local Docker Compose uses dummy/development values only:

```
JWT_PRIVATE_KEY=<dev key generated by setup script>
ENCRYPTION_KEY=<dev key generated by setup script>
PASSWORD_PEPPER=<dev pepper>
```

A `scripts/generate-dev-secrets.sh` script generates consistent dev secrets and writes a local `.env` file (git-ignored). Dev secrets have no security value — they exist only to keep the app running locally.

---

## Rotation Schedule

| Secret | Rotation Frequency | Method |
|:-------|:-------------------|:-------|
| RSA key pair | Every 90 days | Dual-key window (zero downtime) |
| AES-256 encryption key | When compromised | Data migration required — plan carefully |
| Bridge client secrets | Per client request or on compromise | Regenerate via admin panel |
| API keys (Resend, Stripe, PayHere) | Per vendor recommendation | Update Railway env var or encrypted gateway config |

---

## Related

- [[security/auth-architecture|Auth Architecture]] — JWT signing and RSA key rotation
- [[security/data-classification|Data Classification]] — encrypted column inventory
- [[infrastructure/environment-parity|Environment Parity]] — environment comparison table
- [[modules/auth/overview|Auth Module]] — `ISecretsService` usage
- [[backend/api-conventions|API Conventions]] - first-party API authentication and device JWT rules
