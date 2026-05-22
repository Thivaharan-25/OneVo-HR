# Frontend Overview

## Tech Stack

- **Framework:** Angular 21 (standalone components)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Library:** Angular Material 21

## Domain and Deployment

The Developer Platform frontend is deployed at `console.onevo.io` and is intended for **internal development and administrative use only**. This is a separate application from the main OneVo customer product and operates on its own domain.

## Design Language

The frontend uses a **dark-theme admin aesthetic** with a slate/zinc color palette. This distinct visual identity separates the Developer Platform from the main OneVo user-facing product, making it clear to administrators that they are in an internal control environment.

## Authentication Flow

The platform uses **Google OAuth 2.0** with the following user flow:

1. Unauthenticated users are redirected to `/login`
2. User initiates Google OAuth sign-in (no password auth)
3. Backend validates the Google OAuth token
4. Backend checks `dev_platform_accounts.is_active` flag in the database
5. On success, backend issues a **platform-admin JWT** with 30-minute expiry
6. User is redirected to the authenticated console at `/`
7. Angular `authGuard` enforces authentication on all protected routes

## Auth Architecture

- **OAuth Provider:** Google OAuth 2.0
- **JWT Expiry:** 30 minutes (platform-admin scoped)
- **Route Protection:** Angular functional `authGuard` on all routes except `/login`
- **Token Exchange:** Backend validates Google token → issues platform-admin JWT
- **Token Storage:** Secure Angular service (in-memory + HttpOnly cookie); never localStorage

## Relationship to Main Product

The Developer Platform is a **completely separate Angular application** with:
- Separate Angular workspace project (or standalone workspace)
- Separate domain (`console.onevo.io` vs `{tenant}.onevo.com`)
- Separate authentication system (platform-admin JWT vs product cookie session)
- Distinct visual design (dark admin theme vs main product theme)

It is **not a route or feature within the main OneVo customer Angular apps** — it is a standalone administrative console accessible only to platform admins.
