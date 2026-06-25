# Frontend Security

## Threat Model

| Threat | Risk in ONEVO | Mitigation |
|:-------|:-------------|:-----------|
| XSS | High - HR data, salary info | CSP, Angular auto-escaping, `DomSanitizer` for rich content |
| CSRF | Medium - cookie-authenticated writes | SameSite cookies + `X-CSRF-Token` header on mutations |
| Session theft | High - access to HR data | HttpOnly Secure cookies, rotation, short idle timeout |
| Clickjacking | Medium | `X-Frame-Options`, CSP `frame-ancestors` |
| Data exposure in client | High - sensitive employee data | Never cache sensitive data to localStorage; clear on logout |
| Open redirect | Low | Whitelist redirect targets after login |
| Dependency supply chain | Medium | Lock files, `npm audit`, Dependabot/Snyk |

## Security Services (in `@onevo/shared`)

| Service / File | Responsibility |
|:---|:---|
| `auth.interceptor.ts` | Adds `withCredentials: true`; never attaches JWT in Authorization header for customer web |
| `csrf.interceptor.ts` | Reads CSRF nonce cookie and adds `X-CSRF-Token` header to non-GET/HEAD requests |
| `idle-timeout.service.ts` | Listens to user activity and calls `AuthService.logout()` after configurable inactivity |
| `sanitizer.service.ts` | Angular `DomSanitizer` wrapper - all user-generated HTML must pass through it before rendering |
| `auth.guard.ts` | Functional guard - redirects unauthenticated users to `/login` |
| `permission.guard.ts` | Functional guard - redirects users lacking permission to `/403` |

Do not add a browser `token-manager.ts` for customer web auth. Browser JavaScript must not receive or store tenant JWTs.

## Content Security Policy (CSP)

Security headers are set in the Angular dev proxy config and production edge/CDN config. They are **not** set in Angular code itself.

### Development (`proxy.conf.json` + Angular dev server headers)

```json
{
  "headers": {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data: https://*.r2.cloudflarestorage.com https://pub-*.r2.dev; font-src 'self'; connect-src 'self' https://api.onevo.com wss://*.signalr.net; frame-ancestors 'none'; base-uri 'self'; form-action 'self';"
  }
}
```

### Production

CSP, `X-Frame-Options`, and security headers are set at the Azure CDN / nginx edge layer, not in the Angular build output.

## XSS Prevention

Angular auto-escapes all template interpolations by default. Never bypass the sanitizer for untrusted content.

```html
<!-- [ok] Safe - Angular escapes automatically -->
<p>{{ employee.name }}</p>

<!-- [wrong] Unsafe - bypasses Angular sanitizer -->
<div [innerHTML]="userInput"></div>
```

If rich user HTML must be rendered (documents, wiki pages):

```typescript
// shared/src/lib/security/sanitizer.service.ts
@Injectable({ providedIn: 'root' })
export class SanitizerService {
  private domSanitizer = inject(DomSanitizer);

  sanitizeHtml(html: string): SafeHtml {
    // DOMPurify first, then Angular's SafeHtml
    const clean = DOMPurify.sanitize(html, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'h1', 'h2', 'h3'],
      ALLOWED_ATTR: ['href', 'target', 'rel'],
    });
    return this.domSanitizer.bypassSecurityTrustHtml(clean);
  }
}
```

```html
<!-- Usage in template -->
<div [innerHTML]="sanitizer.sanitizeHtml(document.content)"></div>
```

## CSRF Protection

Customer web auth uses cookies, so state-changing requests must include a CSRF header:

- Session cookie: `HttpOnly`, `Secure`, `SameSite=Strict`
- CSRF nonce: separate readable cookie (not HttpOnly)
- All non-GET/HEAD requests include `X-CSRF-Token` header (added by `csrfInterceptor`)

```typescript
// shared/src/lib/api/interceptors/csrf.interceptor.ts
export const csrfInterceptor: HttpInterceptorFn = (req, next) => {
  const safeMethods = ['GET', 'HEAD', 'OPTIONS'];
  if (safeMethods.includes(req.method)) return next(req);

  const csrfToken = getCsrfTokenFromCookie();
  return next(req.clone({ setHeaders: { 'X-CSRF-Token': csrfToken } }));
};

function getCsrfTokenFromCookie(): string {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith('xsrf-token='))
    ?.split('=')[1] ?? '';
}
```

## Sensitive Data Handling

```typescript
// [wrong] Never store sensitive data in localStorage / sessionStorage
localStorage.setItem('employees', JSON.stringify(employeeData));

// [ok] Keep server data in resource() / HttpClient memory only
// Data is released when the component is destroyed
// AuthService.clear() + SignalRService.disconnect() on logout
```

## Logout - Clean State

```typescript
// shared/src/lib/auth/auth.service.ts
logout(): Observable<void> {
  return this.http.post<void>('/api/v1/auth/logout', {}).pipe(
    finalize(() => {
      this.clear();                          // Clear AuthService signals
      inject(SignalRService).disconnect();   // Stop real-time connection
      inject(Router).navigate(['/login']);   // Redirect
    }),
  );
}
```

## Open Redirect Prevention

```typescript
// shared/src/lib/auth/auth.guard.ts
function getSafeRedirect(redirect: string | null): string {
  if (!redirect) return '/home';
  // Only allow relative paths; reject protocol-relative URLs
  if (redirect.startsWith('/') && !redirect.startsWith('//')) return redirect;
  return '/home';
}
```

## Idle Timeout

```typescript
// shared/src/lib/security/idle-timeout.service.ts
@Injectable({ providedIn: 'root' })
export class IdleTimeoutService implements OnDestroy {
  private auth = inject(AuthService);
  private readonly TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes
  private timer: ReturnType<typeof setTimeout> | null = null;
  private readonly events = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'];

  start() {
    this.reset();
    this.events.forEach(e => window.addEventListener(e, () => this.reset(), { passive: true }));
  }

  private reset() {
    if (this.timer) clearTimeout(this.timer);
    this.timer = setTimeout(() => firstValueFrom(this.auth.logout()), this.TIMEOUT_MS);
  }

  ngOnDestroy() {
    if (this.timer) clearTimeout(this.timer);
  }
}
```

## Related

- [[frontend/cross-cutting/authentication|Authentication]] - session handling
- [[frontend/cross-cutting/authorization|Authorization]] - RBAC enforcement
- [[frontend/data-layer/api-integration|API Integration]] - HttpClient interceptors
- [[frontend/architecture/routing|Routing]] - functional route guards
