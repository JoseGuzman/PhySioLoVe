#!/usr/bin/env python
"""
Import health data from CSV/TSV file

Author: Jose Guzman
Created: Thu Feb  5 09:29:27 CET 2026

Usage: uv run python scripts/import_data.py data/health_data.csv
"""

import sys
from datetime import date as Date
from datetime import datetime
from pathlib import Path

import pandas as pd

from app import HealthEntry, app, db

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def parse_time(time_str: str) -> float | None:
    """
    Parse a time string in 'h:mm[:ss]' format and return total hours in
    decimal format with an accuracy of 2 floating points.

    Parameters
    ----------
    time_str : str
        Time string in the format 'h:mm' or 'h:mm:ss' (e.g. '2:30', '1:45:20').

    Returns
    -------
    float or None
        Total time in hours, rounded to two decimal places.
        Returns None for empty, NaN, or placeholder values ('--').

    Raises
    ------
    ValueError
        If the input string does not match the expected time format.

    Examples
    --------
    >>> parse_time("2:30")
    2.5
    >>> parse_time("1:15:00")
    1.25
    >>> parse_time("--")
    None
    >>> parse_time("2:60")
    Traceback (most recent call last):
    ...
    ValueError: Invalid time format: '2:60'. Expected 'h:mm[:ss]'
    >>> parse_time("2:30:61")
    Traceback (most recent call last):
    ...
    ValueError: Invalid time format: '2:30:61'. Expected 'h:mm[:ss]'
    """
    if time_str is None or pd.isna(time_str):
        return None

    if not isinstance(time_str, str):
        raise TypeError(f"Expected string, got {type(time_str).__name__}")

    time_str = time_str.strip()

    if time_str == "" or time_str == "--":
        return None
    try:
        # time_str is guaranteed to be string already here
        parts = time_str.split(":")

        if len(parts) < 2:
            raise ValueError(f"Invalid time format: {time_str!r}. Expected 'h:mm[:ss]'")

        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2]) if len(parts) == 3 else 0

        # check proper time guarantees
        if 0 < hours > 24:
            raise ValueError("Hours cannot be negative")
        if 0 <= minutes >= 60:
            raise ValueError("Minutes must be between 0 and 59")
        if 0 <= seconds >= 60:
            raise ValueError("Seconds must be between 0 and 59")

        return round(hours + minutes / 60 + seconds / 3600, 2)  # when everything works

    # catch 2: or 2:xx, to provide info on format
    except ValueError as exc:
        raise ValueError(
            f"Invalid time format: {time_str!r}. Expected 'h:mm[:ss]'"
        ) from exc


def parse_number(value: str) -> float | None:
    """
    Parse number with comma as decimal separator

    Parameters
    ----------
    value : str
        Number string in the format (e.g. '2,30' or '2,30').

    Returns
    -------
    float or None
        The number as floating point
        Returns None for empty, NaN, or placeholder values ('--').

    Raises
    ------
    ValueError
        If the input string does not match the expected time format.

    Examples
    --------
    >>> parse_number('2.3')
    2.3

    """

    if pd.isna(value) or value == "--" or value == "":
        return None
    try:
        return float(str(value).replace(",", "."))
    except ValueError as exc:
        msg = f"{value!r} invalid argument; expected number, got {type(value).__name__}"
        raise ValueError(msg) from exc

    return None


def parse_date(date_str: str) -> Date | None:
    """
    Parse a date string in common formats and return a `date`.

    Accepts formats:
    - dd/mm/YYYY
    - YYYY-mm-dd
    - mm/dd/YYYY
    - dd-mm-YYYY

    Returns None for NaN/empty/placeholder values or if parsing fails.
    """
    if pd.isna(date_str) or date_str == "--" or date_str == "":
        return None

    # Try different date formats
    formats = ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date()
        except ValueError:
            continue
    return None


