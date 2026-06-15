# Subscription Provisioning Implementation Plan

## Status

Superseded by the corrected Developer Platform model.

Use these current docs instead:

- [[developer-platform/modules/subscription-manager/overview|Subscription Plans]]
- [[developer-platform/modules/subscription-manager/end-to-end-logic|Subscription Plans - End-to-End Logic]]
- [[developer-platform/modules/module-catalog-manager/overview|Module Catalog]]
- [[developer-platform/modules/demo-profiles/overview|Demo Profiles]]
- [[developer-platform/modules/requests-center/overview|Requests Center]]
- [[modules/shared-platform/subscriptions-billing/overview|Subscriptions & Billing]]

## Current Direction

- One selected subscription plan per paid tenant.
- Plan modules are classified as base package modules or optional module add-ons.
- Resource-only add-ons increase shared storage or shared AI allowance and do not create module entitlements.
- Module Catalog provides module metadata and reference values only.
- Demo Profiles control which plans and add-ons demo tenants can upgrade into.
- Demo upgrade submit applies selected plan/add-ons in pending-payment state, generates the first invoice from the confirmed employee count/company-size bracket, resolves shared storage/AI limits, and writes audit history.
- Existing tenant subscriptions do not automatically change when catalog references or plan defaults change.
