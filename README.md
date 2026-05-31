# Train Tracker

Search for Belgian train stations and see upcoming departures in real time. Powered by the [iRail API](https://api.irail.be).

The app uses fuzzy matching against both the English name and local standardname of each station.

---

## Table of contents

- [Running with Docker](#running-with-docker)
- [Running locally](#running-locally)
- [Running tests](#running-tests)
- [Decisions, trade-offs, and known limitations](#decisions-trade-offs-and-known-limitations)
- [Time spent on the project](#time-spent-on-the-project)

---

## Running with Docker

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) with Compose.

```bash
git clone https://github.com/leragogogo/train-tracker.git
cd train-tracker
# Windows: copy .env.template .env
cp .env.template .env   # edit .env if you want to change any values
docker compose up --build -d
```

If you encounter troubles during `docker compose up --build -d`:

```bash
docker compose build frontend
docker compose build backend
docker compose up -d
```

Open **http://localhost** in your browser.

To stop:

```bash
docker compose down
```

### Environment variables

All variables live in the root `.env` file. Docker Compose reads it automatically.

| Variable | Default | Description |
|---|---|---|
| `IRAIL_BASE_URL` | `https://api.irail.be` | iRail API base URL |
| `DEPARTURE_WINDOW_SECONDS` | `900` | How far ahead to show departures (seconds) |
| `VITE_DEBOUNCE_MS` | `300` | Debounce delay before a search fires (ms) |
| `VITE_MIN_QUERY_LENGTH` | `3` | Minimum characters before searching |

Note: `VITE_*` variables are baked into the frontend at build time, so changing them requires a rebuild (`docker compose up --build`).

---

## Running locally

### Backend

**Prerequisites:** Python 3.9+

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the env template and adjust if needed:

```bash
cp .env.template .env # Windows: copy .env.template .env
```

Start the API server:

```bash
uvicorn main:app --reload
```

The API is available at **http://localhost:8000**. Interactive docs at **http://localhost:8000/docs**.

### Frontend

**Prerequisites:** Node 22+

```bash
cd frontend
npm install
```

Copy the env template:

```bash
cp .env.template .env # Windows: copy .env.template .env
```

Start the dev server:

```bash
npm run dev
```

Open **http://localhost:5173**.

---

## Running tests

### Backend

```bash
cd backend
source venv/bin/activate
pytest
```

### Frontend

```bash
cd frontend
npm test
```

---

## Decisions, trade-offs, and known limitations

**Response schema.** The API schema is defined with Pydantic models. FastAPI uses these to validate responses and auto-generate an OpenAPI schema available at `/docs`. Both `station` (the departure board) and `destination` (inside each departure) are returned as full objects with `id`, `name`, and `standardname`, rather than just a name string. This gives the frontend enough information to display both the local and English names.

**Fuzzy matching on both name fields.** For fuzzy search `rapidfuzz` library was chosen. Each station in the iRail dataset has an English `name` (e.g. "Ghent-Sint-Pieters") and a local `standardname` (e.g. "Gent-Sint-Pieters"). The query is scored against both with `rapidfuzz.partial_ratio` and the station matches if either score is ≥ 80. This means typing either the English or the local spelling finds the station. 80 was chosen as a practical balance.

**In-memory stations cache.** The iRail stations list is fetched once on the first request and stored in memory for the lifetime of the process. This avoids a redundant network call on every search. The limitation is that the cache is never refreshed, and if iRail adds or renames stations, or any station is temporarily closed, the changes won’t be visible until a restart.

**No state persistence across reloads.** The search query and results live only in React state. Refreshing the page resets the app to its initial empty state. The right fix is to persist the query in sessionStorage and re-fetch on load. This was not implemented.

**Not optimized for mobile.** The UI was designed and tested on desktop. On narrow screens the departure table remains readable but is not ideal. A proper mobile layout would likely replace the table with a card-based list per departure. This was not implemented.

**No pagination.**  Pagination was considered early on, but the iRail API does not support it, and there is no way to fetch departures in portions. All data is always returned in a single response, so adding a pagination layer on top would only slice the data we already have in memory, not reduce the amount fetched from iRail. It was therefore left out.

## Time spent on the project

Roughly, I spent 5 hours.
