"""Data profiling, part 3: does the data change over time (drift)?

Checks:
  1. Are runs stored in time order?
  2. Runs and failure rate per month.
  3. For every usable sensor, compare the first half of the timeline with the
     second half using the two-sample Kolmogorov-Smirnov (KS) test.
     A very small p-value means the two halves look different (drift).
     Because we run hundreds of tests, we use a strict cut-off
     (Bonferroni: 0.01 divided by the number of sensors tested).
  4. Plot the 4 most drifting sensors over time.

Saves reports/drift_ks.csv, reports/monthly_failures.csv and
reports/drift_top_sensors.png.

Run:  python -m src.drift
"""
import duckdb
import matplotlib
matplotlib.use("Agg")  # save plots to file without opening a window
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import ks_2samp

from src.config import DB_PATH, ROOT
from src.redundancy import usable_sensors

REPORT_DIR = ROOT / "reports"
ALPHA = 0.01


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        sensors = con.execute("SELECT * FROM sensors ORDER BY run_id").df()
        labels = con.execute("SELECT * FROM labels ORDER BY run_id").df()
    return sensors, labels


def time_order_check(labels: pd.DataFrame) -> int:
    """Number of runs whose timestamp is earlier than the run before it."""
    return int((labels["timestamp"].diff().dt.total_seconds() < 0).sum())


def monthly_failures(labels: pd.DataFrame) -> pd.DataFrame:
    month = labels["timestamp"].dt.to_period("M").astype(str)
    out = labels.groupby(month)["fail"].agg(runs="count", failures="sum")
    out["failure_rate_pct"] = (out["failures"] / out["runs"] * 100).round(1)
    out.index.name = "month"
    return out


def ks_drift(X: pd.DataFrame, order: pd.Series) -> pd.DataFrame:
    """KS test: first half of the timeline vs second half, per sensor."""
    X = X.loc[order.sort_values().index]  # sort runs by time
    half = len(X) // 2
    first, second = X.iloc[:half], X.iloc[half:]
    rows = []
    for col in X.columns:
        a, b = first[col].dropna(), second[col].dropna()
        if len(a) < 20 or len(b) < 20:
            continue
        stat, p = ks_2samp(a, b)
        rows.append((col, round(stat, 3), p, round(b.mean() - a.mean(), 4)))
    out = pd.DataFrame(rows, columns=["sensor", "ks_stat", "p_value", "mean_change"])
    out["drift"] = out["p_value"] < ALPHA / len(out)
    return out.sort_values("ks_stat", ascending=False)


def plot_top(X: pd.DataFrame, times: pd.Series, top: list[str], path) -> None:
    order = times.sort_values().index
    fig, axes = plt.subplots(len(top), 1, figsize=(10, 2.5 * len(top)), sharex=True)
    for ax, col in zip(axes, top):
        s = X.loc[order, col]
        ax.plot(times[order], s, ".", markersize=2, alpha=0.4, label="run")
        ax.plot(times[order], s.rolling(50, min_periods=10).mean(),
                linewidth=2, label="rolling mean (50 runs)")
        ax.set_ylabel(col)
    axes[0].legend(loc="upper right")
    axes[0].set_title("Most drifting sensors over time")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def main() -> None:
    sensors, labels = load_data()
    X = usable_sensors(sensors)

    back_steps = time_order_check(labels)
    monthly = monthly_failures(labels)
    drift = ks_drift(X, labels["timestamp"])

    REPORT_DIR.mkdir(exist_ok=True)
    monthly.to_csv(REPORT_DIR / "monthly_failures.csv")
    drift.to_csv(REPORT_DIR / "drift_ks.csv", index=False)
    top = drift["sensor"].head(4).tolist()
    plot_top(X, labels["timestamp"], top, REPORT_DIR / "drift_top_sensors.png")

    print(f"Runs out of time order:     {back_steps} of {len(labels)}")
    print("\nRuns and failures per month:")
    print(monthly.to_string())
    print(f"\nSensors tested for drift:   {len(drift)}")
    print(f"Sensors with clear drift:   {int(drift['drift'].sum())}"
          f"  (p < {ALPHA}/{len(drift)})")
    print("\nThe 10 most drifting sensors:")
    print(drift.head(10)[["sensor", "ks_stat", "p_value", "mean_change"]]
          .to_string(index=False, float_format=lambda v: f"{v:.3g}"))
    print("\nSaved reports/drift_ks.csv, reports/monthly_failures.csv,"
          " reports/drift_top_sensors.png")


if __name__ == "__main__":
    main()