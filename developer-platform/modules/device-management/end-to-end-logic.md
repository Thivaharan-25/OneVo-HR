# Device Management End-to-End Logic

## View Devices

1. Operator opens System Operations -> Device Management.
2. Frontend calls `GET /admin/v1/operations/devices`.
3. Backend verifies `platform.devices.read`.
4. Backend returns cross-tenant device metadata.
5. Operator filters by tenant, health, version, OS, or last check-in.

## Queue Device Command

1. Operator opens device detail.
2. Operator selects approved command.
3. Frontend calls `POST /admin/v1/operations/devices/{deviceId}/commands`.
4. Backend verifies `platform.devices.manage`.
5. Backend writes through Agent Gateway command service and audits the action.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/operations/devices` | Device list | `platform.devices.read` |
| GET | `/admin/v1/operations/devices/{deviceId}` | Device detail | `platform.devices.read` |
| POST | `/admin/v1/operations/devices/{deviceId}/commands` | Queue approved command | `platform.devices.manage` |

## Command Rules

- Command types must be allowlisted.
- Commands must include tenant/device context and operator reason.
- Commands cannot bypass tenant entitlement or agent install policy.
