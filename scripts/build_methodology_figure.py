"""Render the paper's pipeline overview in PNG and editable SVG formats."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "paper" / "figures"


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
    fig, ax = plt.subplots(figsize=(7.2, 3.55))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.02, top=0.98)
    ax.set(xlim=(0, 7.2), ylim=(0, 3.55))
    ax.axis("off")
    ink, edge = "#172B4D", "#506579"

    def box(x, y, w, h, title, lines, fill="#F2F5F8"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.025,rounding_size=0.06",
                                   linewidth=0.9, edgecolor=edge, facecolor=fill))
        ax.text(x+w/2, y+h-0.19, title, ha="center", va="center", fontsize=9,
                fontweight="bold", color=ink)
        for i, line in enumerate(lines):
            ax.text(x+w/2, y+h-0.40-i*0.17, line, ha="center", va="center",
                    fontsize=8, color=ink)

    def arrow(start, end):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=9,
                                    linewidth=1, color=edge))

    box(0.05, 2.73, 2.10, 0.74, "Telemetry", ["Antarex / Westermo", "Separate recordings"])
    box(2.55, 2.73, 2.10, 0.74, "Causal preparation", ["Align and derive rates", "Preserve gaps"])
    box(5.05, 2.73, 2.10, 0.74, "Partitions and windows", ["70 / 15 / 15 time splits", "Training-only scaling"])
    arrow((2.19, 3.10), (2.50, 3.10))
    arrow((4.69, 3.10), (5.00, 3.10))
    box(2.35, 1.57, 2.50, 0.83, "Forecast models", ["Persistence | linear trend", "ARIMA | LSTM"], "#E9F0F7")
    ax.plot([6.1, 6.1, 5.03], [2.70, 1.985, 1.985], color=edge, linewidth=1)
    arrow((5.03, 1.985), (4.90, 1.985))

    ax.plot([3.6, 3.6], [1.54, 1.30], color=edge, linewidth=1)
    ax.plot([1.70, 5.50], [1.30, 1.30], color=edge, linewidth=1)
    arrow((1.70, 1.30), (1.70, 0.99))
    arrow((5.50, 1.30), (5.50, 0.99))
    box(0.15, 0.06, 3.10, 0.90, "Forecast evaluation", ["Predictions versus future actuals", "MAE / RMSE at target times"], "#EAF3F0")
    box(3.95, 0.06, 3.10, 0.90, "Warning rules and evaluation", ["Recent and predicted growth", "Antarex labels; Westermo counts"], "#F7F0E5")
    ax.text(0.17, 1.12, "Forecasts", fontsize=7.5, color=edge)
    ax.text(5.76, 1.12, "+ recent growth", fontsize=7.5, color=edge)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "svg"):
        fig.savefig(OUTPUT / f"pipeline_overview.{extension}", dpi=240, facecolor="white")
    svg = OUTPUT / "pipeline_overview.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n",
                   encoding="utf-8")
    plt.close(fig)
    print("Created paper/figures/pipeline_overview.png and .svg")


if __name__ == "__main__":
    main()
