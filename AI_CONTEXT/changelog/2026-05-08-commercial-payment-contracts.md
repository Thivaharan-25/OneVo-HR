# 2026-05-08 - Commercial Payment Contracts

## Changed

- Updated Developer Platform admin API contracts to make payment collection explicit.
- Normal subscription tenants now use gateway collection for recurring SaaS fees.
- Full-license tenants can record the one-time license sale manually with amount, paid date, and invoice/reference.
- Full-license maintenance/support is a separate recurring commercial item and normally uses gateway collection.
- Updated shared platform schema notes and Dev 1 acceptance criteria to match the contract.

## Decision

The commercial model is not just `stripe_managed` true/false. The backend contract must separately track:

- subscription recurring collection mode,
- one-time full-license payment mode and evidence,
- recurring maintenance collection mode,
- payment gateway references.
