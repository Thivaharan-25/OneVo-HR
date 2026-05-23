# Tech Stack KB Upgrade

**Date:** 2026-05-13
**Type:** docs

## Changed

- Updated all source-of-truth documents to reflect .NET 10 / C# 14 as the current backend runtime.
- Set database guidance to PostgreSQL 16.13 baseline with PostgreSQL 18 as the target only after hosting, backup/restore, migration, RLS, partitioning, and performance validation.
- Corrected package guidance in the active tech stack to match currently implemented package versions where verified from `.csproj` files.
- Kept WorkPulse agent upgrade as a separate validation track because .NET MAUI/device behavior needs real Windows testing before the agent runtime is declared fully upgraded.

## Not Changed

- Historical superpowers planning documents were left intact because they record past plans, not current source-of-truth architecture.
