# PhySioLog API Testing Guide

This document provides curl commands to test the PhySioLog API endpoints.

## Prerequisites

1. **Start the Flask app:**

   ```bash
   uv run python app.py
   ```

2. **Ensure you have test data** (optional, but recommended for testing `/api/stats`):

   ```bash
   uv run python scripts/import_data.py data/health_data.csv
   ```

The app runs on `http://localhost:5000` by default.

---

## API Endpoints

### 1. GET /api/entries

Retrieve all health entries ordered by date (descending).

**Command:**

```bash
curl http://localhost:5000/api/entries
```

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "date": "2026-02-15",
    "weight": 72.5,
    "body_fat": 18.2,
    "calories": 2200,
    "steps": 8500,
    "sleep_total": 7.5,
    "sleep_quality": "good",
    "observations": "felt energetic"
  },
  ...
]
```

---

### 2. POST /api/entries

Create a new health entry.

**Command:**

```bash
curl -X POST http://localhost:5000/api/entries \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-15",
    "weight": 72.5,
    "body_fat": 18.2,
    "calories": 2200,
    "steps": 8500,
    "sleep_total": 7.5,
    "sleep_quality": "good",
    "observations": "felt energetic"
  }'
```

**Response (201 Created):**

```json
{
  "success": true,
  "entry": {
    "id": 1,
    "date": "2026-02-15",
    "weight": 72.5,
    ...
  }
}
```

**Error Cases:**

- **400 Bad Request:** Missing date, invalid JSON, or invalid date format
- **409 Conflict:** Entry for the provided date already exists

---

### 3. GET /api/stats

Return aggregated statistics for health entries.

#### 3.1 All-time stats

```bash
curl http://localhost:5000/api/stats
```

#### 3.2 Last 7 days (using `window` parameter)

```bash
curl "http://localhost:5000/api/stats?window=7d"
```

#### 3.3 Last 30 days

```bash
curl "http://localhost:5000/api/stats?window=30d"
```

#### 3.4 Last 3 months

```bash
curl "http://localhost:5000/api/stats?window=3m"
```

#### 3.5 Last 1 year

```bash
curl "http://localhost:5000/api/stats?window=1y"
```

#### 3.6 Alternative: Using `days` parameter

```bash
curl "http://localhost:5000/api/stats?days=7"
curl "http://localhost:5000/api/stats?days=30"
```

**Response (200 OK):**

```json
{
  "window": "7d",
  "window_days": 7,
  "start_date": "2026-02-09",
  "end_date": "2026-02-15",
  "stats": {
    "avg_weight": 72.14,
    "avg_body_fat": 18.63,
    "avg_calories": 2132.5,
    "avg_steps": 8045.8,
    "avg_sleep": 7.36,
    "total_entries": 6
  }
}
```

**Error Cases:**

- **400 Bad Request:** Invalid window format or non-positive `days` parameter
- **404 Not Found:** No data available for the requested window

---

## Window Parameter Formats

The `window` parameter accepts:

- `7d` — last 7 days
- `30d` — last 30 days
- `3m` — last 3 months (90 days)
- `1y` — last 1 year (365 days)
- Omitted — all-time stats

---

## Troubleshooting

### "Connection refused" or "404 Not Found"

- Make sure the Flask app is running: `uv run python app.py`

### "No data available" (404)

- You need to create or import entries first:
  - Use the POST endpoint to create entries, or
  - Run `uv run python scripts/import_data.py data/health_data.csv`

### "Date already exists" (409)

- An entry for that date already exists in the database. Use a different date.
