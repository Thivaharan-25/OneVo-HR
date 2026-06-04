# Device Management Userflow

> Phase 2 only. This flow is absent from Phase 1 navigation and API scope.

## Actor

Operations or support user with device permissions.

## Journey

1. Operator opens System Operations -> Device Management.
2. Console lists devices across tenants.
3. Operator filters by tenant, status, version, OS, or check-in age.
4. Operator opens device detail.
5. If permitted, operator queues an approved agent command with reason.

## APIs Used

- `GET /admin/v1/operations/devices`
- `GET /admin/v1/operations/devices/{deviceId}`
- `POST /admin/v1/operations/devices/{deviceId}/commands`
