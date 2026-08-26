# Dominican Fuel Prices API — Design Document

Status: Draft v1.0
Audience: Backend developers implementing `dr-fuel-api`

## 1. Overview

The Dominican Republic's Ministerio de Industria, Comercio y Mipymes (MICM) publishes
a fuel price bulletin every Friday, effective the following Saturday through Friday.
The bulletin lists a fixed set of fuel types, each with a price in RD$, compared against
the prior week (see the reference table below).

This API exposes that same information programmatically: the current week's prices, any
past week by year/week, and the price history of a given fuel type over time.

| Combustible | 15-08 | 22-08 | Dif |
|---|---|---|---|
| Gasolina Premium | RD$341.10 | RD$341.10 | RD$0.00 = |
| Gasolina Regular | RD$307.50 | RD$310.50 | RD$3.00 ▲ |
| Gasoil Óptimo | RD$293.10 | RD$293.10 | RD$0.00 = |
| Gasoil Regular | RD$259.80 | RD$262.80 | RD$3.00 ▲ |
| Kerosene | RD$324.60 | RD$336.70 | RD$12.10 ▲ |
| Gas Licuado (GLP) | RD$135.20 | RD$135.20 | RD$0.00 = |
| Gas Natural (GNV) | RD$43.97 | RD$43.97 | RD$0.00 = |

## 2. Goals / Non-Goals

**Goals**
- Serve the current week's prices for all fuel types, with diff vs. the prior week.
- Serve any historical week by `(year, week)`.
- Serve the full price history of a single fuel type, for charting trends over time.
- Keep the data model append-only and auditable — this is officially sourced pricing data.

**Non-goals (v1)**
- No automated scraping of the MICM bulletin (see §7, phased).
- No regional/zone pricing — single national price list per fuel type per week.
- No user accounts; reads are public, writes are admin-only.

## 3. Domain Concepts

- **Fuel type** — one of the 7 fixed categories MICM publishes (Gasolina Premium, Gasolina
  Regular, Gasoil Óptimo, Gasoil Regular, Kerosene, Gas Licuado/GLP, Gas Natural/GNV).
- **Price week** — one MICM bulletin, identified by `(year, week)` using the ISO week
  number, with an explicit `period_start` (Saturday) / `period_end` (Friday).
- **Diff / trend** — the change vs. the immediately preceding week for the same fuel type.
  Always *derived*, never stored, so a backfilled or corrected week never leaves a stale
  diff lying around.

## 4. Data Model

```
fuel_types
  id            smallserial PK
  code          text UNIQUE NOT NULL   -- e.g. "gasolina_premium"
  name          text NOT NULL          -- e.g. "Gasolina Premium"
  unit          text NOT NULL DEFAULT 'gallon'   -- 'gallon' | 'm3'

weekly_prices
  id            bigserial PK
  fuel_type_id  smallint FK -> fuel_types.id
  year          smallint NOT NULL
  week          smallint NOT NULL      -- ISO week number, 1-53
  period_start  date NOT NULL          -- Saturday
  period_end    date NOT NULL          -- Friday
  price         numeric(10,2) NOT NULL
  created_at    timestamptz NOT NULL DEFAULT now()

  UNIQUE (fuel_type_id, year, week)
  INDEX  (year, week)
```

`fuel_types` is a small, slow-changing reference table. `weekly_prices` is append-only:
corrections insert a new row rather than mutating history (exact mechanism is an open
question, see §9).

## 5. API Specification

Base path: `/api/v1`

### `GET /fuel-types`
List all fuel types.

```json
[
  {"code": "gasolina_premium", "name": "Gasolina Premium", "unit": "gallon"},
  {"code": "gas_natural", "name": "Gas Natural (GNV)", "unit": "m3"}
]
```

### `GET /prices/current`
Latest published week, each fuel type with its diff vs. the prior week.

```json
{
  "year": 2026,
  "week": 34,
  "period_start": "2026-08-16",
  "period_end": "2026-08-22",
  "prices": [
    {
      "fuel_type": "gasolina_regular",
      "name": "Gasolina Regular",
      "price": 310.50,
      "previous_price": 307.50,
      "diff": 3.00,
      "trend": "up"
    },
    {
      "fuel_type": "gasolina_premium",
      "name": "Gasolina Premium",
      "price": 341.10,
      "previous_price": 341.10,
      "diff": 0.00,
      "trend": "equal"
    }
  ]
}
```

