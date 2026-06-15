# Frontend Overview

## Tech Stack

- **Framework:** Angular 21 (standalone components)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Library:** Angular Material 21

## Domain and Deployment

The Developer Platform frontend is deployed at `console.onevo.io` and is intended for internal development and administrative use only. This is a separate application from the main OneVo customer product and operates on its own domain.

## Design Language

The frontend uses a dark-theme admin aesthetic with a slate/zinc color palette. This distinct visual identity separates the Developer Platform from the main OneVo user-facing product, making it clear to administrators that they are in an internal control environment.

## Authentication Flow

The platform uses email/password plus mandatory MFA:

1. Unauthenticated users are redirected to `/login`.
2. User enters email and password.
3. Backend validates account, password hash, active state, and lockout state.
4. Backend creates a pending MFA challenge; no full platform session exists yet.
5. User completes MFA at `/mfa`.
6. Backend issues a platform-admin JWT with 30-minute expiry.
7. User is redirected to the authenticated console at `/`.
8. Angular `authGuard` enforces authentication on all protected routes.

Optional Google OAuth setup/sign-in may be enabled for invited platform managers, but it must still finish with MFA before a platform-admin session is issued.

## Auth Architecture

| Concern | Rule |
|---|---|
| Primary auth | Email/password plus mandatory MFA |
| Optional OAuth | Google OAuth can be enabled for invited-manager setup/sign-in where policy allows, followed by MFA |
| JWT expiry | 30 minutes, platform-admin scoped |
| Route protection | Angular functional `authGuard` on all routes except `/login` and `/mfa` |
| Token exchange | Backend validates primary login and MFA before issuing platform-admin JWT |
| Token storage | HttpOnly cookie; never localStorage |

## Relationship to Main Product

The Developer Platform is a completely separate Angular application with:

- Separate Angular workspace project or standalone workspace
- Separate domain (`console.onevo.io` vs `{tenant}.onevo.com`)
- Separate authentication system (platform-admin JWT vs product cookie session)
- Distinct visual design (dark admin theme vs main product theme)

It is not a route or feature within the main OneVo customer Angular apps. It is a standalone administrative console accessible only to platform admins.
