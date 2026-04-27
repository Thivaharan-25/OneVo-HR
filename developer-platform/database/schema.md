# Developer Platform Database Schema

## Overview

The OneVo Developer Platform introduces a dedicated database schema to manage platform accounts, authentication sessions, agent version releases, and deployment ring assignments. This schema enables:

- **Multi-tenant admin isolation**: Developer platform accounts (super_admin, admin, viewer roles) operate independently from tenant-facing systems
- **Agent release management**: Semantic versioning, release channels (stable/beta/recalled), and OS compatibility tracking
- **Gradual rollout capabilities**: Deployment rings (Internal, Beta, GA) allow controlled agent version distribution across tenants
- **Session security**: OAuth-based authentication with token management and IP tracking
- **API access control**: Platform API key provisioning with scope-based permissions and expiration

**Phase 1** adds 5 core tables for accounts, sessions, releases, and ring management, plus the `global_app_catalog` table in the SharedPlatform schema managed by the App Catalog Manager module. **Phase 2** adds the platform_api_keys table for programmatic access.

---

## DbContext Ownership (ADR-001)

> **DbContext:** `ApplicationDbContext` in `ONEVO.Infrastructure/Persistence/`. DevPlatform entities (`DevPlatformAccount`, `DevPlatformSession`, `AgentVersionRelease`, `AgentDeploymentRing`, `AgentDeploymentRingAssignment`) are configured in `ONEVO.Infrastructure/Persistence/Configurations/DevPlatform/`. These entities have **no TenantId** and are excluded from the global tenant query filter.

Per [ADR-001](../../decisions/ADR-001-per-module-database-and-event-bus.md), all developer platform tables are mapped by the unified `ApplicationDbContext`. EF migrations live in `ONEVO.Infrastructure/Persistence/Migrations/` and are run as part of the standard application startup.

Cross-module data access (e.g., reading `tenants`) goes through the existing module's public service interface via DI — never by querying the DbContext directly across module boundaries.

---

## Schema Catalog Impact

| Phase | Change | Table Count |
|-------|--------|------------|
| Current | Baseline | 170 |
| Phase 1 | +5 DevPlatform tables + `global_app_catalog` (SharedPlatform) + `observed_applications` (Configuration) + 3 columns on `app_allowlists` | 177 |
| Phase 2 | +1 new table (`platform_api_keys`) | 178 |

> **Note on ownership:** `global_app_catalog` is owned by `SharedPlatformDbContext` and `observed_applications` by `ConfigurationDbContext`. They are not in `DevPlatformDbContext`. The dev console manages them through `IGlobalAppCatalogService` and `IObservedApplicationReader` interfaces respectively.

---

## Phase 1 Tables

### dev_platform_accounts

Administrative accounts for the developer platform. Supports OAuth (Google Sign-In) and role-based access control.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| email | varchar(255) | UNIQUE, NOT NULL |
| full_name | varchar(255) | NOT NULL |
| google_sub | varchar(255) | Google OAuth subject identifier, nullable |
| role | varchar(30) | NOT NULL; enum: `'super_admin'` \| `'admin'` \| `'viewer'` |
| is_active | boolean | Default: true; controls login permission |
| created_at | timestamptz | NOT NULL; creation timestamp |
| last_login_at | timestamptz | Nullable; tracks last successful authentication |

**Indexes**: `UNIQUE(email)`, `btree(role)`, `btree(is_active)`

---

### dev_platform_sessions

Authenticated sessions for dev platform accounts. One session per login or API token grant.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| account_id | uuid | FOREIGN KEY → dev_platform_accounts(id), NOT NULL |
| token_hash | varchar(64) | SHA256 hash of session token, NOT NULL |
| created_at | timestamptz | NOT NULL |
| expires_at | timestamptz | NOT NULL; session TTL |
| ip_address | varchar(45) | Nullable; IPv4 or IPv6, for audit/security |

**Indexes**: `btree(account_id)`, `btree(expires_at)`

**Notes**: Tokens are hashed; original token never stored. Expired sessions are soft-deleted or archived for audit.

---

### agent_version_releases

