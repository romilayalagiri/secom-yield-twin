"""Central settings: file paths and the facts we expect about SECOM."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DB_PATH = PROCESSED_DIR / "secom.duckdb"

SENSORS_FILE = RAW_DIR / "secom.data"
LABELS_FILE = RAW_DIR / "secom_labels.data"

# Official download locations (UCI Machine Learning Repository)
UCI_FILES = {
    "secom.data": "https://archive.ics.uci.edu/ml/machine-learning-databases/secom/secom.data",
    "secom_labels.data": "https://archive.ics.uci.edu/ml/machine-learning-databases/secom/secom_labels.data",
}
UCI_DATASET_PAGE = "https://archive.ics.uci.edu/dataset/179/secom"

# What the dataset documentation says we should find
EXPECTED_RUNS = 1567
EXPECTED_SENSORS = 590
EXPECTED_FAILURES = 104
