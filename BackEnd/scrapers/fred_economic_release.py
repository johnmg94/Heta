import os
import requests
import datetime

def fetch_fred_releases_api(
    date_str: str = None,
    api_key: str = None
):
    """
    Fetches FRED releases for a given date using the FRED API.
    Returns a list of dicts: {Release, ReleaseID, ReleaseDate}.
    """
    # Get API key
    if api_key is None:
        api_key = os.environ.get('FRED_API_KEY')
    if not api_key:
        raise RuntimeError("FRED API key not set.")

    # Determine the date in YYYY-MM-DD
    if date_str is None:
        dt = datetime.date.today()
    else:
        try:
            if "-" in date_str:
                if len(date_str.split("-")[0]) == 4:
                    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                else:
                    dt = datetime.datetime.strptime(date_str, "%m-%d-%Y").date()
            else:
                raise ValueError("Date format not recognized")
        except Exception as e:
            raise ValueError(f"Invalid date format: {e}")
    formatted_date = dt.strftime("%Y-%m-%d")

    # Query FRED releases for that date
    url = "https://api.stlouisfed.org/fred/releases"
    params = {
        "api_key": api_key,
        "file_type": "json",
        "realtime_start": formatted_date,
        "realtime_end": formatted_date
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    releases = response.json().get("releases", [])

    return releases

def get_releases_for_date(date: str, api_key: str = None):
    url = "https://api.stlouisfed.org/fred/releases"

    # Get API key
    if api_key is None:
        api_key = os.environ.get('FRED_API_KEY')
    if not api_key:
        raise RuntimeError("FRED API key not set.")
    
    params = {
        "api_key": api_key,
        "file_type": "json",
        "realtime_start": date,
        "realtime_end": date
    }
    
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json().get("releases", [])

def get_series_ids_for_release(release_id: int, api_key: str = None):
    url = "https://api.stlouisfed.org/fred/release/series"

    # Get API key
    if api_key is None:
        api_key = os.environ.get('FRED_API_KEY')
    if not api_key:
        raise RuntimeError("FRED API key not set.")
    
    params = {
        "release_id": release_id,
        "api_key": api_key,
        "file_type": "json"
    }
    try:
        r = requests.get(url, params=params)
        if r.status_code == 429:
            series_data = [{}]
            return {
                "status_code": r.status_code,
                "series_data": series_data
            }
        
        r.raise_for_status()
        series = r.json().get("seriess", [])

        sorted_series = sorted(series, key=lambda s: s.get("popularity", 0), reverse=True)[:5]

        series_data = [
                    {
                "series_id": s["id"],
                "title": s["title"],
                "frequency": s["frequency_short"],
                "units_short": s["units_short"],
                "seasonal_adjustment_short": s["seasonal_adjustment_short"],
                "last_updated": s["last_updated"],
                "notes": s.get("notes", ""),
                "popularity": s.get("popularity", 0)
            } for s in sorted_series]
        return {
            "status_code": 200,
            "series_data": series_data
        }

    except requests.RequestException as e:
        return {
            "status_code": r.status_code,
            "series_data": series_data,
        }

def get_releases_published_on(date: str, api_key: str = None):
    # Get API key
    if api_key is None:
        api_key = os.environ.get('FRED_API_KEY')
    if not api_key:
        raise RuntimeError("FRED API key not set.")
    
    all_releases = fetch_fred_releases_api(date, api_key)
    confirmed_releases = []

    for release in all_releases:
        release_id = release['id']
        # Check the actual release dates
        url = f"https://api.stlouisfed.org/fred/release/dates"
        params = {
            "api_key": api_key,
            "release_id": release_id,
            "file_type": "json"
        }
        r = requests.get(url, params=params)
        dates = [d["date"] for d in r.json().get("release_dates", [])]
        if date in dates:
            confirmed_releases.append(release)

    return confirmed_releases

# Example usage:
if __name__ == "__main__":
    import json
#     # results = fetch_fred_releases_api("05-17-2025")


    # results = get_releases_published_on("2025-05-19")

    # out = [release.get("name") for release in results if "name" in release]
    # print(out)
    # print(len(out))


#     series_ids = get_series_ids_for_release("13")
    # print(results)
#     print(series_ids)

#     length = 0
#     for item in series_ids["series_data"]:
#         length += 1
    
#     print("Length: ", length)
    # for r in results:
        # print(r)
