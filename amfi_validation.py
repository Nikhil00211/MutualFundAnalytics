"""
AMFI Code Referential Integrity Check
--------------------------------------
Validates that amfi_code values in dependent datasets (NAV history,
investor transactions, portfolio holdings) all exist in the fund master
dataset. Flags orphan codes — records that reference a fund not present
in the master table — which would silently break downstream joins.

Usage:
    python validate_amfi_codes.py
"""

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

DATA_DIR = Path("data/raw")
FUND_MASTER_FILE = DATA_DIR / "01_fund_master.csv"

# Files to validate against the fund master, keyed by a short label for reporting.
DEPENDENT_FILES = {
    "nav_history": DATA_DIR / "02_nav_history.csv",
    "scheme_performance": DATA_DIR / "07_scheme_performance.csv",
    "investor_transactions": DATA_DIR / "08_investor_transactions.csv",
    "portfolio_holdings": DATA_DIR / "09_portfolio_holdings.csv",
}


def load_codes(path: Path, column: str = "amfi_code") -> set:
    """Read a CSV and return the set of unique values in the given column."""
    df = pd.read_csv(path, encoding="utf-8", usecols=[column])
    return set(df[column].dropna())


def check_against_master(master_codes: set, child_codes: set, child_name: str) -> dict:
    """
    Compare a dependent dataset's codes against the fund master.

    Returns a dict with:
        orphan_codes   -> in child but NOT in master (data integrity problem)
        unused_codes   -> in master but NOT in child (informational only)
    """
    orphan_codes = child_codes - master_codes
    unused_codes = master_codes - child_codes

    if orphan_codes:
        logger.error(
            "%s: %d orphan amfi_code(s) not found in fund master: %s",
            child_name, len(orphan_codes), sorted(orphan_codes),
        )
    else:
        logger.info("%s: all amfi_codes exist in fund master", child_name)

    return {"orphan_codes": orphan_codes, "unused_codes": unused_codes}


def main() -> None:
    if not FUND_MASTER_FILE.exists():
        raise FileNotFoundError(f"Fund master file not found: {FUND_MASTER_FILE}")

    master_codes = load_codes(FUND_MASTER_FILE)
    logger.info("Fund master contains %d unique amfi_code(s)", len(master_codes))

    results = {}
    for name, path in DEPENDENT_FILES.items():
        if not path.exists():
            logger.warning("Skipping %s — file not found: %s", name, path)
            continue

        child_codes = load_codes(path)
        results[name] = check_against_master(master_codes, child_codes, name)

    # Final summary
    print("\n" + "=" * 60)
    print("REFERENTIAL INTEGRITY SUMMARY")
    print("=" * 60)
    any_orphans = False
    for name, result in results.items():
        status = "FAIL" if result["orphan_codes"] else "PASS"
        if result["orphan_codes"]:
            any_orphans = True
        print(f"{name:25s} | {status} | orphan_codes={len(result['orphan_codes'])} | unused_codes={len(result['unused_codes'])}")

    print("=" * 60)
    print("Overall: " + ("❌ Issues found" if any_orphans else "✅ All checks passed"))


if __name__ == "__main__":
    main()