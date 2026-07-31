# Architecture Design Review

**Document:** architecture.md
**Reviewer role:** Senior Architect (Copilot/Claude review pass)
**Date:** 2026-07-31
**Status:** Findings documented — architecture.md updated accordingly

---

## Review Summary

The architecture is well-structured for the stated requirements. The technology choices are appropriate and the data flow is clear. However, **12 risks and gaps** were identified across security, scalability, data integrity, observability, and deployment — several of which would cause production failures if not addressed before coding begins.

---

## Findings

### RISK-01 — Client-Side Filtering Has No Scalability Fallback
**Severity:** High
**Location:** Filter Engine, Architecture Decisions table

**Finding:**
The Filter Engine documents a limit of ~2,000 records but there is no mechanism to detect when this threshold is exceeded. A popular destination (e.g., Paris, London) could return 5,000–10,000+ records. Loading this into the browser causes:
- Large initial payload (potentially 5–10 MB of JSON)
- Slow parse and render on mobile
- Filter Engine execution time exceeds the 3-second NFR

**Resolution:**
- Define a hard payload threshold: if `GET /api/accommodations` returns > 2,000 records, the API applies server-side pre-filtering by destination before returning results.
- Document this threshold explicitly in the architecture.
- Add `X-Total-Count` response header so the frontend can detect large result sets.

---

### RISK-02 — API Has No Caching Implementation
**Severity:** High
**Location:** AccommodationService responsibilities

**Finding:**
The AccommodationService states "Caches frequently requested datasets using FastAPI's cache layer" — but FastAPI has no built-in cache. This is vague and unimplementable as written. Under concurrent load (e.g., 100 users searching "Lisbon" simultaneously), each request hits the database independently.

**Resolution:**
- Add **Azure Cache for Redis** to the architecture as an explicit caching layer.
- Define cache key strategy: `accommodations:{destination}:{check_in}:{check_out}:{guests}`
- Define TTL: 5 minutes (stale data is acceptable for accommodation listings).
- Use `fastapi-cache2` library with Redis backend.
- Add Redis to the Azure Deployment Topology diagram.

---

### RISK-03 — Review Score Is Pre-Aggregated With No Refresh Mechanism
**Severity:** High
**Location:** Database Schema — `review_score` column

**Finding:**
`review_score NUMERIC(3,2)` is described as "pre-aggregated avg" but:
1. There is no `reviews` table or ingestion mechanism shown.
2. There is no cron job, trigger, or event described to recompute scores.
3. Stale scores would violate the user's expectation that the 4★+ filter reflects current ratings.

**Resolution:**
- Add a `reviews` table to the schema (accommodation_id, score, created_at).
- Add a PostgreSQL trigger or a nightly background job (Azure Function / Celery task) to recompute `review_score` from the reviews table.
- Document the refresh cadence.

---

### RISK-04 — No Authentication or Authorization on the API
**Severity:** Medium
**Location:** API Contract — `GET /api/accommodations`

**Finding:**
The API endpoint is entirely unauthenticated. Any actor can call it directly, enumerate all accommodation data by cycling through destinations, or use it as a scraping endpoint. No mention of:
- Who is allowed to call the API
- How the frontend is identified
- Whether guest (unauthenticated) access is intentional

**Resolution:**
- For this user story, accept that end-users browse as guests (no login required).
- Protect the API with **Azure API Management** as a gateway — adds rate limiting, IP-based throttling, and API key for server-to-server calls.
- Document that the endpoint is public-read with rate limiting enforced.

---

### RISK-05 — No Rate Limiting
**Severity:** Medium
**Location:** Accommodation API Router, Azure Deployment Topology

**Finding:**
Without rate limiting, the API is vulnerable to abuse: high-frequency polling, scrapers, or accidental client loops can exhaust database connections.

**Resolution:**
- Add `slowapi` (FastAPI rate limiting middleware) at the application layer.
- Set limit: 60 requests/minute per IP on `GET /api/accommodations`.
- Add Azure API Management in front of App Service for a second layer of throttling.

---

### RISK-06 — CORS Policy Not Configured
**Severity:** Medium
**Location:** Architecture diagram — Frontend ↔ Backend communication

**Finding:**
The frontend (Azure Static Web Apps) and backend (Azure App Service) are on different origins (different subdomains). Without explicit CORS configuration, the browser will block all API calls from the frontend, making the application non-functional.

**Resolution:**
- Add FastAPI CORS middleware configuration:
  - `allow_origins`: Azure Static Web App URL (not `*` in production)
  - `allow_methods`: `["GET"]`
  - `allow_headers`: `["*"]`
- Document allowed origins per environment (dev / staging / prod).

---

### RISK-07 — `property_type` Is a Free-Text VARCHAR
**Severity:** Medium
**Location:** Database Schema

**Finding:**
`property_type VARCHAR(50)` allows dirty data: 'Hotel', 'hotel', 'HOTEL', 'hotell' are all valid but would not match the same filter. This breaks the OR-logic in the Filter Engine silently.

