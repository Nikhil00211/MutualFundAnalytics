"""
Categorical Consistency Check
------------------------------
Profiles categorical columns in the fund master dataset and flags
potential inconsistencies — case differences, leading/trailing whitespace,
or near-duplicate labels — that would silently fragment groupings in
downstream analysis (e.g. "SBI Mutual Fund" vs "sbi mutual fund ").

Usage:
    python categorical_consistency_check.py
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

FUND_MASTER_FILE = Path("data/raw/01_fund_master.csv")

# Columns to profile. Edit this list if the schema changes.
CATEGORICAL_COLUMNS = [
    "fund_house",
    "category",
    "sub_category",
    "plan",
    "risk_category",
    "sebi_category_code",
]


def profile_column(df: pd.DataFrame, column: str) -> dict:
    """
    Profile a single categorical column: unique values, counts, and any
    values that collide once case and whitespace are normalized.
    """
    series = df[column].dropna()
    unique_values = sorted(series.unique())

    # Group raw values by a normalized form (lowercase, stripped) to catch
    # values that are "the same" but stored inconsistently.
    normalized_groups: dict[str, list[str]] = {}
    for value in unique_values:
        key = str(value).strip().lower()
        normalized_groups.setdefault(key, []).append(value)

    collisions = {key: vals for key, vals in normalized_groups.items() if len(vals) > 1}

    return {
        "unique_count": len(unique_values),
        "values": unique_values,
        "value_counts": series.value_counts().to_dict(),
        "collisions": collisions,
    }


def main() -> None:
    if not FUND_MASTER_FILE.exists():
        raise FileNotFoundError(f"File not found: {FUND_MASTER_FILE}")

    df = pd.read_csv(FUND_MASTER_FILE, encoding="utf-8")
    logger.info("Loaded %d rows from %s", len(df), FUND_MASTER_FILE.name)

    any_collisions = False

    for column in CATEGORICAL_COLUMNS:
        if column not in df.columns:
            logger.warning("Column '%s' not found in dataset — skipping", column)
            continue

        result = profile_column(df, column)

        print("\n" + "=" * 60)
        print(f"COLUMN: {column}")
        print("=" * 60)
        print(f"Unique values: {result['unique_count']}")
        for value, count in result["value_counts"].items():
            print(f"  - {value!r}: {count}")

        if result["collisions"]:
            any_collisions = True
            print("\n⚠️  Potential inconsistencies (same value, different formatting):")
            for normalized, variants in result["collisions"].items():
                print(f"  {variants} all normalize to {normalized!r}")
        else:
            print("\n✅ No case/whitespace inconsistencies detected")

    print("\n" + "=" * 60)
    print("Overall: " + ("⚠️  Inconsistencies found — review above" if any_collisions else "✅ All categorical columns are clean"))


if __name__ == "__main__":
    main()