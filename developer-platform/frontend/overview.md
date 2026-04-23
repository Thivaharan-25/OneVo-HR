# Frontend Overview

## Tech Stack

- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Library:** shadcn/ui

## Domain and Deployment

The Developer Platform frontend is deployed at `console.onevo.io` and is intended for **internal development and administrative use only**. This is a separate application from the main OneVo product and operates on its own domain during development.

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
7. The `middleware.ts` enforces authentication on all protected routes

## Auth Architecture

- **OAuth Provider:** Google OAuth 2.0
- **JWT Expiry:** 30 minutes (platform-admin scoped)
- **Middleware Protection:** All routes except `/login` require valid authentication
- **Token Exchange:** Backend validates Google token → issues platform-admin JWT

## Relationship to Main Product

The Developer Platform is a **completely separate Next.js application** with:
- Separate code repository (or monorepo workspace)
- Separate domain (`console.onevo.io` vs main product domain)
- Separate authentication system (platform-admin JWT vs product JWT)
- Distinct visual design (dark admin theme vs main product theme)

It is **not a route or feature within the main OneVo frontend** — it is a standalone administrative console accessible only to platform admins.
