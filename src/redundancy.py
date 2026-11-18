"""Data profiling, part 2: which sensors are near-copies of each other?

Steps:
  1. Leave out constant sensors and sensors with over 50% missing
     (exploration only; the final pipeline decides this on training data).
  2. Calculate the correlation between every pair of remaining sensors.
  3. List pairs with |correlation| >= 0.95 ("near-duplicates").
  4. Join connected pairs into groups. In each group, one sensor would be
     enough; the others are candidates for removal.

Saves reports/correlated_pairs.csv and reports/correlated_groups.csv.

Run:  python -m src.redundancy
"""
import pandas as pd

from src.config import ROOT
from src.profiling import load_sensors, sensor_profile

REPORT_DIR = ROOT / "reports"
THRESHOLD = 0.95
MAX_MISSING_PCT = 50


def usable_sensors(sensors: pd.DataFrame) -> pd.DataFrame:
    """Sensors that are not constant and not mostly empty."""
    profile = sensor_profile(sensors)
    keep = profile[(~profile["constant"]) & (profile["missing_pct"] <= MAX_MISSING_PCT)]
    return sensors[keep.index]


def correlated_pairs(X: pd.DataFrame, threshold: float = THRESHOLD) -> pd.DataFrame:
    """All sensor pairs whose absolute correlation is at least the threshold."""
    corr = X.corr()  # uses all runs where both sensors have a value
    pairs = []
    cols = corr.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            r = corr.iat[i, j]
            if pd.notna(r) and abs(r) >= threshold:
                pairs.append((cols[i], cols[j], round(r, 4)))
    return pd.DataFrame(pairs, columns=["sensor_a", "sensor_b", "correlation"])


def group_pairs(pairs: pd.DataFrame) -> list[list[str]]:
    """Join pairs that share a sensor into groups (A~B and B~C -> {A, B, C})."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in zip(pairs["sensor_a"], pairs["sensor_b"]):
        parent[find(a)] = find(b)

    groups = {}
    for sensor in parent:
        groups.setdefault(find(sensor), []).append(sensor)
    return sorted((sorted(g) for g in groups.values()), key=len, reverse=True)


def main() -> None:
    X = usable_sensors(load_sensors())
    pairs = correlated_pairs(X)
    groups = group_pairs(pairs)
    removable = sum(len(g) - 1 for g in groups)

    REPORT_DIR.mkdir(exist_ok=True)
    pairs.to_csv(REPORT_DIR / "correlated_pairs.csv", index=False)
    pd.DataFrame({
        "group": range(1, len(groups) + 1),
        "size": [len(g) for g in groups],
        "sensors": [", ".join(g) for g in groups],
    }).to_csv(REPORT_DIR / "correlated_groups.csv", index=False)

    print(f"Usable sensors checked:          {X.shape[1]}")
    print(f"Near-duplicate pairs (|r|>={THRESHOLD}): {len(pairs)}")
    print(f"Groups of near-duplicates:       {len(groups)}")
    print(f"Sensors in those groups:         {sum(len(g) for g in groups)}")
    print(f"Could be removed (keep 1/group): {removable}")
    print(f"Sensors left after that:         {X.shape[1] - removable}")
    print("\nThe 5 largest groups:")
    for k, g in enumerate(groups[:5], 1):
        print(f"  {k}. ({len(g)} sensors) {', '.join(g)}")
    print("\nSaved reports/correlated_pairs.csv and reports/correlated_groups.csv")


if __name__ == "__main__":
    main()