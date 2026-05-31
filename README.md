# Train Tracker

Search for Belgian train stations and see upcoming departures in real time. Powered by the [iRail API](https://api.irail.be).

Type at least 3 characters — the app uses fuzzy matching against both the English name and local standardname of each station.

---

## Running with Docker

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) with Compose.

```bash
git clone https://github.com/leragogogo/train-tracker.git
cd train-tracker
cp .env.template .env   # edit .env if you want to change any values
docker compose up --build
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
cp .env.template .env
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
cp .env.template .env
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
