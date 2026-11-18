"""Data profiling, part 1: how complete and how useful is each sensor?

For every sensor it calculates:
  missing_pct : percentage of runs where the value is empty
  n_unique    : how many different values the sensor ever shows
  constant    : True if the sensor shows only one value (no information)
  mean, std, min, max : basic statistics

Saves the full table to reports/sensor_profile.csv and prints a summary.

Run:  python -m src.profiling
"""
import duckdb
import pandas as pd

from src.config import DB_PATH, ROOT

REPORT_DIR = ROOT / "reports"


def load_sensors() -> pd.DataFrame:
    """Read the sensors table from the DuckDB database."""
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        return con.execute("SELECT * FROM sensors ORDER BY run_id").df()


def sensor_profile(sensors: pd.DataFrame) -> pd.DataFrame:
    """One row per sensor with missingness and basic statistics."""
    X = sensors.drop(columns="run_id")
    profile = pd.DataFrame({
        "missing_pct": X.isna().mean() * 100,
        "n_unique": X.nunique(dropna=True),
        "mean": X.mean(),
        "std": X.std(),
        "min": X.min(),
        "max": X.max(),
    })
    profile["constant"] = profile["n_unique"] <= 1
    profile.index.name = "sensor"
    return profile


def print_summary(profile: pd.DataFrame) -> None:
    bands = pd.cut(
        profile["missing_pct"],
        bins=[-0.1, 0, 5, 20, 50, 100],
        labels=["0% (complete)", "0-5%", "5-20%", "20-50%", "over 50%"],
    )
    print(f"Sensors profiled:        {len(profile)}")
    print(f"Constant (useless):      {int(profile['constant'].sum())}")
    print("\nSensors by share of missing values:")
    print(bands.value_counts().sort_index().to_string())
    print("\nThe 10 sensors with the most missing values:")
    print(profile.sort_values("missing_pct", ascending=False)
          .head(10)[["missing_pct", "n_unique"]].round(1).to_string())


def main() -> None:
    profile = sensor_profile(load_sensors())
    REPORT_DIR.mkdir(exist_ok=True)
    out = REPORT_DIR / "sensor_profile.csv"
    profile.to_csv(out)
    print_summary(profile)
    print(f"\nFull table saved to {out}")


if __name__ == "__main__":
    main()
