"""Automated checks for Week 1: is the data complete and correctly read?

Run:  pytest -v
"""
import pytest

from src.config import (DB_PATH, EXPECTED_FAILURES, EXPECTED_RUNS,
                        EXPECTED_SENSORS, LABELS_FILE, SENSORS_FILE)
from src.ingest import read_labels, read_sensors

needs_data = pytest.mark.skipif(
    not (SENSORS_FILE.exists() and LABELS_FILE.exists()),
    reason="SECOM not downloaded yet: run  python -m src.download",
)


@needs_data
def test_row_and_column_counts():
    sensors = read_sensors()
    assert len(sensors) == EXPECTED_RUNS
    assert sensors.shape[1] - 1 == EXPECTED_SENSORS  # minus run_id


@needs_data
def test_labels_match_documentation():
    labels = read_labels()
    assert len(labels) == EXPECTED_RUNS
    assert set(labels["label_raw"].unique()) == {-1, 1}
    assert labels["fail"].sum() == EXPECTED_FAILURES


@needs_data
def test_timestamps_are_valid():
    labels = read_labels()
    assert labels["timestamp"].notna().all()
    assert labels["timestamp"].dt.year.eq(2008).all()


@pytest.mark.skipif(not DB_PATH.exists(), reason="run  python -m src.ingest  first")
def test_duckdb_tables():
    import duckdb
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        n_sensors = con.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]
        n_labels = con.execute("SELECT COUNT(*) FROM labels").fetchone()[0]
        n_cols = len(con.execute("SELECT * FROM sensors LIMIT 0").description)
    assert n_sensors == n_labels == EXPECTED_RUNS
    assert n_cols == EXPECTED_SENSORS + 1
