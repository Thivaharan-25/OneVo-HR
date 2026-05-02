# Integration Connection

**Area:** Configuration -> Integrations  
**Trigger:** Admin connects or updates an external integration  
**Required Permission(s):** `settings:admin`  
**Related Permissions:** `integrations:manage`

---

## Preconditions

- Tenant is active -> [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]
- Required permissions are assigned -> [[Userflow/Auth-Access/permission-assignment|Permission Assignment]]
- Target integration is enabled for the tenant package or feature flags

## Flow Steps

### Step 1: Open Integrations
- **UI:** Settings -> Integrations
- **API:** `GET /api/v1/configuration/integrations`
- **UI:** Shows available connectors, connection status, last sync, and required permissions

### Step 2: Select Integration
- **UI:** Admin opens a connector card such as PeopleHR, Microsoft Teams, GitHub, payroll provider, or SSO-related provider
- **Backend:** Checks module entitlement and tenant feature flags

### Step 3: Enter Credentials or Start OAuth
- **API Credentials:** Admin enters API key/client details; sensitive values are masked after save
- **OAuth:** Admin starts provider authorization and returns through callback
- **Security:** Secrets are encrypted before storage

### Step 4: Test Connection
- **API:** `POST /api/v1/configuration/integrations/{id}/test`
- **Backend:** Validates credentials and required scopes
- **UI:** Shows success, missing scope, invalid credentials, or provider unavailable

### Step 5: Save Connection
- **API:** `PUT /api/v1/configuration/integrations/{id}`
- **DB:** `integration_connections`
- **Result:** Integration becomes available to the owning module

### Step 6: Monitor Sync Health
- **UI:** Integration card shows connected/disconnected/error state, last sync time, and retry action
- **Backend:** Sync jobs publish status updates and audit events

## Variations

### OAuth Provider
- Admin is redirected to the provider
- Callback exchanges code for token
- Token metadata is saved without exposing raw token values in UI

### API-Key Provider
- Admin enters a key or secret directly
- UI only reveals masked value after save
- Rotation flow replaces the encrypted credential

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Feature not entitled | Save blocked | "This integration is not enabled for your plan" |
| Invalid credentials | Test fails | "Connection failed. Check credentials." |
| Missing provider scope | Test fails with scope list | Missing permission/scopes message |
| Provider unavailable | Test can be retried | "Provider is temporarily unavailable" |
| Secret rotation fails | Existing connection remains active | "Could not update credentials" |

## Events Triggered

- `IntegrationConnected`
- `IntegrationConnectionUpdated`
- `IntegrationConnectionFailed`

## Related Flows

- [[Userflow/Data-Import/data-import-wizard|Data Import Wizard]]
- [[Userflow/Platform-Setup/sso-configuration|SSO Configuration]]
- [[Userflow/Work-Management/workspace-teams-sync|Workspace Teams Sync]]
- [[Userflow/Work-Management/integration-automation-flow|WorkSync Integration Automation]]

## Module References

- [[modules/configuration/integrations/overview|Integrations]]
- [[modules/configuration/overview|Configuration]]
- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]
