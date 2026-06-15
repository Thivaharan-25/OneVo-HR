# Requests Center - End-to-End Logic

## Demo Requests

1. Super Admin opens Requests Center -> Demo Requests.
2. Page lists requester, company/tenant name, domain, requested demo access, status, requested on, and actions.
3. Super Admin opens a pending request.
4. Detail page shows requester details, company/tenant details, requested demo profile, requested access notes, and current request history.
5. Approve requires `platform.requests.manage`.
6. Approval:
   - Validates requested access against active Demo Profiles.
   - Creates or updates the demo tenant.
   - Applies the selected demo profile limits.
   - Notifies the requester.
   - Writes audit log.
7. Rejection records optional note, keeps tenant in demo/trial state or configured rejected state, notifies tenant, and writes audit log.

Paid activation is customer self-service. The customer enters company details, confirms employee count, selects an allowed plan/add-ons, receives an automatically generated first invoice based on the matching company-size range, pays, and then becomes active. That path does not enter Requests Center.

## Trial Extension Requests

1. Super Admin opens Requests Center -> Trial Extension Requests.
2. Page shows total requests, pending review, approved, near limit, and expired.
3. Table shows tenant, domain, current trial end date, status, demo profile, days remaining, requested extension, requested on, admin notes, and actions.
4. Detail page shows tenant summary, trial information, extension reason, requested days, response-by date, and current usage.
5. Approval requires approved extension days.
6. Approval updates trial end date, notifies tenant, and writes audit log.
7. Rejection keeps original trial end date, notifies tenant, and writes audit log.
