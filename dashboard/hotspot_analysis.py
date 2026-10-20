import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px


# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_DIR / "crime_data.db"


# --------------------------------------------------
# LOAD CRIME DATA
# --------------------------------------------------

def load_hotspot_data():
    """Load crime records that have valid geographic coordinates."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Crime database not found: {DATABASE_PATH}"
        )

    query = """
        SELECT
            id,
            crime_date,
            primary_type,
            description,
            location_description,
            community_area,
            latitude,
            longitude
        FROM crimes
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL
    """

    with sqlite3.connect(DATABASE_PATH) as connection:
        data = pd.read_sql_query(query, connection)

    if data.empty:
        raise ValueError(
            "No crime records with geographic coordinates were found."
        )

    data["crime_date"] = pd.to_datetime(
        data["crime_date"],
        errors="coerce"
    )

    data["latitude"] = pd.to_numeric(
        data["latitude"],
        errors="coerce"
    )

    data["longitude"] = pd.to_numeric(
        data["longitude"],
        errors="coerce"
    )

    # Keep valid Chicago-area coordinates.
    data = data.dropna(
        subset=["latitude", "longitude"]
    )

    data = data[
        data["latitude"].between(41.0, 43.0)
        & data["longitude"].between(-88.5, -87.0)
    ].copy()

    return data


# --------------------------------------------------
# FILTER CRIME DATA
# --------------------------------------------------


def filter_hotspot_data(
    data,
    crime_type="All",
    start_date=None,
    end_date=None
):
    """Filter records by crime type and date range."""

    filtered = data.copy()

    # Apply the selected crime type.
    if crime_type != "All":
        filtered = filtered[
            filtered["primary_type"].astype("string").str.strip()
            == str(crime_type).strip()
        ]

    # Apply the start date.
    if start_date is not None:
        filtered = filtered[
            filtered["crime_date"].dt.date >= start_date
        ]

    # Apply the end date.
    if end_date is not None:
        filtered = filtered[
            filtered["crime_date"].dt.date <= end_date
        ]

    return filtered.copy()

# --------------------------------------------------
# CREATE CRIME HOTSPOT MAP
# --------------------------------------------------

def get_top_hotspots(data, grid_size=0.005):
    """Group nearby crime records into geographic hotspot cells."""

    columns = [
        "latitude",
        "longitude",
        "crime_count",
        "most_common_crime"
    ]

    if data.empty:
        return pd.DataFrame(columns=columns)

    if grid_size <= 0:
        raise ValueError("Grid size must be greater than zero.")

    grouped_data = data.copy()

    grouped_data["latitude_cell"] = (
        grouped_data["latitude"] / grid_size
    ).round().astype(int)

    grouped_data["longitude_cell"] = (
        grouped_data["longitude"] / grid_size
    ).round().astype(int)

    group_columns = ["latitude_cell", "longitude_cell"]

    hotspots = (
        grouped_data
        .groupby(group_columns, as_index=False)
        .agg(
            crime_count=("id", "count"),
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean")
        )
    )

    valid_crimes = grouped_data.dropna(
        subset=["primary_type"]
    )

    if valid_crimes.empty:
        hotspots["most_common_crime"] = "Unknown"
    else:
        common_crimes = (
            valid_crimes
            .groupby(group_columns + ["primary_type"])
            .size()
            .reset_index(name="type_count")
            .sort_values(
                ["type_count", "primary_type"],
                ascending=[False, True]
            )
            .drop_duplicates(subset=group_columns)
            .rename(
                columns={"primary_type": "most_common_crime"}
            )
        )

        hotspots = hotspots.merge(
            common_crimes[
                group_columns + ["most_common_crime"]
            ],
            on=group_columns,
            how="left"
        )

        hotspots["most_common_crime"] = (
            hotspots["most_common_crime"].fillna("Unknown")
        )

    return (
        hotspots
        .sort_values("crime_count", ascending=False)
        .reset_index(drop=True)
    )


COMMUNITY_AREA_NAMES = {
    1: "Rogers Park",
    2: "West Ridge",
    3: "Uptown",
    4: "Lincoln Square",
    5: "North Center",
    6: "Lake View",
    7: "Lincoln Park",
    8: "Near North Side",
    9: "Edison Park",
    10: "Norwood Park",
    11: "Jefferson Park",
    12: "Forest Glen",
    13: "North Park",
    14: "Albany Park",
    15: "Portage Park",
    16: "Irving Park",
    17: "Dunning",
    18: "Montclare",
    19: "Belmont Cragin",
    20: "Hermosa",
    21: "Avondale",
    22: "Logan Square",
    23: "Humboldt Park",
    24: "West Town",
    25: "Austin",
    26: "West Garfield Park",
    27: "East Garfield Park",
    28: "Near West Side",
    29: "North Lawndale",
    30: "South Lawndale",
    31: "Lower West Side",
    32: "Loop",
    33: "Near South Side",
    34: "Armour Square",
    35: "Douglas",
    36: "Oakland",
    37: "Fuller Park",
    38: "Grand Boulevard",
    39: "Kenwood",
    40: "Washington Park",
    41: "Hyde Park",
    42: "Woodlawn",
    43: "South Shore",
    44: "Chatham",
    45: "Avalon Park",
    46: "South Chicago",
    47: "Burnside",
    48: "Calumet Heights",
    49: "Roseland",
    50: "Pullman",
    51: "South Deering",
    52: "East Side",
    53: "West Pullman",
    54: "Riverdale",
    55: "Hegewisch",
    56: "Garfield Ridge",
    57: "Archer Heights",
    58: "Brighton Park",
    59: "McKinley Park",
    60: "Bridgeport",
    61: "New City",
    62: "West Elsdon",
    63: "Gage Park",
    64: "Clearing",
    65: "West Lawn",
    66: "Chicago Lawn",
    67: "West Englewood",
    68: "Englewood",
    69: "Greater Grand Crossing",
    70: "Ashburn",
    71: "Auburn Gresham",
    72: "Beverly",
    73: "Washington Heights",
    74: "Mount Greenwood",
    75: "Morgan Park",
    76: "O'Hare",
    77: "Edgewater",
}


def get_neighborhood_crime_counts(data):
    """Count crimes recorded in each Chicago community area."""

    columns = [
        "community_area",
        "community_area_name",
        "crime_count"
    ]

    if data.empty or "community_area" not in data.columns:
        return pd.DataFrame(columns=columns)

    neighborhood_data = data.copy()

    neighborhood_data["community_area"] = pd.to_numeric(
        neighborhood_data["community_area"],
        errors="coerce"
    )

    neighborhood_data = neighborhood_data.dropna(
        subset=["community_area"]
    )

    neighborhood_data = neighborhood_data[
        neighborhood_data["community_area"].between(1, 77)
    ].copy()

    if neighborhood_data.empty:
        return pd.DataFrame(columns=columns)

    neighborhood_data["community_area"] = (
        neighborhood_data["community_area"].astype(int)
    )

    result = (
        neighborhood_data
        .groupby("community_area")
        .size()
        .reset_index(name="crime_count")
    )

    result["community_area_name"] = (
        result["community_area"].map(COMMUNITY_AREA_NAMES)
    )

    return (
        result[columns]
        .sort_values("crime_count", ascending=False)
        .reset_index(drop=True)
    )


def create_hotspot_map(data, grid_size=0.005):
    """Display a smoother crime density heatmap with hotspot details."""

    import plotly.graph_objects as go

    if data.empty:
        return None

    # Create the density layer from individual crime locations.
    figure = px.density_map(
        data,
        lat="latitude",
        lon="longitude",
        radius=9,
        center={"lat": 41.8781, "lon": -87.6298},
        zoom=10,
        map_style="open-street-map",
        opacity=0.60,
        color_continuous_scale=[
            [0.00, "#FF3B30"],
            [0.25, "#FF6B35"],
            [0.50, "#FF9F1C"],
            [0.75, "#FFD166"],
            [1.00, "#FFF176"]
        ],
        title="Crime Density Heatmap"
    )

    # Aggregate crimes into geographic grid cells.
    points = data.copy()
    points["latitude_cell"] = (
        points["latitude"] / grid_size
    ).round() * grid_size
    points["longitude_cell"] = (
        points["longitude"] / grid_size
    ).round() * grid_size

    grouped = points.groupby(
        ["latitude_cell", "longitude_cell"]
    )

    hotspots = grouped.size().reset_index(name="crime_count")

    # Find the most common crime type in each cell.
    common_crimes = (
        points.groupby(
            ["latitude_cell", "longitude_cell"]
        )["primary_type"]
        .agg(lambda values: values.mode().iloc[0]
             if not values.mode().empty else "Unknown")
        .reset_index(name="most_common_crime")
    )

    # Find the most frequently recorded community area in each cell.
    if "community_area" in points.columns:
        area_values = (
            points.dropna(subset=["community_area"])
            .groupby(
                ["latitude_cell", "longitude_cell"]
            )["community_area"]
            .agg(lambda values: values.mode().iloc[0]
                 if not values.mode().empty else None)
            .reset_index(name="community_area")
        )

        hotspots = hotspots.merge(
            area_values,
            on=["latitude_cell", "longitude_cell"],
            how="left"
        )

        if "COMMUNITY_AREA_NAMES" in globals():
            hotspots["area_name"] = (
                pd.to_numeric(
                    hotspots["community_area"],
                    errors="coerce"
                )
                .map(COMMUNITY_AREA_NAMES)
                .fillna("Area unavailable")
            )
        else:
            hotspots["area_name"] = "Area unavailable"
    else:
        hotspots["area_name"] = "Area unavailable"

    hotspots = hotspots.merge(
        common_crimes,
        on=["latitude_cell", "longitude_cell"],
        how="left"
    )

    hotspots["latitude"] = hotspots["latitude_cell"]
    hotspots["longitude"] = hotspots["longitude_cell"]

    # Invisible hover targets preserve the heatmap's appearance.
    hover_data = hotspots[
        ["area_name", "crime_count", "latitude", "longitude",
         "most_common_crime"]
    ].to_numpy()

    figure.add_trace(
        go.Scattermap(
            lat=hotspots["latitude"],
            lon=hotspots["longitude"],
            mode="markers",
            marker={"size": 12, "opacity": 0.01},
            customdata=hover_data,
            hovertemplate=(
                "<b>Area:</b> %{customdata[0]}<br>"
                "<b>Number of Crimes:</b> %{customdata[1]}<br>"
                "<b>Latitude:</b> %{customdata[2]:.5f}<br>"
                "<b>Longitude:</b> %{customdata[3]:.5f}<br>"
                "<b>Most Common Crime:</b> %{customdata[4]}"
                "<extra></extra>"
            ),
            showlegend=False
        )
    )

    figure.update_layout(
        height=650,
        margin={"l": 0, "r": 0, "t": 55, "b": 0},
        coloraxis_colorbar={"title": "Crime Density"}
    )

    return figure



def create_crime_count_map(data, grid_size=0.005):
    """Display crime counts as blue bubbles on a street map."""

    import plotly.graph_objects as go
    import numpy as np

    if data.empty:
        return None

    # Aggregate using the same integer grid indexes.
    points = data.copy()
    points["latitude_cell"] = (
        points["latitude"] / grid_size
    ).round().astype(int)
    points["longitude_cell"] = (
        points["longitude"] / grid_size
    ).round().astype(int)

    hotspots = get_top_hotspots(data, grid_size)

    if hotspots.empty:
        return None

    # Match community areas using the integer grid indexes.
    if "community_area" in points.columns:
        points["community_area"] = pd.to_numeric(
            points["community_area"], errors="coerce"
        )

        points = points.dropna(subset=["community_area"])

        area_ids = (
            points.groupby(
                ["latitude_cell", "longitude_cell"]
            )["community_area"]
            .agg(lambda values: values.mode().iloc[0])
            .reset_index(name="community_area")
        )

        area_ids["community_area"] = (
            area_ids["community_area"].round().astype(int)
        )

        hotspots = hotspots.merge(
            area_ids,
            on=["latitude_cell", "longitude_cell"],
            how="left"
        )

        hotspots["area_name"] = (
            hotspots["community_area"]
            .map(COMMUNITY_AREA_NAMES)
            .fillna("Area unavailable")
        )
    else:
        hotspots["area_name"] = "Area unavailable"

    # Find the most common crime type for each matching grid cell.
    hotspots = hotspots.drop(
        columns=["most_common_crime"], errors="ignore"
    )

    common_crimes = (
        points.dropna(subset=["primary_type"])
        .groupby(
            ["latitude_cell", "longitude_cell", "primary_type"]
        )
        .size()
        .reset_index(name="type_count")
        .sort_values(
            ["type_count", "primary_type"],
            ascending=[False, True]
        )
        .drop_duplicates(
            subset=["latitude_cell", "longitude_cell"]
        )
        .rename(columns={"primary_type": "most_common_crime"})
    )

    hotspots = hotspots.merge(
        common_crimes[
            ["latitude_cell", "longitude_cell", "most_common_crime"]
        ],
        on=["latitude_cell", "longitude_cell"],
        how="left"
    )

    hotspots["most_common_crime"] = (
        hotspots["most_common_crime"].fillna("Unknown")
    )

    # Convert integer grid indexes to map coordinates.
    hotspots["latitude"] = hotspots["latitude_cell"] * grid_size
    hotspots["longitude"] = hotspots["longitude_cell"] * grid_size

    counts = hotspots["crime_count"].astype(float)
    maximum = max(counts.max(), 1)

    hotspots["bubble_size"] = (
    8 + 12 * np.sqrt(counts / maximum)
    )

    # Keep labels visible, using compact numbers for large counts.
    def format_count(value):
        if value >= 1000:
            return f"{value / 1000:.1f}k".replace(".0k", "k")
        return str(int(value))

    label_cutoff = 1
    hotspots["count_label"] = [
        format_count(value) if value >= label_cutoff else ""
        for value in counts
    ]

    hover_data = hotspots[
        [
            "area_name",
            "crime_count",
            "latitude",
            "longitude",
            "most_common_crime"
        ]
    ].to_numpy()

    figure = go.Figure(
        go.Scattermap(
            lat=hotspots["latitude"],
            lon=hotspots["longitude"],
            mode="markers+text",
            text=hotspots["count_label"],
            textposition="middle center",
            textfont={"color": "white", "size": 9},
            marker={
                "size": hotspots["bubble_size"],
                "color": "#087EA4",
                "opacity": 0.90
            },
            customdata=hover_data,
            hovertemplate=(
                "<b>Area:</b> %{customdata[0]}<br>"
                "<b>Number of Crimes:</b> %{customdata[1]:,.0f}<br>"
                "<b>Latitude:</b> %{customdata[2]:.5f}<br>"
                "<b>Longitude:</b> %{customdata[3]:.5f}<br>"
                "<b>Most Common Crime:</b> %{customdata[4]}"
                "<extra></extra>"
            ),
            showlegend=False
        )
    )

    figure.update_layout(
        title="Crime Count by Geographic Grid Cell",
        map={
            "style": "open-street-map",
            "center": {"lat": 41.8781, "lon": -87.6298},
            "zoom": 10
        },
        height=650,
        margin={"l": 0, "r": 0, "t": 55, "b": 0}
    )

    return figure