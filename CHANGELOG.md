# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — feature/advanced-filters → main

### Added
- **Backend (FastAPI + SQLAlchemy async)**
  - `AccommodationService` with Redis caching and configurable 2 000-record threshold enforced at the SQL `LIMIT` level
  - Alembic migration `001_initial_schema.py` — `accommodations` table with full-text-searchable destination column
  - Pydantic schemas with `model_validator` enforcing `check_out > check_in`
  - slowapi rate limiter (60 req/min) with trusted-proxy-aware `_real_client_ip()` key function
  - CORS middleware and `asynccontextmanager` lifespan (replaces deprecated `@on_event`)
  - `app/limiter.py` module to break circular-import between `main.py` and router
  - `scripts/seed.py` (2 000 synthetic records) and `scripts/refresh_review_scores.py` (nightly cron)
  - 8 pytest tests across router (5) and service (3) layers
  - `.dockerignore` to prevent `.env` leaking into Docker image layers
  - `requirements.txt` with pinned versions including `aiosqlite` for SQLite test driver

- **Frontend (Next.js + Tailwind + Zustand)**
  - `FilterEngine` — pure TypeScript AND/OR/threshold filter logic, zero React dependency
  - `FilterPanel` — desktop sidebar + mobile drawer with responsive breakpoint
  - `ResultsList` — virtualisable card grid with skeleton loading state
  - `ActiveFilterBadges` — pill row with per-filter dismiss and "clear all"
  - `SearchPage` — wires all components; live filtering on every store change
  - Zustand `filterStore` with `selectActiveFilterCount` selector
  - `lib/api.ts` typed fetch wrapper for the backend `/accommodations` endpoint
  - 7 Vitest unit tests for `filterEngine.ts`

- **Infrastructure**
  - `docker-compose.yml` — PostgreSQL 16 + Redis 7 with loopback-only port bindings and env-var passwords
  - `install.cmd` — one-shot Windows dev-environment bootstrap script

- **Documentation**
  - `requirements.md`, `architecture.md`, `design-review.md`, `impl-plan.md`

### Fixed
- Auth-bypass: XFF header now walked right-to-left; leftmost spoofable entry no longer used as rate-limit key (`43b554f`)
- `None` falsy guard in `AccommodationService` — `0.0` score/price no longer serialised as `null` (`c895864`)
- `ValidationError` raised inside `Depends()` now returns 422 instead of 500 (`352d35c`)
- Vitest globals not in scope — `globals: true` added to `vitest.config.ts` (`352d35c`)
- Next.js upgraded `14.2.5 → 14.2.29` to patch CVE-2024-46982 cache-poisoning (`c895864`)
- docker-compose DB/Redis ports bound to `127.0.0.1` only; passwords moved to env vars (`73b529f`)
