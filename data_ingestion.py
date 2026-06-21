"""
Mutual Fund Data Ingestion
---------------------------
Scans a folder for CSV files, profiles each one (shape, dtypes, missing
values, duplicates, basic stats), and writes a consolidated text report.

Usage:
    python ingest_mutual_fund_data.py
    python ingest_mutual_fund_data.py --folder data/raw --report out/report.txt
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def profile_dataframe(df: pd.DataFrame, name: str) -> str:
    """Build a readable text profile of a single dataframe."""
    lines = [
        f"\n{'=' * 60}",
        f"FILE: {name}",
        "=" * 60,
        f"Shape: {df.shape}",
        "\nColumns:",
        ", ".join(df.columns.astype(str)),
        "\nData Types:",
        df.dtypes.to_string(),
    ]

    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2) if len(df) else missing
    missing_summary = pd.DataFrame({"missing": missing, "missing_%": missing_pct})
    lines.append("\nMissing Values:")
    lines.append(missing_summary[missing_summary["missing"] > 0].to_string())
    if missing.sum() == 0:
        lines.append("None")

    dup_count = df.duplicated().sum()
    lines.append(f"\nDuplicate Rows: {dup_count}")

    numeric_df = df.select_dtypes(include="number")
    if not numeric_df.empty:
        lines.append("\nNumeric Summary:")
        lines.append(numeric_df.describe().T.to_string())

    lines.append("\nFirst 5 Rows:")
    lines.append(df.head().to_string())

    return "\n".join(lines)


def ingest_folder(folder_path: Path) -> list[str]:
    """Read every CSV in folder_path and return a list of profile reports."""
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    csv_files = sorted(folder_path.glob("*.csv"))
    if not csv_files:
        logger.warning("No CSV files found in %s", folder_path)
        return []

    reports = []
    for file_path in csv_files:
        logger.info("Reading %s", file_path.name)
        try:
            df = pd.read_csv(file_path, encoding="utf-8")
            reports.append(profile_dataframe(df, file_path.name))
        except Exception as exc:
            logger.error("Failed to read %s: %s", file_path.name, exc)
            reports.append(f"\nFILE: {file_path.name}\nERROR: {exc}")

    return reports


def write_report(reports: list[str], report_path: Optional[Path]) -> None:
    full_text = "\n".join(reports) if reports else "No files processed."
    print(full_text)

    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(full_text, encoding="utf-8")
        logger.info("Report saved to %s", report_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile CSV files for mutual fund data ingestion.")
    parser.add_argument("--folder", default="data/raw", help="Folder containing CSV files (default: data/raw)")
    parser.add_argument("--report", default=None, help="Optional path to save the report as a .txt file")
    args = parser.parse_args()

    logger.info("Starting mutual fund data ingestion")
    reports = ingest_folder(Path(args.folder))
    write_report(reports, Path(args.report) if args.report else None)
    logger.info("Processed %d file(s)", len(reports))


if __name__ == "__main__":
    main()