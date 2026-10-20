import sqlite3
from pathlib import Path

import pandas as pd


# Locate the main project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Locate the existing SQLite database
DATABASE_PATH = PROJECT_DIR / "crime_data.db"


def get_connection():
    """Create a connection to the existing crime database."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Crime database not found: {DATABASE_PATH}"
        )

    return sqlite3.connect(DATABASE_PATH)


def get_total_crimes():
    """Return the total number of stored crime records."""

    with get_connection() as connection:
        result = pd.read_sql_query(
            "SELECT COUNT(*) AS total FROM crimes",
            connection
        )

    return int(result.iloc[0]["total"])


def get_crime_types():
    """Return crime counts grouped by crime type."""

    query = """
        SELECT
            primary_type AS crime_type,
            COUNT(*) AS total
        FROM crimes
        WHERE primary_type IS NOT NULL
          AND TRIM(primary_type) != ''
        GROUP BY primary_type
        ORDER BY total DESC
    """

    with get_connection() as connection:
        return pd.read_sql_query(query, connection)


def get_yearly_trends():
    """Return recorded crime counts grouped by year."""

    query = """
        SELECT
            year,
            COUNT(*) AS total
        FROM crimes
        WHERE year IS NOT NULL
        GROUP BY year
        ORDER BY year
    """

    with get_connection() as connection:
        return pd.read_sql_query(query, connection)


def get_area_crime_counts():
    """Return recorded crime counts by community area."""

    query = """
        SELECT
            community_area,
            COUNT(*) AS total
        FROM crimes
        WHERE community_area IS NOT NULL
          AND TRIM(community_area) != ''
        GROUP BY community_area
        ORDER BY total DESC
    """

    with get_connection() as connection:
        return pd.read_sql_query(query, connection)