Agent binary releases with version metadata, channels, and OS requirements.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| version | varchar(20) | NOT NULL; semver format (e.g., `'1.4.2'`) |
| release_channel | varchar(20) | NOT NULL; enum: `'stable'` \| `'beta'` \| `'recalled'` |
| min_os_version | varchar(20) | Nullable; minimum OS version required (e.g., `'10.0.26000'` for Windows) |
| release_notes | text | Nullable; markdown-formatted changelog |
| download_url | varchar(500) | NOT NULL; CDN or S3 URL to agent binary |
| published_by_id | uuid | FOREIGN KEY → dev_platform_accounts(id), NOT NULL |
| published_at | timestamptz | NOT NULL; release publication time |
| recalled_at | timestamptz | Nullable; if set, version is marked as recalled/unsafe |

**Indexes**: `btree(version, release_channel)`, `btree(release_channel)`, `btree(published_at DESC)`

**Notes**: Recalled releases remain in schema for audit but are excluded from deployment eligibility queries.

---

### agent_deployment_rings

Deployment rings for phased agent rollouts. Defines the rollout strategy tiers.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| ring_number | int | NOT NULL; enum: `0` (Internal) \| `1` (Beta) \| `2` (GA) |
| name | varchar(50) | NOT NULL; human-readable ring name (`'Internal'` \| `'Beta'` \| `'GA'`) |
| description | text | Nullable; explains ring purpose and rollout scope |

**Indexes**: `UNIQUE(ring_number)`, `btree(name)`

**Notes**: Immutable reference data. Three rings provide a standard phased rollout pattern.

---

### agent_deployment_ring_assignments

Maps tenants to deployment rings, controlling which agent versions they receive.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| tenant_id | uuid | FOREIGN KEY → tenants(id), NOT NULL |
| ring_id | uuid | FOREIGN KEY → agent_deployment_rings(id), NOT NULL |
| assigned_by_id | uuid | FOREIGN KEY → dev_platform_accounts(id), NOT NULL |
| assigned_at | timestamptz | NOT NULL; assignment timestamp for audit |

**Indexes**: `UNIQUE(tenant_id, ring_id)`, `btree(ring_id)`, `btree(assigned_by_id)`

**Notes**: A tenant can belong to only one ring at a time (enforced by unique constraint). Ensures consistent version delivery within a ring cohort.

---

## Phase 2 Table

### platform_api_keys

API keys for programmatic access to the developer platform admin API. Supports revocation and expiration.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| key_hash | varchar(64) | SHA256 hash of the API key, NOT NULL, UNIQUE |
| name | varchar(100) | NOT NULL; human-readable label for key management |
| scopes | text[] | Array of permission scopes; e.g., `ARRAY['agent:read', 'deployment:write']` |
| created_by_id | uuid | FOREIGN KEY → dev_platform_accounts(id), NOT NULL |
| expires_at | timestamptz | Nullable; if set, key becomes invalid after this time |
| revoked_at | timestamptz | Nullable; if set, key is revoked and unusable |
| created_at | timestamptz | NOT NULL; key creation time |

**Indexes**: `UNIQUE(key_hash)`, `btree(created_by_id)`, `btree(expires_at)`, `btree(revoked_at)`

**Notes**: Keys are hashed on storage; original key is shown only once at creation. Revoked and expired keys are excluded from validation queries.

---

## Existing Table Changes

### tenants.status Enum Update

The `tenants.status` column enum is expanded to include a `'provisioning'` state alongside existing `'active'` and `'suspended'` values.

| Status | Meaning | Visibility |
|--------|---------|------------|
| `active` | Production-ready tenant | Visible in all tenant-facing and admin queries |
| `suspended` | Temporarily disabled | Excluded from tenant-facing queries; visible only in admin API |
| `provisioning` | Onboarding in progress | Excluded from all tenant-facing queries; visible only in admin API for platform managers |

**Visibility Rule**: Tenants in `provisioning` status are excluded from:
- Multi-tenant admin API queries by default (must explicitly filter to include)
- Tenant-facing application queries
- Standard analytics and reporting

Provisioning tenants are only visible to developer platform super_admin and admin accounts via explicit admin API calls, ensuring clean separation during onboarding workflows.

---

## Security & Access Control

- **OAuth Integration**: dev_platform_accounts authenticate via Google OAuth; tokens are hashed in dev_platform_sessions
- **Role-Based Access**: Three roles (super_admin, admin, viewer) control API endpoint access
- **API Key Hashing**: platform_api_keys stores SHA256 hashes; plaintext keys never persisted
- **Audit Trail**: All admin actions (published_by_id, assigned_by_id, created_by_id) track who made changes
- **Tenant Isolation**: dev_platform_* tables are isolated from tenant_facing_* schema; cross-tenant queries are forbidden
