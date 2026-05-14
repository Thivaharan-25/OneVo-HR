# Tech Stack KB Upgrade

**Date:** 2026-05-13
**Type:** docs

## Changed

- Earlier in the day this KB attempted to move source-of-truth documents from .NET 9 / C# 13 to .NET 10 / C# 14.
- Current correction: source-of-truth documents must describe .NET 9 / C# 13 as implemented and .NET 10 / C# 14 only as a future migration target until the backend `.csproj` files move to `net10.0`.
- Set database guidance to PostgreSQL 16.13 baseline with PostgreSQL 18 as the target only after hosting, backup/restore, migration, RLS, partitioning, and performance validation.
- Corrected package guidance in the active tech stack to match currently implemented package versions where verified from `.csproj` files.
- Kept WorkPulse agent upgrade as a separate validation track because .NET MAUI/device behavior needs real Windows testing before the agent runtime is declared fully upgraded.

## Not Changed

- Historical superpowers planning documents were left intact because they record past plans, not current source-of-truth architecture.
