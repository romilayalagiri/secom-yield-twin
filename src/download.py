"""Step 1: download the two SECOM files into data/raw/.

Run:  python -m src.download
"""
import sys

import requests

from src.config import RAW_DIR, UCI_DATASET_PAGE, UCI_FILES


def download() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in UCI_FILES.items():
        target = RAW_DIR / name
        if target.exists():
            print(f"[skip] {name} already exists")
            continue
        print(f"[get ] {url}")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
        except requests.RequestException as err:
            print(f"\nDownload failed: {err}")
            print(f"Download the files manually from {UCI_DATASET_PAGE}")
            print(f"and put secom.data and secom_labels.data into {RAW_DIR}")
            sys.exit(1)
        target.write_bytes(response.content)
        print(f"[done] saved {target} ({len(response.content):,} bytes)")


if __name__ == "__main__":
    download()
