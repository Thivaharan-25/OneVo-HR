# Documents - Schema

**Module:** [[modules/documents/overview|Documents]]
**Phase:** Phase 2 HR-specific additions
**Tables:** 4

> Work Management.Collaboration owns the Phase 1 `documents` and `document_versions` core because Work Management requires project/wiki/task document behavior. HR Documents adds the HR-specific governance tables below. Do not build a separate Work Management document store or a second `documents`/`document_versions` definition here.

---

## `document_access_logs`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `document_version_id` | `uuid` | FK -> document_versions |
| `employee_id` | `uuid` | FK -> employees |
| `action` | `varchar(20)` | `view`, `download`, `print` |
| `accessed_at` | `timestamptz` | |
| `ip_address` | `varchar(45)` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `document_version_id` -> [[database/schemas/wms-collaboration#`document_versions`|document_versions]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `document_acknowledgements`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `document_version_id` | `uuid` | FK -> document_versions |
| `employee_id` | `uuid` | FK -> employees |
| `acknowledged_by_id` | `uuid` | FK -> users (may differ from employee if acknowledged on behalf) |
| `method` | `varchar(20)` | `click`, `e_signature` |
| `acknowledged_at` | `timestamptz` | |
| `ip_address` | `varchar(45)` | IPv4/IPv6 for audit |

**Foreign Keys:** `document_version_id` -> [[database/schemas/wms-collaboration#`document_versions`|document_versions]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `acknowledged_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `document_categories`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `parent_category_id` | `uuid` | FK -> document_categories (nullable; null for root) |
| `name` | `varchar(100)` | |
| `applies_to` | `varchar(30)` | `company`, `department`, `employee` |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `parent_category_id` -> [[#`document_categories`|document_categories]]

---

## `document_templates`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(100)` | |
| `category_id` | `uuid` | FK -> document_categories (nullable) |
| `template_content` | `text` | HTML/Markdown template body |
| `variables_json` | `jsonb` | Available merge variables, e.g. `{{employee_name}}` |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `category_id` -> [[#`document_categories`|document_categories]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## Related

- [[modules/documents/overview|Documents Module]]
- [[database/schemas/wms-collaboration|Work Management Collaboration Schema]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
