import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# Database location
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_DIR / "crime_data.db"


def load_weekly_crime_data():
    """Load crime records and convert them into weekly crime counts."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Crime database not found: {DATABASE_PATH}"
        )

    with sqlite3.connect(DATABASE_PATH) as connection:
        query = """
            SELECT crime_date
            FROM crimes
            WHERE crime_date IS NOT NULL
              AND TRIM(crime_date) != ''
        """
        records = pd.read_sql_query(query, connection)

    records["crime_date"] = pd.to_datetime(
        records["crime_date"],
        errors="coerce"
    )

    records = records.dropna(subset=["crime_date"])

    if records.empty:
        raise ValueError("No valid crime dates were found.")

    # Count crimes for each week, starting on Monday.
    records["week"] = (
        records["crime_date"]
        .dt.to_period("W-SUN")
        .dt.start_time
    )

    weekly_counts = (
        records.groupby("week")
        .size()
        .rename("crime_count")
        .sort_index()
    )

    # Exclude the final week if it is incomplete.
    latest_date = records["crime_date"].max()

    if latest_date.weekday() != 6:
        latest_week_start = (
            latest_date.to_period("W-SUN").start_time
        )

        weekly_counts = weekly_counts[
            weekly_counts.index < latest_week_start
        ]

    # Include weeks with zero recorded crimes.
    full_weeks = pd.date_range(
        start=weekly_counts.index.min(),
        end=weekly_counts.index.max(),
        freq="7D"
    )

    weekly_counts = weekly_counts.reindex(
        full_weeks,
        fill_value=0
    )

    weekly_counts.index.name = "week"

    return weekly_counts


def create_features(weekly_counts):
    """Create features using past crime counts and calendar information."""

    data = pd.DataFrame({
        "crime_count": weekly_counts
    })

    data["week_number"] = np.arange(len(data))
    data["month"] = data.index.month
    data["week_of_year"] = data.index.isocalendar().week.astype(int)

    # Previous weeks' crime counts.
    data["previous_week"] = data["crime_count"].shift(1)
    data["previous_2_weeks"] = data["crime_count"].shift(2)
    data["previous_4_weeks"] = data["crime_count"].shift(4)

    # Average crime count over the previous four weeks.
    data["previous_4_week_average"] = (
        data["crime_count"]
        .shift(1)
        .rolling(window=4)
        .mean()
    )

    return data.dropna()


def train_and_evaluate_model():
    """Train the model and evaluate it on later historical weeks."""

    weekly_counts = load_weekly_crime_data()

    if len(weekly_counts) < 20:
        raise ValueError(
            "At least 20 weeks of crime data are required."
        )

    data = create_features(weekly_counts)

    if len(data) < 12:
        raise ValueError(
            "There are not enough weekly observations to train the model."
        )

    # Keep the later observations for testing.
    split_index = max(1, int(len(data) * 0.8))

    train_data = data.iloc[:split_index]
    test_data = data.iloc[split_index:]

    if test_data.empty:
        raise ValueError("Not enough observations for model evaluation.")

    feature_columns = [
        "week_number",
        "month",
        "week_of_year",
        "previous_week",
        "previous_2_weeks",
        "previous_4_weeks",
        "previous_4_week_average",
    ]

    X_train = train_data[feature_columns]
    y_train = train_data["crime_count"]

    X_test = test_data[feature_columns]
    y_test = test_data["crime_count"]

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=5,
        min_samples_leaf=2,
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    # Random Forest evaluation
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    # Baseline: predict using the previous week's actual crime count
    baseline_predictions = X_test["previous_week"].values

    baseline_mae = mean_absolute_error(
        y_test,
        baseline_predictions
    )

    baseline_rmse = np.sqrt(
        mean_squared_error(y_test, baseline_predictions)
    )

    # Additional baseline: use the crime count from four weeks earlier.
    seasonal_predictions = X_test["previous_4_weeks"].values

    seasonal_mae = mean_absolute_error(
        y_test,
        seasonal_predictions
    )

    seasonal_rmse = np.sqrt(
        mean_squared_error(y_test, seasonal_predictions)
    )

    # Compare model performance
    if baseline_mae > 0:
        improvement = (
            (baseline_mae - mae) / baseline_mae
        ) * 100
    else:
        improvement = 0.0

    actual_vs_predicted = pd.DataFrame({
        "Week": test_data.index,
        "Actual Crimes": y_test.values,
        "Predicted Crimes": np.maximum(0, predictions).round().astype(int)
    })

    return {
        "model": model,
        "baseline_mae": float(baseline_mae),
        "baseline_rmse": float(baseline_rmse),
        "seasonal_mae": float(seasonal_mae),
        "seasonal_rmse": float(seasonal_rmse),
        "improvement_percent": float(improvement),
        "weekly_counts": weekly_counts,
        "mae": float(mae),
        "rmse": float(rmse),
        "test_results": actual_vs_predicted,
        "feature_columns": feature_columns,
        "training_weeks": len(train_data),
        "testing_weeks": len(test_data),
    }


def forecast_next_weeks(model_results, number_of_weeks=4):
    """Forecast crime counts for the next few weeks."""

    if number_of_weeks < 1:
        raise ValueError("The forecast period must be at least one week.")

    model = model_results["model"]
    weekly_counts = model_results["weekly_counts"]
    feature_columns = model_results["feature_columns"]

    history = list(weekly_counts.astype(float).values)
    last_week = weekly_counts.index[-1]

    forecast_rows = []

    for step in range(1, number_of_weeks + 1):
        next_week = last_week + pd.Timedelta(weeks=step)

        features = pd.DataFrame([{
            "week_number": len(history),
            "month": next_week.month,
            "week_of_year": int(next_week.isocalendar().week),
            "previous_week": history[-1],
            "previous_2_weeks": history[-2],
            "previous_4_weeks": history[-4],
            "previous_4_week_average": float(
                np.mean(history[-4:])
            ),
        }])[feature_columns]

        predicted_count = max(
            0,
            int(round(model.predict(features)[0]))
        )

        forecast_rows.append({
            "Week": next_week,
            "Predicted Crimes": predicted_count
        })

        # Use the predicted count as input for the next forecast.
        history.append(float(predicted_count))

    return pd.DataFrame(forecast_rows)