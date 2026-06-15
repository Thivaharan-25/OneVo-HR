# Requests Center

## Purpose

Requests Center is the Super Admin queue for demo/trial requests that require platform-side review. Paid activation is not approved here; customers self-activate by entering company details, confirming employee count, selecting an allowed plan/add-ons, receiving the first invoice, and paying it.

## Tabs

| Tab | Purpose |
|---|---|
| Demo Requests | Review requests for demo/trial access |
| Trial Extension Requests | Review demo tenants requesting additional trial days |

## Permissions

| Action | Permission |
|---|---|
| View requests | `platform.requests.read` |
| Approve/reject demo access or trial extension | `platform.requests.manage` |

Customer Support is a separate sidebar item and module. It may link to a tenant request context, but support tickets are not a Requests Center tab.
