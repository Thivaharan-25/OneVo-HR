# Frontend Security

## Threat Model

| Threat | Risk in ONEVO | Mitigation |
|:-------|:-------------|:-----------|
| XSS | High - HR data, salary info | CSP, React auto-escaping, DOMPurify for rich content |
| CSRF | Medium - cookie-authenticated writes | SameSite cookies, CSRF token on mutations |
| Session theft | High - access to HR data | HttpOnly Secure cookies, rotation, short idle timeout |
| Clickjacking | Medium | X-Frame-Options, CSP frame-ancestors |
| Data exposure in client | High - sensitive employee data | Never cache sensitive data to localStorage, clear on logout |
| Open redirect | Low | Whitelist redirect targets |
| Dependency supply chain | Medium | Lock files, audit, Snyk/Dependabot |

## Security Layer (`src/lib/security/`)

| File | Responsibility |
|------|---------------|
| `csrf.ts` | Reads the CSRF nonce cookie and provides the `X-CSRF-Token` header value for mutations. |
| `idle-timeout.ts` | Listens to user activity and logs out after configurable inactivity. |
| `sanitizer.ts` | DOMPurify wrapper. All user-generated HTML must pass through `sanitize(html)` before rendering. |
| `permission-guard.tsx` | `<ProtectedRoute permission="key">` checks permission metadata and redirects to `/403` if denied. |

Do not add a browser `token-manager.ts` for customer web auth. Browser JavaScript must not receive or store tenant JWTs.

## Content Security Policy (CSP)

Security headers are set in the dev server and production edge/CDN config.

```typescript
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

## XSS Prevention

React escapes JSX expressions by default. Never bypass this for untrusted content.

```tsx
// Safe
<p>{employee.name}</p>

// Unsafe unless sanitized first
<div dangerouslySetInnerHTML={{ __html: userInput }} />
```

If rich HTML must be rendered:

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

## CSRF Protection

Because customer web auth uses cookies, state-changing requests must include a CSRF header.

- Session cookie is `HttpOnly`, `Secure`, and `SameSite`.
- CSRF nonce is sent in a separate readable cookie.
- Mutations include `X-CSRF-Token`.

```tsx
async fetch<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-Correlation-Id': crypto.randomUUID(),
  };

  if (options?.method && !['GET', 'HEAD'].includes(options.method)) {
    headers['X-CSRF-Token'] = getCsrfToken();
  }

  return fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    credentials: 'include',
  });
}
```

## Sensitive Data Handling

```tsx
// Never store sensitive data in localStorage/sessionStorage
localStorage.setItem('employees', JSON.stringify(employeeData));

// Keep server data in TanStack Query memory cache only
// Cache is cleared on logout and page refresh
```

## Clear On Logout

```tsx
function logout() {
  useAuthStore.getState().clear();
  queryClient.clear();
  signalRConnection?.stop();
  window.location.href = '/login';
}
```

## Open Redirect Prevention

```tsx
function getSafeRedirect(redirect: string | null): string {
  if (!redirect) return '/overview';
  if (redirect.startsWith('/') && !redirect.startsWith('//')) return redirect;
  return '/overview';
}
```

## Related

- [[frontend/cross-cutting/authentication|Authentication]] - session handling
- [[frontend/cross-cutting/authorization|Authorization]] - RBAC enforcement
- [[frontend/data-layer/file-handling|File Handling]] - file upload security
- [[backend/messaging/error-handling|Error Handling]] - auth error flows
