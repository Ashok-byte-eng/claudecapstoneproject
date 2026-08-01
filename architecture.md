# High-Level System Architecture

## Overview

This document describes the proposed architecture for the Accommodation Advanced Filters feature — a new web application that allows travelers to filter search results by amenities, property type, and customer review scores in real time.

---

## Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | **React + Next.js** | SSR support, fast page loads, strong ecosystem, mobile-ready |
| Styling | **Tailwind CSS** | Utility-first, mobile-responsive out of the box |
| State Management | **Zustand** | Lightweight, simple filter state management |
| Backend | **Python + FastAPI** | Async, high-performance REST API, auto-generates OpenAPI docs |
| Database | **PostgreSQL** | Structured accommodation data, enforced enums for data integrity |
| Caching | **Azure Cache for Redis** | API response caching; prevents DB overload under concurrent load |
| Migrations | **Alembic** | Versioned schema migrations across dev / staging / prod |
| Rate Limiting | **slowapi** | FastAPI middleware — 60 req/min per IP on accommodation endpoint |
| Monitoring | **Azure Application Insights + OpenTelemetry** | Error rates, p95 latency alerting, NFR-01 enforcement |
| API Gateway | **Azure API Management** | Gateway-level throttling, API key management |
| CI/CD | **GitHub Actions** | Automated lint → test → build → deploy pipeline |
| Cloud | **Microsoft Azure** | Hosting, database, CDN, static web apps |
| Containerisation | **Docker** | Consistent environment across dev and Azure deployment |

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Microsoft Azure                             │
│                                                                     │
│  ┌──────────────────────────┐      ┌──────────────────────────────┐ │
│  │  Azure Static Web Apps   │      │   Azure App Service          │ │
│  │  (Next.js Frontend)      │      │   (FastAPI Backend)          │ │
│  │                          │      │                              │ │
│  │  ┌────────────────────┐  │      │  ┌────────────────────────┐  │ │
│  │  │   Search Results   │  │      │  │  AccommodationRouter   │  │ │
│  │  │       Page         │  │      │  │  GET /accommodations   │  │ │
│  │  └─────────┬──────────┘  │      │  └───────────┬────────────┘  │ │
│  │            │             │      │              │               │ │
│  │  ┌─────────▼──────────┐  │ HTTP │  ┌───────────▼────────────┐  │ │
│  │  │   Filter UI Panel  │  │◄─────┤  │  AccommodationService  │  │ │
│  │  │  - Amenities       │  │      │  │  - Query & transform   │  │ │
│  │  │  - Property Type   │  │      │  │  - Serialize response  │  │ │
│  │  │  - Review Score    │  │      │  └───────────┬────────────┘  │ │
│  │  └─────────┬──────────┘  │      │              │               │ │
│  │            │             │      │  ┌───────────▼────────────┐  │ │
│  │  ┌─────────▼──────────┐  │      │  │     DatabaseClient     │  │ │
│  │  │   Filter Engine    │  │      │  │  (SQLAlchemy ORM)      │  │ │
│  │  │  (Client-side JS)  │  │      │  └───────────┬────────────┘  │ │
│  │  └─────────┬──────────┘  │      └──────────────┼───────────────┘ │
│  │            │             │                     │               │ │
│  │  ┌─────────▼──────────┐  │      ┌──────────────▼───────────────┐ │
│  │  │  Results List      │  │      │  Azure Database for          │ │
│  │  │  (Live Updated)    │  │      │  PostgreSQL                  │ │
│  │  └────────────────────┘  │      │  - accommodations            │ │
│  │                          │      │  - amenities                 │ │
│  │  ┌────────────────────┐  │      │  - property_types            │ │
│  │  │  Azure CDN         │  │      │  - review_scores             │ │
│  │  │  (Static Assets)   │  │      └──────────────────────────────┘ │
│  │  └────────────────────┘  │                                     │ │
│  └──────────────────────────┘                                     │ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Components and Responsibilities

### 1. Filter UI Panel (Frontend)
**Location:** React component — `components/FilterPanel.tsx`

**Responsibilities:**
- Renders multi-select checkboxes for amenities (Wi-Fi, Breakfast, Pool, Gym, Spa)
- Renders multi-select checkboxes for property type (Hotel, Villa)
- Renders a toggle for the 4★+ review score filter
- Displays active filter badges with individual clear buttons
- Provides a "Clear All" reset control
- On mobile: renders as a collapsible drawer/sidebar
- Dispatches filter state changes to Zustand store on every selection

---

### 2. Filter Engine (Frontend)
**Location:** `lib/filterEngine.ts`

