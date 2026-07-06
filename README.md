# Risk Map — Kędzierzyn-Koźle County

An interactive map combining diverse local risks (public safety, infrastructure, natural hazards) in one place, regardless of which service or institution is responsible for them.

## Project Goal

A demo showing an approach to the problem of aggregating geospatial data from multiple, independent sources (some available via API, some existing only as local knowledge) and visualizing them on a single, interactive map.

## MVP Scope

- Interactive map (Leaflet) with layers corresponding to risk categories
- Seed data: risk categories from the `Mapa_zagrożeń.xlsx` file (critical infrastructure, vacant/derelict buildings, road infrastructure, higher-risk facilities, rivers/watercourses, flood zones, illegal dumping sites, and others)
- A form for reporting new risks (for categories without a public API)
- Layer filtering by category
- Risk detail preview (popup)
- Aggregate risk heatmap
- Distinction between `verified` / `unverified` reports
- A simple report-approval mechanism (basic-level authorization — see Authorization section)

## Architecture

### Data ingestion layer

Each data source (Excel file, future external APIs, the report form) implements the same fixed sequence of steps:

```
load() → clean() → geocode() → map_to_schema()
```

The base class defines the order and the output format; each source implements the steps in its own way. This means adding a new data source in the future (e.g. AED locations or ISOK flood zones) only requires writing one new class, with no changes to the rest of the application.

Sources are registered in a single place (a configuration/list), rather than scattered across the codebase — adding a source is just adding an entry to the registry.

A failure in one source (e.g. an unavailable external API) does not interrupt the loading of the others — each source is isolated (fault isolation).

### Common risk schema

Regardless of source, every risk record is mapped to a shared format:

| Field           | Description                                              |
| --------------- | -------------------------------------------------------- |
| `main_category` | e.g. Critical infrastructure, Vacant/derelict buildings  |
| `risk_type`     | detailed description of the hazard                       |
| `geometry`      | point or area (lat/lng)                                  |
| `weight`        | intensity/significance of the risk, used for the heatmap |
| `source`        | where the record comes from (source/file name)           |
| `status`        | `verified` / `unverified`                                |
| `updated_at`    | when the record was added/modified                       |

Risk categories are stored as configuration data (not hardcoded), so that adding a new category doesn't require changes to the map-rendering logic.

### Tech stack

- **Frontend**: SPA (React) + Leaflet (map, layers, heatmap, popups)
- **Backend**: simple REST API (CRUD for risks and reports) — Python + FastAPI
- **Database**: relational (PostgreSQL) — rationale: the report form requires real-time writes, which rules out static GeoJSON files as the sole data store; a database + migrations also make future schema changes easier
- **Geocoding**: `openlocationcode` library (Plus Codes) + `requests` (expanding shortened Google Maps links)
- **Hosting**: Railway (backend + database) + Vercel/Netlify (frontend)

The frontend communicates with the backend exclusively through a defined API contract — this allows both layers to evolve independently.

### Report verification

- Seed data (from the Excel file) is `verified` from the start
- New reports submitted via the form default to `unverified`
- Visually distinguished on the map (e.g. different marker border style)
- Approval via a dedicated endpoint (`PATCH /risks/{id}/approve`)

### Authorization

Endpoints that modify data (approving reports) are protected by a fixed API key passed in a request header, set as an environment variable on the backend — never committed to the frontend code. This is a simplified solution suitable for internal testing/demo purposes.

**Recommendation before production deployment**: replace with a full login system (user table, hashed passwords, session tokens) — deliberately deferred outside MVP scope due to time constraints.

For public hosting, the minimum requirements are: HTTPS, CORS restricted to the frontend domain, and rate limiting on write endpoints.

## Source Data Geocoding

The `Mapa_zagrożeń.xlsx` file contains locations in two formats, both requiring conversion to lat/lng:

- Google Maps links (expanding the redirect)
- Plus Codes / Open Location Code (decoded with an offline library)

## Possible Extensions (beyond MVP)

- AED coverage gap analysis (Voronoi diagram or point grid + distance to nearest AED)
- Integration with the GUS BDL API (aggregate crime statistics per municipality)
- Integration with ISOK/Hydroportal (official flood risk zones)
- Real emergency-response drive-time isochrones (OSRM/OpenRouteService)
- A spreadsheet template for collecting local knowledge from the remaining municipalities in the county

## Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (for the local database)
- Git

### 1. Clone the repository and set up the database

```bash
git clone <repo-url>
cd mapa-zagrozen
docker-compose up -d
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` (see `backend/.env.example`):

Run database migrations:

```bash
alembic upgrade head
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

Verify it's running:

### 3. Frontend setup

```bash
cd frontend
npm install
```

Create `frontend/.env`:

Start the frontend:

```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

### Database migrations (Alembic)

To add a new migration after changing a model in `app/models.py`:

```bash
alembic revision --autogenerate -m "description of the change"
alembic upgrade head
```

To roll back the last migration:

```bash
alembic downgrade -1
```

## Project Structure

```
mapa-zagrozen/
├── docker-compose.yml        # Local PostgreSQL database
├── .gitignore
├── README.md
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI entry point, CORS config
│   │   ├── database.py       # DB connection/session setup
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   └── zagrozenia.py # CRUD endpoints for risks/reports
│   │   └── sources/
│   │       ├── base.py              # Template Method base class
│   │       └── manager_excel.py     # Adapter for Mapa_zagrożeń.xlsx
│   ├── alembic/               # Migration scripts
│   ├── requirements.txt
│   ├── .env                   # Local secrets (gitignored)
│   └── .env.example           # Template, committed to git
└── frontend/
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx
    │   ├── components/
    │   │   ├── Map.jsx              # Leaflet map component
    │   │   ├── LayerControls.jsx    # Layer toggle controls
    │   │   ├── RiskPopup.jsx        # Risk detail popup
    │   │   └── ReportForm.jsx       # New risk report form
    │   ├── api/
    │   │   └── client.js            # Backend API calls
    │   └── index.css
    ├── .env                          # Local config (gitignored)
    ├── .env.example                  # Template, committed to git
    └── package.json
```
