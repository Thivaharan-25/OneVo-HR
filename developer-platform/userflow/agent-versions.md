# Agent Version and Ring Management Flows

## Purpose

The Agent Version Manager controls which version of the OneVo desktop agent is deployed to tenants, how versions roll out across deployment rings, and how to respond to a bad release.

---

## Deployment Rings

Rings control rollout scope. Every tenant is assigned to exactly one ring.

| Ring | Name | Who is in it |
|---|---|---|
| Ring 0 | Internal | OneVo's own internal test tenants |
| Ring 1 | Beta | Opted-in customer tenants who accept early releases |
| Ring 2 | GA | All remaining tenants — general availability |

A force-update command pushes a new version to all agents in a given ring. Normal (non-forced) upgrades are pulled by agents on their own update check cycle.

---

## 1. Version Catalog View

**Path:** `/agents/versions`

Lists all published agent versions from `agent_version_releases`. Each row shows:
- Version number (semver)
- Release channel: `stable` | `beta` | `recalled`
- Release notes (truncated; click row for full notes)
- Minimum OS version
- Published by (developer account name)
- Published date
- Recalled date (if applicable)

**Filter:** by channel, by date range.

**API:** `GET /admin/v1/agent-versions`

---

## 2. Publish a New Version

**Minimum role:** admin

1. Navigate to `/agents/versions`
2. Click **Publish Version**
3. Fill in the form:
   - Version number (semver, e.g. `1.5.0`) — validated for uniqueness
   - Release channel (`stable` or `beta`)
   - Minimum OS version
   - Release notes (markdown supported)
   - Download URL (HTTPS, points to signed binary)
4. Click **Publish**
5. **API call:** `POST /admin/v1/agent-versions` with body `{ "version": "...", "release_channel": "...", "min_os_version": "...", "release_notes": "...", "download_url": "..." }`
6. The new version appears at the top of the catalog
7. Toast: "Version published"

A newly published version does not automatically push to any ring. Push is a separate, deliberate action (see Force-Update below).

---

## 3. Force-Update a Ring

**Minimum role:** super_admin

Force-update sends an `UPDATE_AGENT` command to every agent currently in the specified ring via AgentGateway. Agents receive the command on their next connection and begin updating.

1. Navigate to `/agents/versions`
2. Click the version row you want to push
3. Click **Force Update Ring**
4. Select the target ring (Ring 0, 1, or 2) from the dropdown
5. `ConfirmActionDialog` appears: "Force-update Ring `<n>` (`<name>`) to version `<version>`? This will push an update command to all `<N>` agents in this ring."
6. Click **Confirm**
7. **API call:** `POST /admin/v1/agent-versions/{id}/force-update` with body `{ "ring": 0 | 1 | 2 }`
8. Toast: "Update command dispatched to Ring `<n>`"

The command is published to all agents in the ring via AgentGateway. Agents that are offline will receive it on next reconnect.

**Typical rollout sequence:** publish → force Ring 0 → verify → force Ring 1 → verify → force Ring 2.

---

## 4. Ring Assignment (Moving Tenants Between Rings)

**Minimum role:** admin

A tenant's ring determines which force-update commands affect their agents.

### View Ring Assignments

**Path:** `/agents/rings`

Shows each ring with the list of tenants assigned to it.

**API:** `GET /admin/v1/agent-rings`

### Move a Tenant to a Different Ring

**From the ring view:**

1. Navigate to `/agents/rings`
2. Find the tenant in their current ring
3. Click **Reassign** next to the tenant
4. Select the new ring from the dropdown
5. Click **Confirm**
6. **API call:** `PUT /admin/v1/tenants/{id}/agent-ring` with body `{ "ring": 0 | 1 | 2 }`
7. Toast: "Tenant assigned to Ring `<n>`"

**From the tenant detail page:**

1. Navigate to `/tenants/{id}` → **Overview** tab
2. Current ring is shown in the agent section
3. Click **Change Ring** → same dropdown and confirm flow as above

---

## 5. Rollback

**Minimum role:** super_admin

Rollback force-pins a tenant's agents to a previous stable version, overriding the ring's current version target.

**When to use:** a tenant's agents have updated to a version with a known issue. Force-pinning them to the previous stable version immediately pushes a downgrade command via AgentGateway.

**Steps:**

1. Navigate to `/tenants/{id}` → **Overview** tab → agent section
2. Click **Rollback Agent Version**
3. A dropdown of previous `stable`-channel versions appears
4. Select the target version
5. `ConfirmActionDialog`: "Force-pin `<tenant>` to version `<version>`? Their agents will receive a downgrade command."
6. Click **Confirm**
7. **API call:** `POST /admin/v1/agent-versions/{id}/force-update` with body `{ "ring": <tenant's current ring> }` targeting the selected older version, or use channel change to `recalled` on the bad version followed by force-update with the prior version — whichever applies.
8. Toast: "Rollback command dispatched"

**For platform-wide rollback** (bad version reached Ring 2):

1. Go to `/agents/versions` → click the bad version
2. Click **Change Channel** → set to `recalled`
   - **API call:** `PATCH /admin/v1/agent-versions/{id}/channel` with body `{ "channel": "recalled" }`
3. Force-update all three rings to the last known-good stable version (repeat the Force-Update flow three times, Ring 0 → 1 → 2)

Recalled versions are flagged in the catalog with a red **"Recalled"** badge and are excluded from all future force-update selections.