**Resolution:**
- Change `property_type` to a PostgreSQL `ENUM` type:
  ```sql
  CREATE TYPE property_type_enum AS ENUM ('hotel', 'villa');
  ALTER TABLE accommodations
    ALTER COLUMN property_type TYPE property_type_enum
    USING property_type::property_type_enum;
  ```
- Enforce lowercase normalisation at the API serialization layer (Pydantic model).

---

### RISK-08 — `image_url` Missing From Database Schema
**Severity:** Low
**Location:** API Contract response body vs Database Schema

**Finding:**
The API response includes `"image_url": "https://cdn.example.com/hotel1.jpg"` but the `accommodations` table has no `image_url` column. This will cause a runtime error when the service tries to serialize the response.

**Resolution:**
- Add `image_url VARCHAR(500)` column to the `accommodations` table.
- Add index only if image URL lookups are needed; otherwise no index required.

---

### GAP-01 — No Database Migration Tooling
**Severity:** Medium
**Location:** Database Schema section

**Finding:**
The schema is presented as raw `CREATE TABLE` SQL with no migration strategy. Without a migration tool, schema changes during development will be applied manually and inconsistently across dev/staging/prod.

**Resolution:**
- Add **Alembic** (the standard SQLAlchemy migration tool) to the backend stack.
- Add `alembic/` directory to the project structure.
- Document that all schema changes go through Alembic versioned migration files.

---

### GAP-02 — No Observability / Monitoring
**Severity:** Medium
**Location:** Azure Deployment Topology

**Finding:**
No logging, monitoring, or alerting is defined. In production, there is no way to detect API errors, slow queries, or filter performance degradation.

**Resolution:**
- Add **Azure Application Insights** to the deployment topology.
- Instrument FastAPI with `opentelemetry-instrumentation-fastapi`.
- Define at minimum: error rate alert, p95 response time alert (threshold: 3 seconds, matching NFR-01).
- Add structured logging to the Filter Engine timing on the frontend.

---

### GAP-03 — No CI/CD Pipeline
**Severity:** Medium
**Location:** Azure Deployment Topology

**Finding:**
The deployment topology shows Azure services but no pipeline is defined. Manual deployments to production are error-prone and unauditable.

**Resolution:**
- Add **GitHub Actions** pipeline with stages: lint → test → build → deploy-staging → deploy-prod.
- Frontend: deploy to Azure Static Web Apps via `azure/static-web-apps-deploy` action.
- Backend: build Docker image → push to Azure Container Registry → deploy to App Service.
- Add pipeline diagram to architecture.md.

---

### GAP-04 — No Environment Separation Strategy
**Severity:** Low
**Location:** Azure Deployment Topology

**Finding:**
Only a single environment is shown. No dev / staging / production separation means developers test changes against production infrastructure.

**Resolution:**
- Define three environments: `dev`, `staging`, `prod`.
- Each environment gets its own Azure Resource Group.
- Azure Static Web Apps supports preview environments per PR — leverage this for staging.
- Document environment-specific configuration (API URLs, Redis TTL, rate limits).

---

## Agreed Design Decisions

| ID | Decision | Rationale |
|---|---|---|
| DD-01 | Add Azure Cache for Redis as explicit API caching layer | Prevents DB overload; replaces vague "FastAPI cache layer" reference |
| DD-02 | Set client-side filtering threshold at 2,000 records; API pre-filters by destination beyond that | Protects mobile clients from oversized payloads |
| DD-03 | Add `reviews` table + nightly score recomputation job | Ensures `review_score` reflects current ratings |
| DD-04 | Add Azure API Management as API gateway | Provides rate limiting, throttling, and API observability |
| DD-05 | Add `slowapi` rate limiting middleware (60 req/min per IP) | Defense-in-depth against abuse |
| DD-06 | Configure FastAPI CORS middleware with explicit origin allowlist | Required for browser to accept cross-origin API responses |
| DD-07 | Change `property_type` from VARCHAR to PostgreSQL ENUM | Prevents dirty data breaking filter logic |
| DD-08 | Add `image_url VARCHAR(500)` to accommodations table | Fixes schema/API contract mismatch |
| DD-09 | Add Alembic for database migrations | Consistent schema management across all environments |
| DD-10 | Add Azure Application Insights + OpenTelemetry instrumentation | Enables monitoring and NFR-01 alerting |
| DD-11 | Add GitHub Actions CI/CD pipeline | Automated, auditable deployments |
| DD-12 | Define dev / staging / prod environment separation | Prevents testing against production infrastructure |

---

## Items Deferred (Out of Scope for This Review)

- Authentication / user login flows (no login required for this user story)
- Pagination (dataset per destination stays under 2,000 with server-side pre-filtering)
- Elasticsearch / search engine replacement (PostgreSQL sufficient at current scale)