def import_data(filepath: str) -> float | None:
    """
    Imports health data from a CSV or TSV file into the database.
    The file should have a 'Date' column and may include columns for
    weight, body fat percentage, calories, steps, sleep total, sleep quality,
    and observations. The function will attempt to map columns based on common keywords.

    Parameters
    ----------
    filepath : str
        The path to the CSV or TSV file containing health data.

    Returns
    -------
    float or None
        Total time in hours, rounded to two decimal places.
        Returns None for empty, NaN, or placeholder values ('--').

    Raises
    ------
    ValueError
        If the input string does not match the expected time format.
    """

    # Import data from CSV/TSV file
    print(f"\n📊 Importing data from {filepath}...")

    # Detect separator (CSV or TSV)
    sep = "t" if filepath.endswith(".tsv") else ","
    # Read file
    df = pd.read_csv(filepath, sep=sep, encoding="utf-8")

    # Print column names to help debug
    print(f"\n📋 Found columns: {list(df.columns)}\n")

    # Map column names (handle variations)
    column_map = {}
    for col in df.columns:
        col_lower = col.lower().strip()
        if "date" in col_lower:
            column_map["date"] = col
        elif "weight" in col_lower and "kg" in col_lower:
            column_map["weight"] = col
        elif "body" in col_lower and "fat" in col_lower:
            column_map["body_fat"] = col
        elif "calorie" in col_lower:
            column_map["calories"] = col
        elif "step" in col_lower:
            column_map["steps"] = col
        elif "sleep total" in col_lower:
            column_map["sleep_total"] = col
        elif "sleep quality" in col_lower:
            column_map["sleep_quality"] = col
        elif "observation" in col_lower:
            column_map["observations"] = col

    print(f"📌 Mapped columns: {column_map}\n")

    if "date" not in column_map:
        print("❌ Error: Could not find a 'Date' column!")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)

    added = 0
    skipped = 0
    errors = 0

    with app.app_context():
        for idx, row in df.iterrows():
            try:
                date = parse_date(row[column_map["date"]])
                if not date:
                    errors += 1
                    continue

                # Check if entry exists
                existing = HealthEntry.query.filter_by(date=date).first()
                if existing:
                    skipped += 1
                    continue

                # Create new entry
                entry = HealthEntry(
                    date=date,
                    weight=parse_number(row.get(column_map.get("weight")))
                    if "weight" in column_map
                    else None,
                    body_fat=parse_number(row.get(column_map.get("body_fat")))
                    if "body_fat" in column_map
                    else None,
                    calories=int(parse_number(row.get(column_map.get("calories"))))
                    if "calories" in column_map
                    and parse_number(row.get(column_map.get("calories")))
                    else None,
                    steps=int(parse_number(row.get(column_map.get("steps"))))
                    if "steps" in column_map
                    and parse_number(row.get(column_map.get("steps")))
                    else None,
                    sleep_total=parse_time(row.get(column_map.get("sleep_total")))
                    if "sleep_total" in column_map
                    else None,
                    sleep_quality=row.get(column_map.get("sleep_quality"))
                    if "sleep_quality" in column_map
                    and pd.notna(row.get(column_map.get("sleep_quality")))
                    and row.get(column_map.get("sleep_quality")) != "--"
                    else None,
                    observations=row.get(column_map.get("observations"))
                    if "observations" in column_map
                    and pd.notna(row.get(column_map.get("observations")))
                    else None,
                )

                db.session.add(entry)
                added += 1

            except Exception as e:
                errors += 1
                print(f"⚠️  Error on row {idx + 1}: {e}")  # type: ignore
                continue

        db.session.commit()

    print("✓ Import complete!")
    print(f"  • Added: {added} entries")
    print(f"  • Skipped: {skipped} entries (already exist)")
    print(f"  • Errors: {errors} entries (invalid data)")

    total = HealthEntry.query.count()
    print(f"  • Total in database: {total}\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/import_data.py <path_to_file>")
        print("Example: uv run python scripts/import_data.py data/health_data.csv")
        sys.exit(1)

    myfilepath = sys.argv[1]
    if not Path(myfilepath).exists():
        print(f"Error: File '{myfilepath}' not found")
        sys.exit(1)

    import_data(filepath=myfilepath)
