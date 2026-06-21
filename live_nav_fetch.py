"""
Live NAV Fetcher
-----------------
Pulls historical NAV data for multiple mutual fund schemes from the
mfapi.in API and saves each one as a separate CSV inside data/raw/.

Usage:
    python live_nav_fetch.py
"""

import logging
from pathlib import Path

import pandas as pd
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

API_URL_TEMPLATE = "https://api.mfapi.in/mf/{scheme_code}"
REQUEST_TIMEOUT_SECONDS = 10
OUTPUT_DIR = Path("data/raw")

# All schemes to fetch, including HDFC Top 100. Defined once, at the top,
# so it's visible before any function that depends on it.
SCHEMES = {
    "hdfc_top100": "125497",
    "sbi_bluechip": "119551",
    "icici_bluechip": "120503",
    "nippon_largecap": "118632",
    "axis_bluechip": "119092",
    "kotak_bluechip": "120841",
}


def fetch_nav_data(scheme_code: str) -> dict:
    """Call the mfapi.in API for a scheme code and return the parsed JSON."""
    url = API_URL_TEMPLATE.format(scheme_code=scheme_code)
    logger.info("Requesting NAV data for scheme %s", scheme_code)

    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()  # raises HTTPError for 4xx/5xx responses

    payload = response.json()

    if "data" not in payload or not payload["data"]:
        raise ValueError(f"No NAV data returned for scheme code {scheme_code}")

    return payload


def build_nav_dataframe(payload: dict) -> pd.DataFrame:
    """Convert the API payload into a clean, typed dataframe."""
    df = pd.DataFrame(payload["data"])

    # Source columns are strings; convert to proper types for downstream analysis.
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    if df["date"].isnull().any() or df["nav"].isnull().any():
        logger.warning("Some rows had unparseable date/nav values and were set to NaT/NaN")

    # Attach scheme metadata if available, useful once multiple funds are combined.
    meta = payload.get("meta", {})
    df["scheme_code"] = meta.get("scheme_code")
    df["scheme_name"] = meta.get("scheme_name")

    df = df.sort_values("date").reset_index(drop=True)
    return df


def save_nav_data(df: pd.DataFrame, output_path: Path) -> None:
    """Save a NAV dataframe to CSV, creating the target folder if needed."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info("Saved %d rows to %s", len(df), output_path)


def fetch_all_schemes(schemes: dict[str, str]) -> None:
    """Fetch and save NAV history for every scheme in the given mapping."""
    for name, code in schemes.items():
        try:
            payload = fetch_nav_data(code)
            df = build_nav_dataframe(payload)
            output_file = OUTPUT_DIR / f"{name}_nav.csv"
            save_nav_data(df, output_file)
        except requests.exceptions.RequestException as exc:
            logger.error("Network/API error while fetching %s (%s): %s", name, code, exc)
        except ValueError as exc:
            logger.error("Data error for %s (%s): %s", name, code, exc)
        except Exception as exc:
            logger.error("Unexpected error for %s (%s): %s", name, code, exc)


def main() -> None:
    logger.info("Starting NAV fetch for %d schemes", len(SCHEMES))
    fetch_all_schemes(SCHEMES)
    logger.info("NAV fetch complete")


if __name__ == "__main__":
    main()