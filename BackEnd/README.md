# 📊 FRED Economic Data API

This project is a FastAPI application that queries, caches, and serves economic data from the [Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/) API.

It includes intelligent caching with MongoDB to reduce redundant API calls and support repeated data retrieval by date and series ID.

---

## 🔧 Setup

### 1. Environment Variables

Create a `.env` file or export in your shell:

```bash
FRED_API_KEY=your_fred_api_key_here
```

### 2. Dependencies

Install requirements:

```bash
pip install -r requirements.txt
```

Make sure MongoDB is running (local or remote).

---

## 📂 MongoDB Structure

### `fred_release_summaries`
Stores release metadata per date.

```json
{
  "date": "2025-05-19",
  "timestamp": "...",
  "releases": [
    {
      "release_id": 17,
      "release_name": "H.10 Foreign Exchange Rates",
      "series": [
        {
          "series_id": "DTWEXBGS",
          "title": "...",
          "frequency": "D"
        }
      ]
    }
  ]
}
```

### `fred_series_observations`
Stores actual time series data for each `series_id`.

```json
{
  "series_id": "UNRATE",
  "last_fetched": "...",
  "data": [
    { "date": "2023-01-01", "value": 3.5 },
    { "date": "2023-02-01", "value": 3.6 }
  ]
}
```

---

## 🚀 API Endpoints

### `/fred/daily_series_ids?date=YYYY-MM-DD`
Returns release metadata and all series IDs published on the given date.

- **Method**: `GET`
- **Returns**: JSON array of releases with series metadata

---

### `/fred/daily_series_data?date=YYYY-MM-DD`
Returns **full time series data** for each series released on a specific date.

- ✅ Checks MongoDB first
- 🌀 Falls back to live FRED API if not cached
- 🧠 Caches results in MongoDB

---

### `/fred/get_series?series_id=...`
Returns full time series data for a specific `series_id`.

- **Method**: `GET`
- **Returns**: List of `{date, value}` records

---

## 🧠 Usage Notes

- FRED API rate limits apply. We handle `429` errors and retry gracefully.
- Data is automatically cached by date and series for future reuse.
- Time series values are cleaned, converted to floats, and indexed by date.

---

## 📌 TODO / Improvements

- [ ] Add authentication for sensitive endpoints
- [ ] Add Swagger schema for better UI
- [ ] Add CLI utility for batch backfilling
- [ ] Add TTL index or refresh strategy for stale series

---

## 📞 Contact

For support or questions, contact: **youremail@example.com**
