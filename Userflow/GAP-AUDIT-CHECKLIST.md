# Userflow Gap Audit Checklist

**Purpose:** Use this checklist when reviewing any existing flow or writing a new one. It ensures no common path type is missed. Based on 6 gap categories that cover the most frequently forgotten user journeys.

---

## How to Use

1. Open the flow file you want to audit
2. Walk through each category below
3. For each item, check if the flow already documents it
4. If missing and relevant, add it to the flow's **Variations** or **Error Scenarios** section
5. Mark N/A if the category genuinely doesn't apply to this flow

---

## Category 1: Error & Failure Paths

Every flow should document what happens when things go wrong — not just the happy path.

- [ ] **Validation failure** — What does the user see when input is invalid?
- [ ] **Permission denied** — What happens if the user lacks the required permission?
- [ ] **Dependency unavailable** — What if a downstream service/module is down?
- [ ] **Duplicate/conflict** — What if the action conflicts with existing data?
- [ ] **Timeout/network failure** — What does the user experience during connectivity issues?
- [ ] **Concurrent edit** — What if two users modify the same record simultaneously?

---

## Category 2: Undo & Reversal Paths

Can the user reverse or correct what they just did?

- [ ] **Cancel before completion** — Can the user abandon mid-flow? What state is left behind?
- [ ] **Undo after submission** — Can the user retract a submitted action (e.g., cancel leave request)?
- [ ] **Edit after save** — Can the user modify a saved-but-not-finalized record?
- [ ] **Admin override/reversal** — Can an admin reverse a completed action on behalf of someone?
- [ ] **Cascade reversal** — If this action triggered downstream events, what gets reversed when undone?

---

## Category 3: Admin Override & Bypass

Admins often need to act outside the normal flow.

- [ ] **Act on behalf** — Can an admin perform this action for another employee?
- [ ] **Skip approval** — Can an admin bypass the normal approval workflow?
- [ ] **Backdate** — Can this action be applied retroactively (past dates)?
- [ ] **Bulk action** — Can this be done for multiple employees at once?
- [ ] **Override validation** — Can an admin override system validation rules (e.g., exceed leave balance)?

---

## Category 4: First-Time & Empty State

What does the user see before any data exists?

- [ ] **Empty state** — What does the page/screen look like with zero records?
- [ ] **First-time setup prompt** — Does the system guide the user through initial configuration?
- [ ] **Missing prerequisite** — What if a dependency hasn't been configured yet (e.g., no leave types exist)?
- [ ] **Onboarding tooltip/guide** — Is there contextual help for first-time users of this feature?

---

## Category 5: Cross-Module Impact

Does this flow affect or depend on other modules?

- [ ] **Events published** — What events does this flow emit? Who consumes them?
- [ ] **Events consumed** — Does this flow react to events from other modules?
- [ ] **Data dependency** — Does this flow read data from another module (e.g., leave reads calendar holidays)?
- [ ] **Approval routing** — Does this flow use the workflow engine for approvals?
- [ ] **Notification triggers** — What notifications are sent, to whom, via which channels?
- [ ] **Audit trail** — Is this action logged for compliance/audit purposes?

If the cross-module impact is significant (3+ modules), consider creating a Cross-Module scenario doc (see `Userflow/Cross-Module/` folder).

---

## Category 6: Passive & Background Flows

Not all flows are user-initiated. What happens automatically?

- [ ] **Scheduled jobs** — Does anything run on a schedule related to this feature (e.g., leave accrual, payroll run)?
- [ ] **Auto-expiry** — Do records expire or auto-close after a period (e.g., pending requests auto-rejected after 30 days)?
- [ ] **Threshold triggers** — Does the system act when a threshold is reached (e.g., leave balance hits 0)?
- [ ] **Digest/summary notifications** — Are periodic summaries sent (e.g., weekly attendance summary)?
- [ ] **Data retention** — Is data automatically archived or deleted per retention policy?

---

## Quick Reference: Trigger Type Taxonomy

When documenting the **Trigger** field in a flow, use one of these categories:

| Trigger Type | Description | Example |
|:-------------|:------------|:--------|
| **User action** | User explicitly initiates | Employee clicks "New Request" |
| **Reaction** | Triggered by another flow/event | Manager gets approval notification |
| **Scheduled** | Runs on a time schedule | Monthly payroll run |
| **System-triggered** | System detects a condition | Exception engine flags anomaly |
| **Configuration** | Admin sets up system rules | Leave type creation |
| **Self-service** | User manages own profile/settings | Employee updates profile |
| **View only** | User reads data, no state change | Employee views leave balance |
| **First-time setup** | One-time initial configuration | Tenant provisioning |
| **Error recovery** | Correcting a previous mistake | Payroll adjustment |
| **Cascade/chain** | Automatic downstream reaction | Leave approval updates calendar + attendance |

---

*Use this checklist during flow creation, sprint reviews, or periodic audits. Not every item applies to every flow — use judgment.*
