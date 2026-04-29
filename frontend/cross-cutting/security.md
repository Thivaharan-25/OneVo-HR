# Frontend Security

## Threat Model

| Threat | Risk in ONEVO | Mitigation |
|:-------|:-------------|:-----------|
| XSS (Cross-Site Scripting) | High — HR data, salary info | CSP, React auto-escaping, DOMPurify for rich content |
| CSRF (Cross-Site Request Forgery) | Medium | SameSite cookies, CSRF token on mutations |
| Token theft | High — access to all HR data | In-memory tokens, HttpOnly refresh, short TTL |
| Clickjacking | Medium | X-Frame-Options, CSP frame-ancestors |
| Data exposure in client | High — sensitive employee data | Never cache to localStorage, clear on logout |
| Open redirect | Low | Whitelist redirect targets |
| Dependency supply chain | Medium | Lock files, audit, Snyk/Dependabot |

## Content Security Policy (CSP)

Security headers are set in two places: `vite.config.ts` for local dev, and the web server / CDN config (nginx/Azure CDN) for production.

```typescript
// vite.config.ts — dev server headers
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    headers: {
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
      'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
      'Content-Security-Policy': [
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' blob: data: https://*.blob.core.windows.net",
        "font-src 'self'",
        `connect-src 'self' ${process.env.VITE_API_URL} wss://*.signalr.net`,
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'",
      ].join('; '),
    },
  },
});
```

> **Production:** Set the same headers in your nginx config or Azure CDN rules. The CSP `connect-src` value must reference your production API domain.

## XSS Prevention

### React Auto-Escaping

React escapes all JSX expressions by default. Never bypass this:

```tsx
// ✅ Safe — React auto-escapes
<p>{employee.name}</p>

// ❌ NEVER DO THIS
<div dangerouslySetInnerHTML={{ __html: userInput }} />
```

### Rich Content Sanitization

If rich HTML must be rendered (e.g., formatted notes from a WYSIWYG editor):

```tsx
import DOMPurify from 'dompurify';

function SafeHTML({ html }: { html: string }) {
  const clean = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
  });

  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}
```

### URL Validation

```tsx
// Sanitize URLs before rendering as links
function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
}
```

## CSRF Protection

- **Refresh token** is `SameSite=Strict`, `HttpOnly`, `Secure` — immune to CSRF
- **State-changing requests** (POST, PUT, DELETE) include `X-CSRF-Token` header
- The CSRF token is obtained from a cookie set by the API and included in request headers

```tsx
// ApiClient includes CSRF token on mutations
async fetch<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getAccessToken()}`,
    'X-Correlation-Id': crypto.randomUUID(),
  };

  if (options?.method && options.method !== 'GET') {
    headers['X-CSRF-Token'] = getCsrfToken(); // Read from cookie
  }

  // ...
}
```

## Sensitive Data Handling

### Never Persist to Client Storage

```tsx
// ❌ NEVER store sensitive data in localStorage/sessionStorage
localStorage.setItem('employees', JSON.stringify(employeeData));

// ✅ Keep in TanStack Query memory cache only
// Cache is cleared on logout and page refresh
```

### Clear on Logout

```tsx
function logout() {
  // Clear ALL client-side data
  accessToken = null;
  useAuthStore.getState().clear();
  queryClient.clear();          // Wipe query cache
  signalRConnection?.stop();
  window.location.href = '/login'; // Full navigation clears JS memory
}
```

### Mask Sensitive Fields

```tsx
// SSN, salary, etc. are masked by default
function MaskedField({ value, permission }: { value: string; permission: string }) {
  const [revealed, setRevealed] = useState(false);
  const canView = useHasPermission(permission);

  if (!canView) return <span className="text-muted-foreground">***</span>;

  return (
    <div className="flex items-center gap-1">
      <span className="font-mono">{revealed ? value : '••••••'}</span>
      <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => setRevealed(!revealed)}>
        {revealed ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
      </Button>
    </div>
  );
}
```

## Open Redirect Prevention

```tsx
// Only allow redirect to internal paths
function getSafeRedirect(redirect: string | null): string {
  if (!redirect) return '/overview';
  if (redirect.startsWith('/') && !redirect.startsWith('//')) return redirect;
  return '/overview'; // Reject external URLs
}
```

## Dependency Security

- `npm audit` runs in CI on every PR
- Dependabot / Snyk for automated vulnerability alerts
- `package-lock.json` committed and reviewed
- No `*` version ranges in `package.json`

## Related

- [[frontend/cross-cutting/authentication|Authentication]] — token management, session security
- [[frontend/cross-cutting/authorization|Authorization]] — RBAC enforcement
- [[frontend/data-layer/file-handling|File Handling]] — file upload security
- [[backend/messaging/error-handling|Error Handling]] — auth error flows
