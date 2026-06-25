# Tenant Branding

## What's Customizable

Each tenant can override a subset of the design system to match their brand:

| Token | Default | Customizable | Applied Via |
|:------|:--------|:-------------|:------------|
| Primary color | Violet Electric (`263.4 70% 50.4%`) | Yes | CSS variable override |
| Primary foreground | White | Yes (auto-calculated) | CSS variable override |
| Accent color | Derived from primary | Yes | CSS variable override |
| Company logo | ONEVO logo | Yes | `<img>` src from tenant config |
| Company name | "ONEVO" | Yes | Text in sidebar header |
| Favicon | ONEVO favicon | Yes | Dynamic `<link>` in head |
| Login background | Default gradient | Yes | CSS variable or image URL |

**Not customizable:** status colors, severity colors, typography, spacing, component structure. These ensure UX consistency across all tenants.

### Additional Customizable Properties

| Property | Default | Scope |
|:---------|:--------|:------|
| Default theme | `system` | Tenant can set `dark` or `light` as default (user override still applies) |
| Glass opacity | `0.85` | Tenant can adjust glass surface opacity |
| Accent glow intensity | `0.15` | Tenant can adjust violet glow intensity |

## Architecture

### Tenant Config API

```typescript
interface TenantBranding {
  primaryColor: string;       // HSL: "263.4 70% 50.4%"
  accentColor?: string;       // HSL or null (auto-derive)
  logoUrl: string;            // URL to tenant logo
  logoDarkUrl?: string;       // Dark mode variant
  faviconUrl?: string;        // Custom favicon
  companyName: string;        // Display name
  loginBackgroundUrl?: string; // Custom login page background
}
```

### CSS Variable Injection

Applied once on app load, before first paint:

```typescript
// shared/services/branding.service.ts
@Injectable({ providedIn: 'root' })
export class BrandingService {
  private readonly branding = signal<TenantBranding | null>(null);

  readonly companyName = computed(() => this.branding()?.companyName ?? 'ONEVO');
  readonly logoUrl = computed(() => this.branding()?.logoUrl ?? '');

  constructor() {
    effect(() => {
      const b = this.branding();
      if (!b) return;
      const root = document.documentElement;
      if (b.primaryColor) {
        root.style.setProperty('--primary', b.primaryColor);
        root.style.setProperty('--ring', b.primaryColor);
        root.style.setProperty('--primary-foreground', getContrastColor(b.primaryColor));
      }
      if (b.accentColor) {
        root.style.setProperty('--accent', b.accentColor);
      }
    });
  }

  apply(branding: TenantBranding): void {
    this.branding.set(branding);
  }
}
```

### Logo Rendering

```typescript
// shared/components/tenant-logo/tenant-logo.component.ts
@Component({
  selector: 'app-tenant-logo',
  standalone: true,
  template: `
    <img [src]="logoSrc()" [alt]="branding.companyName()"
         class="h-8 w-auto object-contain" loading="eager" />
  `,
})
export class TenantLogoComponent {
  protected readonly branding = inject(BrandingService);
  private readonly theme = inject(ThemeService);

  protected readonly logoSrc = computed(() =>
    this.theme.current() === 'dark' && this.branding.logoDarkUrl()
      ? this.branding.logoDarkUrl()
      : this.branding.logoUrl()
  );
}
```

## Contrast Safety

When tenants pick custom primary colors, the system must ensure text remains readable:

```typescript
function getContrastColor(hslColor: string): string {
  const lightness = parseFloat(hslColor.split(' ')[2]);
  // If primary is light (>60% lightness), use dark text
  return lightness > 60 ? '222.2 84% 4.9%' : '210 40% 98%';
}
```

Additionally, the branding settings UI shows a live preview with contrast ratio check (WCAG AA >= 4.5:1).

## Related

- [[frontend/design-system/theming/dark-mode|Dark Mode]] - theme system
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] - base color tokens
- [[frontend/cross-cutting/authentication|Authentication]] - login page branding
