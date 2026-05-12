# Company Registration Profile Setup

**Area:** Org Structure  
**Trigger:** Admin updates the tenant's company registration profile  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `settings:admin` (tenant-level config)

---

## Preconditions

- Tenant provisioned -> [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]
- Country data seeded in system -> [[modules/infrastructure/overview|Infrastructure]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Company Profile
- **UI:** Sidebar -> Organization -> Company Profile
- **API:** `GET /api/v1/company-profile`

### Step 2: Enter Registration Details
- **UI:** Form: registered name, registration number, country, currency, address
- **Validation:** Registration number format per country, currency is a valid ISO 4217 code

### Step 3: Configure Profile Settings
- **UI:** Currency defaults from the selected country but can be overridden. Fiscal year start month, work week, and public holidays are configured through tenant settings/calendar setup.
- **Backend:** CompanyProfileService.UpdateAsync() -> [[modules/org-structure/legal-entities/overview|Company Registration Profile]]

### Step 4: Save
- **API:** `PUT /api/v1/company-profile`
- **DB:** `company_registration_profiles` updated for the current tenant
- **Result:** Profile available for registration/compliance, payroll configuration, leave policies, and default country holiday setup
- **Calendar result:** `CompanyProfileCountrySet` seeds or updates `holiday_calendar_settings` with the selected country as the default holiday calendar and queues country holiday import.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Invalid registration number | Validation fails | "Registration number format invalid for selected country" |
| Invalid currency | Validation fails | "Currency is not supported" |

## Events Triggered

- `CompanyProfileCountrySet` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]
- [[Userflow/Payroll/payroll-provider-setup|Payroll Provider Setup]]
- [[Userflow/Leave/leave-policy-setup|Leave Policy Setup]]
- [[Userflow/Calendar/calendar-integrations|Calendar Integrations]]

## Module References

- [[modules/org-structure/legal-entities/overview|Company Registration Profile]]
- [[modules/org-structure/overview|Org Structure]]
