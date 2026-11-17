"""Step 2: read the raw SECOM files, check them, and load them into DuckDB.

Creates two tables in data/processed/secom.duckdb:
  sensors : run_id, s000 ... s589        (one row per production run)
  labels  : run_id, timestamp, label_raw, fail
            label_raw is the original value (-1 = pass, 1 = fail)
            fail is 0/1, which is easier for modelling

Run:  python -m src.ingest
"""
from pathlib import Path

import pandas as pd

from src.config import (DB_PATH, EXPECTED_RUNS, EXPECTED_SENSORS,
                        LABELS_FILE, SENSORS_FILE)


def read_sensors(path: Path = SENSORS_FILE) -> pd.DataFrame:
    """590 space-separated numbers per line; missing values are written as NaN."""
    df = pd.read_csv(path, sep=r"\s+", header=None, na_values=["NaN"])
    df.columns = [f"s{i:03d}" for i in range(df.shape[1])]
    run_id = pd.Series(range(len(df)), name="run_id")
    return pd.concat([run_id, df], axis=1)


def read_labels(path: Path = LABELS_FILE) -> pd.DataFrame:
    """Each line: label (-1 pass / 1 fail) and a quoted timestamp "dd/mm/yyyy HH:MM:SS"."""
    df = pd.read_csv(path, sep=" ", header=None, quotechar='"',
                     names=["label_raw", "timestamp"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d/%m/%Y %H:%M:%S")
    df["fail"] = (df["label_raw"] == 1).astype(int)
    df.insert(0, "run_id", range(len(df)))
    return df[["run_id", "timestamp", "label_raw", "fail"]]


def validate(sensors: pd.DataFrame, labels: pd.DataFrame) -> None:
    """Stop immediately if the data is not what we expect."""
    assert len(sensors) == EXPECTED_RUNS, f"expected {EXPECTED_RUNS} runs, got {len(sensors)}"
    assert sensors.shape[1] - 1 == EXPECTED_SENSORS, \
        f"expected {EXPECTED_SENSORS} sensors, got {sensors.shape[1] - 1}"
    assert len(labels) == len(sensors), "sensor and label files have different lengths"
    assert set(labels["label_raw"].unique()) <= {-1, 1}, "unexpected label values"
    assert labels["timestamp"].notna().all(), "some timestamps could not be read"


def load_to_duckdb(sensors: pd.DataFrame, labels: pd.DataFrame,
                   db_path: Path = DB_PATH) -> None:
    import duckdb  # imported here so the reading functions work without DuckDB

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(db_path)) as con:
        con.register("sensors_df", sensors)
        con.register("labels_df", labels)
        con.execute("CREATE OR REPLACE TABLE sensors AS SELECT * FROM sensors_df")
        con.execute("CREATE OR REPLACE TABLE labels AS SELECT * FROM labels_df")


def summary(sensors: pd.DataFrame, labels: pd.DataFrame) -> str:
    n_fail = int(labels["fail"].sum())
    missing = sensors.drop(columns="run_id").isna().mean().mean()
    return (
        f"Runs:            {len(sensors):,}\n"
        f"Sensors:         {sensors.shape[1] - 1}\n"
        f"Failures:        {n_fail} ({n_fail / len(labels):.1%})\n"
        f"Time range:      {labels['timestamp'].min()}  ->  {labels['timestamp'].max()}\n"
        f"Missing values:  {missing:.1%} of all sensor cells"
    )


def main() -> None:
    sensors = read_sensors()
    labels = read_labels()
    validate(sensors, labels)
    load_to_duckdb(sensors, labels)
    print("SECOM loaded into", DB_PATH)
    print(summary(sensors, labels))


if __name__ == "__main__":
    main()