**Responsibilities:**
- Pure function — takes the full accommodation dataset and current filter state as inputs
- Applies AND logic for multi-selected amenities (accommodation must have all selected amenities)
- Applies OR logic for multi-selected property types (accommodation matches any selected type)
- Applies minimum threshold logic for review score (>= 4.0)
- Returns a filtered array of accommodations
- Runs entirely client-side on every filter state change (no API call required)
- Executes in < 100ms for datasets up to ~2,000 records
- **Threshold rule:** if the API returns > 2,000 records, the backend pre-filters by destination before responding; client-side filtering is never applied to payloads exceeding this limit

---

### 3. Results List (Frontend)
**Location:** `components/ResultsList.tsx`

**Responsibilities:**
- Renders accommodation cards from the filtered dataset
- Displays name, property type, amenities icons, review score, and price
- Responds to filter changes without page reload
- Shows result count (e.g., "24 of 150 properties")
- Handles empty state (no results match current filters)
- Mobile-responsive card grid layout

---

### 4. Accommodation API Router (Backend)
**Location:** `routers/accommodations.py`

**Responsibilities:**
- Exposes `GET /api/accommodations` endpoint
- Accepts optional query parameters for destination, travel dates, and passenger count (existing filters)
- Returns full accommodation dataset as JSON for client-side filtering
- Validates and parses request parameters
- Returns appropriate HTTP error responses

---

### 5. Accommodation Service (Backend)
**Location:** `services/accommodation_service.py`

**Responsibilities:**
- Contains all business logic for accommodation queries
- Queries PostgreSQL via SQLAlchemy ORM (uses `selectinload` to avoid N+1 on amenities JOIN)
- Joins accommodations with amenities, property types, and aggregated review scores
- Serializes database records to Pydantic response models
- Caches API responses in **Azure Cache for Redis** (TTL: 5 min, key: `accommodations:{destination}:{check_in}:{check_out}:{guests}`)
- Enforces 2,000-record threshold: applies server-side destination pre-filter when result set exceeds limit

---

### 6. Database Client (Backend)
**Location:** `db/database.py`

**Responsibilities:**
- Manages PostgreSQL connection pool via SQLAlchemy async engine
- Provides session factory for dependency injection into FastAPI routes
- Handles connection lifecycle (open, reuse, close)

---

### 7. PostgreSQL Database (Azure)
**Service:** Azure Database for PostgreSQL — Flexible Server

**Responsibilities:**
- Persists all accommodation records
- Stores amenity associations per accommodation
- Stores property type per accommodation
- Stores aggregated review scores (pre-computed average per accommodation)

---

## Data Flow

### Initial Page Load
```
1. User navigates to Search Results page
2. Next.js (SSR) calls GET /api/accommodations?destination=X&dates=Y&guests=Z
3. FastAPI AccommodationRouter receives request
4. AccommodationService queries PostgreSQL (accommodations + amenities JOIN)
5. Returns JSON array of all matching accommodations (with amenities, type, score)
6. Frontend stores full dataset in Zustand store
7. ResultsList renders all accommodations (no filters active)
8. FilterPanel renders with all options unchecked
```

### User Applies a Filter
```
1. User checks "Pool" in the Filter UI Panel
2. FilterPanel dispatches updated filter state to Zustand store
3. Filter Engine runs synchronously against the cached dataset
4. Filter Engine returns filtered array (accommodations with Pool)
5. ResultsList re-renders with filtered results
6. Active filter badge "Pool" appears in FilterPanel
7. Result count updates (e.g., "12 of 150 properties")
   ── No API call is made ──
```

### User Clears All Filters
```
1. User clicks "Clear All"
2. Zustand store resets filter state to empty
3. Filter Engine returns the full cached dataset
4. ResultsList re-renders with all accommodations
```

---

## Database Schema

```sql
-- Enum for property type — prevents dirty data ('Hotel' vs 'hotel')
CREATE TYPE property_type_enum AS ENUM ('hotel', 'villa');

-- Core accommodation record
CREATE TABLE accommodations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    property_type   property_type_enum NOT NULL,
    destination     VARCHAR(255) NOT NULL,
    price_per_night NUMERIC(10, 2),
    review_score    NUMERIC(3, 2),       -- recomputed nightly from reviews table
    image_url       VARCHAR(500),        -- accommodation photo URL
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Amenities lookup table
CREATE TABLE amenities (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL     -- 'wifi' | 'breakfast' | 'pool' | 'gym' | 'spa'
);

-- Many-to-many: accommodations ↔ amenities
CREATE TABLE accommodation_amenities (
    accommodation_id UUID REFERENCES accommodations(id) ON DELETE CASCADE,
    amenity_id       INT  REFERENCES amenities(id) ON DELETE CASCADE,
    PRIMARY KEY (accommodation_id, amenity_id)
);

-- Reviews table — source of truth for review_score
CREATE TABLE reviews (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    accommodation_id UUID REFERENCES accommodations(id) ON DELETE CASCADE,
    score            NUMERIC(3, 2) NOT NULL CHECK (score >= 0 AND score <= 5),
    created_at       TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_review_score   ON accommodations(review_score);
CREATE INDEX idx_property_type  ON accommodations(property_type);
CREATE INDEX idx_destination    ON accommodations(destination);
CREATE INDEX idx_reviews_acc_id ON reviews(accommodation_id);
```

