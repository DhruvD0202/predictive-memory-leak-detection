"""Make paper figures from unchanged, manifest-verified Colab result tables.

Uses the existing .venv-baseline Matplotlib environment. No models are fitted,
intervals selected, or result values changed. Saves PNG and editable SVG copies.
"""

import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "paper" / "figures"
COLORS = {"actual": "#172B4D", "persistence": "#008577", "linear_trend": "#777777",
          "arima": "#7752B8", "lstm": "#C83450"}


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def values(rows, key):
    return np.array([float(row[key]) for row in rows])


def shade(ax, x, active):
    """Show each labeled grid cell, including isolated active samples."""
    step = float(np.median(np.diff(x)))
    starts = np.flatnonzero(active & ~np.r_[False, active[:-1]])
    ends = np.flatnonzero(active & ~np.r_[active[1:], False])
    for start, end in zip(starts, ends):
        ax.axvspan(x[start], min(x[end] + step, x[-1]), color="#F4CED4", alpha=0.5,
                   linewidth=0, zorder=0)


def style_axis(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.22, linewidth=0.6)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(OUTPUT / f"{name}.png", dpi=300, facecolor="white")
    svg = OUTPUT / f"{name}.svg"
    fig.savefig(svg, facecolor="white")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())
                   + "\n", encoding="utf-8")
    plt.close(fig)


def main():
    verified_files = 0
    for folder in ["results/lstm_colab", "results/warnings_colab"]:
        root = ROOT / folder
        manifest = json.loads((root / "MANIFEST.json").read_text())
        for entry in manifest["files"]:
            data = (root / entry["entry"]).read_bytes()
            assert len(data) == entry["bytes"]
            assert hashlib.sha256(data).hexdigest() == entry["sha256"], entry["entry"]
            verified_files += 1

    sources = {
        "forecast": ROOT / "results/lstm_colab/antarex_mono/first_test_30min.csv",
        "learning": ROOT / "results/lstm_colab/antarex_mono/training_history.csv",
        "warnings": ROOT / "results/warnings_colab/antarex_first_test_30min.csv",
    }
    forecast, learning, warnings = [read_rows(sources[key]) for key in sources]
    assert len(forecast) == len(warnings) == 361
    assert all(float(r["target_timestamp"]) - float(r["origin_timestamp"]) == 60
               for r in forecast)
    assert [r["origin_index"] for r in forecast] == [r["origin_index"] for r in warnings]
    selected = min(learning, key=lambda r: float(r["validation_rmse_percentage_points"]))
    assert int(selected["epoch"]) == 8

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5,
                         "axes.labelsize": 9.5, "legend.fontsize": 8,
                         "svg.fonttype": "none"})
    OUTPUT.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6.6, 2.85))
    fig.subplots_adjust(left=0.095, right=0.99, bottom=0.20, top=0.76)
    x = (values(forecast, "target_timestamp") - float(forecast[0]["target_timestamp"])) / 60
    shade(ax, x, values(forecast, "leak_active_at_target") == 1)
    for key, label, linestyle in [("actual", "Actual", "-"),
                                  ("persistence", "Persistence", "--"),
                                  ("linear_trend", "Linear trend", ":"),
                                  ("arima", "ARIMA", "-."), ("lstm", "LSTM", "-")]:
        ax.plot(x, 100 * values(forecast, key), label=label, color=COLORS[key],
                linestyle=linestyle, linewidth=1.4 if key in ["actual", "lstm"] else 1.1)
    handles, labels = ax.get_legend_handles_labels()
    handles.append(Patch(facecolor="#F4CED4", alpha=0.5))
    labels.append("Injected leak active")
    ax.legend(handles, labels, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.01),
              frameon=False, columnspacing=1.4)
    ax.set(xlim=(0, 30), xlabel="Target time: minutes from interval start",
           ylabel="Memory pressure (% RAM)")
    style_axis(ax)
    save(fig, "antarex_forecast_results")

    fig, ax = plt.subplots(figsize=(6.6, 2.55))
    fig.subplots_adjust(left=0.095, right=0.99, bottom=0.20, top=0.97)
    epochs = values(learning, "epoch")
    ax.plot(epochs, values(learning, "training_rmse_percentage_points_online"),
            color="#147F9B", label="Training (online batches)", linewidth=1.5)
    ax.plot(epochs, values(learning, "validation_rmse_percentage_points"),
            color="#B76700", label="Validation (fixed epoch weights)", linewidth=1.5)
    ax.axvline(8, color="#555555", linestyle="--", linewidth=1)
    ax.text(8.12, 1.36, "Selected epoch 8", fontsize=8, color="#444444")
    ax.legend(loc="upper right", frameon=False)
    ax.set(xlabel="Epoch", ylabel="RMSE (percentage points of RAM)", xticks=[2, 4, 6, 8, 10, 12])
    style_axis(ax)
    save(fig, "antarex_training_results")

    fig, axes = plt.subplots(2, 1, figsize=(6.6, 3.5), sharex=True,
                             gridspec_kw={"height_ratios": [1.45, 1]})
    fig.subplots_adjust(left=0.165, right=0.99, bottom=0.135, top=0.92, hspace=0.10)
    x = (values(warnings, "origin_timestamp") - float(warnings[0]["origin_timestamp"])) / 60
    active = values(warnings, "leak_active") == 1
    for ax in axes:
        style_axis(ax)
        shade(ax, x, active)
    axes[0].plot(x, 100 * values(warnings, "memory_pressure_at_origin"),
                 color=COLORS["actual"], linewidth=1.5)
    axes[0].set_ylabel("Memory pressure (% RAM)")
    axes[0].legend(handles=[Patch(facecolor="#F4CED4", alpha=0.5,
                                 label="Injected leak active")],
                   loc="lower right", bbox_to_anchor=(1, 1), frameon=False)
    for y, method, color in [(0, "trend_only", COLORS["persistence"]),
                              (1, "arima_growth", COLORS["arima"]),
                              (2, "lstm_growth", COLORS["lstm"])]:
        enabled = np.array([row[method + "_warning"] == "True" for row in warnings])
        starts = np.flatnonzero(enabled & ~np.r_[False, enabled[:-1]])
        ends = np.flatnonzero(enabled & ~np.r_[enabled[1:], False])
        for start, end in zip(starts, ends):
            axes[1].broken_barh([(x[start], min(x[end] + 5/60, 30) - x[start])],
                                (y - 0.28, 0.56), facecolors=color, alpha=0.85)
        axes[1].hlines(y - 0.28, 0, 30, color=color, linewidth=0.65)
    axes[1].set(yticks=[0, 1, 2], yticklabels=["Trend only", "ARIMA + trend", "LSTM + trend"],
                ylim=(-0.5, 2.5), xlim=(0, 30), xlabel="Warning origin: minutes from interval start")
    save(fig, "antarex_warning_results")

    provenance = {"verified_original_files": verified_files, "new_experiment": False,
                  "interval_selection": "unchanged first eligible 30-minute interval",
                  "forecast_target_start": int(forecast[0]["target_timestamp"]),
                  "warning_origin_start": int(warnings[0]["origin_timestamp"]),
                  "interval_rows": len(forecast),
                  "sources": {key: {"path": str(path.relative_to(ROOT)).replace("\\", "/"),
                                       "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                              for key, path in sources.items()}}
    (OUTPUT / "results_figure_sources.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(f"Verified {verified_files} original files; rendered 3 paper figures from saved tables.")


if __name__ == "__main__":
    main()
