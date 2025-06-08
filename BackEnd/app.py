from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from datetime import datetime
import os
import pandas as pd
import json
import requests
from scrapers.fred_economic_release import fetch_fred_releases_api, get_releases_published_on, get_series_ids_for_release
import time
import logging
import re

# uvicorn app:app --reload

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["heta"]
collection = db["daily_series_ids"]
summary_collection = db["fred_release_summaries"]
series_data_collection = db["fred_series_observations"]


# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("dailyseries.log"),
        logging.StreamHandler()  # Also output to console
    ]
)

logger = logging.getLogger(__name__)
app = FastAPI(
    title="My API",
    version="1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to specific domains later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs('static/plots', exist_ok=True)
os.makedirs('models', exist_ok=True)

@app.get("/")
def home():
    return {"name": "hello_world"}
            
@app.get('/fred/get_series')
# If this URL is accessed arbitrarily, it will attempt to make a connection to the db which is not correct. There needs to be some form of authentication

def get_series(
    series_id: str = Query(..., description="Series ID like GFDGDPA188S"),
):
    fred_api_key = os.environ.get('FRED_API_KEY')
    if not fred_api_key:
        raise HTTPException(status_code=500, detail="FRED API key not set in environment")

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": fred_api_key,
        "file_type": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="FRED observation fetch failed")

        data = response.json()
        observations = data.get("observations", [])
        if not observations:
            raise HTTPException(status_code=404, detail="No observations found")

        # Clean and transform data as needed
        df = pd.DataFrame(observations)
        # Example: convert values (if exists) to float, parse dates, etc.
        if "value" in df.columns:
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime('%Y-%m-%d')
        df = df.drop(columns=['realtime_start', 'realtime_end'])

        df.dropna(subset=["value"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        df_key = {
            "Series Id": series_id,
            "observations": df.to_dict(orient='records')
        }

        return JSONResponse(
            content=df_key["observations"],
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@app.get('/fred/get_metadata')

def fred_get_metadata(
    series_id: str = Query(..., description="Series ID like GFDGDPA188S")
):
    """
    Fetches metadata for a FRED series and returns it as a one-row DataFrame.
    """
    fred_api_key = os.environ.get("FRED_API_KEY")
    if not fred_api_key:
        raise HTTPException(status_code=500, detail="FRED API key not set in environment")

    url = "https://api.stlouisfed.org/fred/series"
    params = {
        "series_id": series_id,
        "api_key": fred_api_key,
        "file_type": "json"
    }

    response = requests.get(url, params=params, timeout=30)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="FRED metadata fetch failed")

    data = response.json()
    series_list = data.get("seriess", [])

    if not series_list:
        raise HTTPException(status_code=404, detail="No metadata found")

    df = pd.DataFrame(series_list)
    df["series_id"] = series_id  # Make sure this column is consistent

    # Optionally assign a primary key id (for DB insert)
    # Clean and transform data
    try:
        df.dropna(inplace=True)
        df["observation_start"] = pd.to_datetime(df["observation_start"], errors='coerce').dt.date
        df["observation_end"] = pd.to_datetime(df["observation_end"], errors='coerce').dt.date
        df.drop(columns=['realtime_start', 'realtime_end'], errors='ignore', inplace=True)
    except Exception as e:
        print("Data transformation failed:", e)

    return JSONResponse(content=json.loads(df.to_json(orient="records", date_format="iso")))


@app.get('/fred/dailyseries_ids')
def fred_daily_series_ids(date: str = Query(...)):
    try:
        fred_api_key = os.environ.get("FRED_API_KEY")
        releases = fetch_fred_releases_api(date, fred_api_key)
        all_series_ids = []

        for release in releases:
            release_id = release["id"]
            try:
                series_ids = get_series_ids_for_release(release_id, fred_api_key)
                all_series_ids.extend(series_ids)
            except Exception as sub_e:
                print(f"Failed for release ID {release_id}: {sub_e}")

        return JSONResponse(content={"date": date, "series_ids": all_series_ids}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get('/fred/daily_series_ids')
def fred_daily_series(date: str = Query(...)):
    api_key = os.environ.get("FRED_API_KEY")
    releases = get_releases_published_on(date, api_key)
    all_series = check_releases(date, releases, api_key)
    return JSONResponse(
        content=json.loads(json.dumps(all_series, default=str)),
        status_code=200
    )

def safe_parse_last_updated(ts: str) -> datetime:
    # print("ts: ", ts)
    # print("ts-3", ts[-3])
    # print("len: ", len(ts.split()[-1]))
    if ts[-3] in ['+', '-']:
        ts += "00"  # Convert -05 → -0500
        # print("ts_edited: ", ts)
        # print("return: ", datetime.strptime(ts, "%Y-%m-%d %H:%M:%S%z"))
    return datetime.strptime(ts, "%Y-%m-%d")

def clean_to_date(value: str) -> datetime.date:
    """
    Extracts the YYYY-MM-DD from a timestamp string using regex.
    Example: '2025-05-15 07:34:01-05' → datetime.date(2025, 5, 15)
    """
    match = re.match(r"(\d{4}-\d{2}-\d{2})", value)
    if not match:
        raise ValueError(f"Could not extract date from: {value}")
    return datetime.strptime(match.group(1), "%Y-%m-%d")

# for_later = []
def check_releases(date, releases, api_key, depth=0, max_depth=5):
    all_series = []
    for_later = []

    cached_doc = summary_collection.find_one({"date": date})
    if cached_doc:
        logger.info(f"Using cached FRED data for date {date}")
        return cached_doc["releases"]

    for release in releases:
        
        release_id = release["id"]
        release_name = release["name"]
        logger.info(f"Checking release: {release_name} (ID: {release_id})")

        # 1. Check if this release already exists in MongoDB
        mongo_series = list(collection.find({"release_id": release_id}))
        
        # Determine if we need to fetch from API
        print("HERE")
        should_call_api = True
        if mongo_series:
            latest_cached = max([doc.get("date_cached", datetime.min) for doc in mongo_series])
            # print("Latest cached: ", latest_cached)
            latest_updated = max([clean_to_date(doc["last_updated"]) for doc in mongo_series if "last_updated" in doc])

            
            # print("Latest Updated: ", latest_updated)
            # print("Latest cached: ", str(latest_cached))
            # print("Last updated:", str(latest_updated))

            if latest_cached > latest_updated:
                # Cached data is up-to-date
                logger.info(f"Using cached data for release {release_id} (cached: {latest_cached.date()}, updated: {latest_updated.date()})")

                all_series.append({
                    "release_name": release_name,
                    "release_id": release_id,
                    "series": [
                        {
                            "series_id": s["series_id"],
                            "title": s["title"],
                            "frequency": s["frequency"]
                        } for s in mongo_series
                    ]
                })
                should_call_api = False

        if should_call_api:
            logger.info(f"Fetching series from FRED API for release ID: {release_id}")
            try:
                series_list = get_series_ids_for_release(release_id, api_key)
                if series_list["series_data"]:
                    logger.info(f"First series ID received: {series_list['series_data'][0]['series_id']}")
            except requests.exceptions.HTTPError as http_err:
                status_code = http_err.response.status_code if http_err.response else None
                if status_code == 429:
                    logger.warning(f"Rate limit hit for release ID: {release_id}")
                    for_later.append(release)
                else:
                    logger.error(f"HTTP error for release ID {release_id}: {status_code}")
                series_list = {"series_data": []}
            except Exception as e:
                logger.error(f"General error for release ID {release_id}: {str(e)}")
                series_list = {"series_data": []}

            # Insert each series document into MongoDB
            for s in series_list["series_data"]:
                s_doc = {
                    "series_id": s["series_id"],
                    "title": s["title"],
                    "frequency": s["frequency"],
                    "release_id": release_id,
                    "release_name": release_name,
                    "last_updated": s["last_updated"],
                    "date_cached": datetime.utcnow()
                }
                collection.update_one(
                    {"series_id": s["series_id"], "release_id": release_id},
                    {"$set": s_doc},
                    upsert=True
                )
                logger.info(f"MongoDB upserted series: {s['series_id']} (release ID: {release_id})")


            all_series.append({
                "release_name": release_name,
                "release_id": release_id,
                "series": [
                    {
                        "series_id": s["series_id"],
                        "title": s["title"],
                        "frequency": s["frequency"]
                    } for s in series_list["series_data"]
                ]
            })

    # Retry failed releases
    if for_later and depth < max_depth:
        logger.info(f"Retrying {len(for_later)} releases after rate limit. Retry #{depth + 1}")
        all_series += check_releases(for_later, api_key, depth=depth + 1, max_depth=max_depth)
    elif for_later:
        logger.warning(f"Max retry depth reached. Could not process {len(for_later)} releases.")

    # Store the full all_series summary in its own collection
    summary_doc = {
    "date": date,  # pass this in as a function parameter
    "timestamp": datetime.utcnow(),
    "releases": all_series
    }

    summary_collection.update_one(
        {"date": date},
        {"$set": summary_doc},
        upsert=True
    )
    logger.info(f"Cached all_series summary in MongoDB for date {date}")

    return all_series

@app.get("/fred/daily_series_data")
def get_series_data_for_date(date: str = Query(...)):
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="FRED API key not set")

    # Step 1: Check summary cache
    summary_doc = summary_collection.find_one({"date": date})
    if summary_doc:
        releases = summary_doc["releases"]
    else:
        # Step 2: Fallback to live fetch
        logger.info(f"No cached summary for {date}. Fetching from FRED...")
        releases_raw = get_releases_published_on(date, api_key)
        releases = check_releases(date, releases_raw, api_key)
        # Note: check_releases() already stores to summary_collection

    # Step 3: Get all unique series_ids
    series_ids = []
    for release in releases:
        for s in release["series"]:
            series_ids.append(s["series_id"])

    # Step 4: Fetch series data for each ID
    all_data = {}
    for sid in series_ids:
        cached = series_data_collection.find_one({"series_id": sid})
        if cached:
            all_data[sid] = cached["data"]
            continue

        # Fetch from FRED API
        try:
            response = requests.get(
                "https://api.stlouisfed.org/fred/series/observations",
                params={
                    "series_id": sid,
                    "api_key": api_key,
                    "file_type": "json"
                }, timeout=30
            )
            response.raise_for_status()
            observations = response.json().get("observations", [])

            df = pd.DataFrame(observations)
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
            df.drop(columns=["realtime_start", "realtime_end"], inplace=True, errors="ignore")
            df.dropna(subset=["value"], inplace=True)

            records = df.to_dict(orient="records")

            # Cache it
            series_data_collection.update_one(
                {"series_id": sid},
                {"$set": {"series_id": sid, "data": records, "last_fetched": datetime.utcnow()}},
                upsert=True
            )

            all_data[sid] = records

        except Exception as e:
            logger.warning(f"Failed to fetch data for {sid}: {e}")
            all_data[sid] = []

    return JSONResponse(content=all_data, status_code=200)


    # No matching date in the file so read from fred_economic_release.csv
    # Otherwise, get the info from the fred_economic_release.csv and fetch from API
    
    # full_series_list = []
    # for release in all_series:
    #     series_list = release["series"]
    #     full_series_list.append(series_list)
    
    # return JSONResponse(
    #     content=json.loads(full_series_list.to_json(oritn="records", date_format="iso")),
    #     status_code=200
    # )

    # print(full_series_list)

    # existing_data = {}
    # url = 'http://127.0.0.1:8000/fred/get_series'
    # for series in full_series_list:
    #     try:
    #         params= {
    #             "series_id": series
    #         }
    #         r = requests.get(url=url, params=params)
    #         out = json.loads(r)
    #         existing_data[series] = out
    #     except Exception as e:
    #         return JSONResponse(
    #             content={"error": str(e)},
    #             status_code=500
    #         )
    #     return JSONResponse(
    #     content=json.loads(existing_data.to_json(orient="records", date_format="iso")),  # return just the records for this date
    #     status_code=200
    # )