### `GET /prices/{year}/{week}`
Same shape as `/prices/current`, for an arbitrary past week.

### `GET /prices/{year}`
Array of every weekly snapshot published in `year`, each shaped like `/prices/{year}/{week}`.

### `GET /prices/history?fuel_type={code}&from={year}-W{week}&to={year}-W{week}`
Time series for one fuel type — the endpoint a price-trend chart would call.

```json
{
  "fuel_type": "kerosene",
  "name": "Kerosene",
  "points": [
    {"year": 2026, "week": 33, "period_start": "2026-08-09", "price": 324.60, "diff": null, "trend": null},
    {"year": 2026, "week": 34, "period_start": "2026-08-16", "price": 336.70, "diff": 12.10, "trend": "up"}
  ]
}
```

### `POST /admin/prices` (protected)
Ingest one week's bulletin. Requires an admin-scoped API key/JWT (see §8).

```json
{
  "year": 2026,
  "week": 34,
  "period_start": "2026-08-16",
  "period_end": "2026-08-22",
  "prices": [
    {"fuel_type": "gasolina_premium", "price": 341.10},
    {"fuel_type": "gasolina_regular", "price": 310.50}
  ]
}
```
Rejects the request if `(year, week)` already exists — corrections go through a separate,
explicit endpoint/flow (open question, §9).

## 6. Business Rules

- Week identity is the ISO `(year, week)` pair, matching MICM's own Saturday–Friday cadence.
- `diff = round(current.price - previous.price, 2)`.
- `trend` = `"up"` if `diff > 0`, `"down"` if `diff < 0`, `"equal"` if `diff == 0`.
- If no prior week exists for a fuel type, `diff`/`trend` are `null`.

## 7. Data Ingestion

MICM publishes the bulletin as a PDF/image, not a public API or feed.

- **Phase 1 (MVP)** — manual entry through `POST /admin/prices`, filled in by hand from
  the published bulletin each Friday.
- **Phase 2** — a scheduled job (cron/Celery beat) fetches and parses the bulletin, then
  calls the same ingestion endpoint, with a manual review/approval step before it goes
  live — this is pricing data people will treat as authoritative, so silent bad parses
  are the failure mode to design against.

## 8. Non-Functional Requirements

- **Auth** — reads are public and unauthenticated; writes require an admin-scoped
  API key or JWT.
- **Caching** — a given `(year, week)` never changes once published, so historical and
  current-week responses should be cached aggressively (`Cache-Control`/`ETag`, optionally
  Redis in front of the DB).
- **Versioning** — `/api/v1` prefix from day one.
- **Pagination** — `/prices/{year}` and `/prices/history` return arrays that grow over
  time; give them `limit`/`offset` (or cursor) params now so the contract doesn't break
  later.
- **Auditability** — log ingestion events (who, when, what changed) since this data is
  presented as an official record.
- **i18n** — fuel `name` stays in Spanish (source of truth); `code`s and field names are
  English for the API contract.

## 9. Tech Stack & Project Structure

Per `requirements.txt`: FastAPI, Uvicorn, SQLAlchemy + psycopg (Postgres), Alembic,
pydantic-settings. Mapped onto the project structure:

```
app/models/fuel_type.py         # SQLAlchemy models
app/models/weekly_price.py
app/schemas/fuel_price.py       # FuelTypeOut, WeeklyPriceOut, PriceDiffOut
app/crud/fuel_price.py          # DB access
app/services/price_diff.py      # diff/trend calculation
app/api/v1/endpoints/fuel_types.py
app/api/v1/endpoints/prices.py
```

## 10. Open Questions

1. Is there any structured MICM source beyond the PDF bulletin, for Phase 2 ingestion?
2. How should corrections to an already-published week be handled — a new versioned row,
   or a hard update with an audit log?
3. Confirm the `unit` split — GLP/GNV priced per m³ vs. liquid fuels per gallon.
4. Is pricing ever regional/zoned, or always a single national list (current assumption)?
5. Auth mechanism for `/admin/prices` — API key, JWT, or restrict to an internal network?