---

## API Contract

### `GET /api/accommodations`

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| destination | string | Yes | City or region name |
| check_in | date | Yes | ISO 8601 date |
| check_out | date | Yes | ISO 8601 date |
| guests | integer | Yes | Number of guests |

**Response (200 OK):**
```json
{
  "total": 150,
  "accommodations": [
    {
      "id": "uuid",
      "name": "Grand Hotel Lisbon",
      "property_type": "hotel",
      "destination": "Lisbon",
      "price_per_night": 120.00,
      "review_score": 4.7,
      "amenities": ["wifi", "breakfast", "gym"],
      "image_url": "https://cdn.example.com/hotel1.jpg"
    }
  ]
}
```

---

## Azure Deployment Topology

```
┌───────────────────────────────────────────────────────────┐
│              Azure Resource Group (per environment)        │
│                                                           │
│  ┌─────────────────────┐                                  │
│  │ Azure Static Web App│  ← Next.js build output          │
│  │ (Frontend)          │    PR preview envs supported     │
│  └──────────┬──────────┘                                  │
│             │ HTTPS                                        │
│  ┌──────────▼──────────┐                                  │
│  │ Azure API Management│  ← Rate limiting, throttling     │
│  │ (API Gateway)       │    API key for server calls      │
│  └──────────┬──────────┘                                  │
│             │ HTTPS (internal)                             │
│  ┌──────────▼──────────┐                                  │
│  │ Azure App Service   │  ← Docker (FastAPI + slowapi)    │
│  │ (Backend API)       │    CORS middleware configured    │
│  └──────────┬──────────┘                                  │
│             │ Private VNet                                 │
│  ┌──────────▼──────────┐   ┌──────────────────────────┐  │
│  │ Azure DB for        │   │ Azure Cache for Redis    │  │
│  │ PostgreSQL          │   │ (API response cache)     │  │
│  │ (Flexible Server)   │   │ TTL: 5 min               │  │
│  └─────────────────────┘   └──────────────────────────┘  │
│                                                           │
│  ┌─────────────────────┐   ┌──────────────────────────┐  │
│  │ Azure CDN           │   │ Azure Application        │  │
│  │ (Static assets)     │   │ Insights (Monitoring)    │  │
│  └─────────────────────┘   └──────────────────────────┘  │
│                                                           │
│  ┌─────────────────────┐                                  │
│  │ Azure Key Vault     │  ← DB + Redis connection strings │
│  │                     │    accessed via Managed Identity  │
│  └─────────────────────┘                                  │
└───────────────────────────────────────────────────────────┘

Environments: dev → staging → prod (separate Resource Groups)
Pipeline: GitHub Actions → Azure Container Registry → App Service
```

---

## Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Filtering strategy | Client-side (≤ 2,000 records) | Real-time UX without API round-trips; threshold enforced server-side |
| API pattern | REST (not GraphQL) | Simpler for a well-defined, single-entity endpoint |
| ORM | SQLAlchemy (async) + selectinload | Python-native async; selectinload prevents N+1 on amenities JOIN |
| Frontend state | Zustand | Minimal boilerplate vs Redux; sufficient for filter state complexity |
| DB hosting | Azure DB for PostgreSQL Flexible Server | Managed, auto-backup, scales vertically, stays within Azure |
| property_type | PostgreSQL ENUM | Enforces data integrity; prevents case/typo mismatches breaking filters |
| review_score | Pre-aggregated + nightly refresh job | Fast reads; reviews table is source of truth for recalculation |
| Caching | Azure Cache for Redis (5-min TTL) | Absorbs repeated identical queries under concurrent load |
| Rate limiting | slowapi (app) + Azure APIM (gateway) | Defense-in-depth against API abuse |
| CORS | FastAPI middleware with explicit origin allowlist | Required for cross-origin browser requests; never `*` in production |
| Secret management | Azure Key Vault + Managed Identity | Credentials never hardcoded or passed via environment variables in plain text |
| Migrations | Alembic | Versioned, reproducible schema changes across all environments |
| Observability | Azure Application Insights + OpenTelemetry | Error rate and p95 latency alerts aligned to NFR-01 (3-second threshold) |
| CI/CD | GitHub Actions | Automated pipeline: lint → test → build → deploy-staging → deploy-prod |
| Styling | Tailwind CSS | NFR-02 mobile responsiveness achieved with minimal custom CSS |
