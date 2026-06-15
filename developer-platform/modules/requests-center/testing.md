# Requests Center - Testing

## Required Tests

- Demo access requests require `platform.requests.read` to view.
- Approval/rejection requires `platform.requests.manage`.
- Demo access approval validates requested access against active Demo Profiles.
- Demo access approval creates or updates the demo tenant.
- Demo access approval applies the selected demo profile limits.
- Demo upgrade submit rejects plans not allowed by Demo Profile.
- Demo upgrade submit rejects add-ons not allowed by Demo Profile.
- Demo upgrade submit hides/rejects duplicate module charges.
- Demo upgrade submit calculates shared storage and AI allowance from base plan plus selected add-ons.
- Demo upgrade submit generates the first invoice from the confirmed employee count/company-size bracket.
- Trial extension request approval updates trial end date.
- Trial extension rejection keeps original trial end date.
- Every decision writes an audit log and tenant notification.
