"""Draw the archived experimental workflow at the manuscript's printed size."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "paper/spin2027_no_disclosure/figures"


def main():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "pdf.fonttype": 42,
        "ps.fonttype": 42, "svg.fonttype": "none",
    })
    width, height = 346, 355
    fig = plt.figure(figsize=(width / 72, height / 72))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, width), ylim=(0, height))
    ax.axis("off")
    labels = []

    def box(x, y, w, h, title, lines=()):
        ax.add_patch(Rectangle((x, y), w, h, facecolor="white",
                               edgecolor="black", linewidth=0.75, zorder=2))
        leading = 11
        baseline = y + h / 2 + leading * len(lines) / 2
        for i, text in enumerate((title, *lines)):
            label = ax.text(x + w / 2, baseline - leading * i, text,
                            ha="center", va="center", fontsize=8.2 if i else 8.6,
                            fontweight="normal" if i else "bold", zorder=3)
            labels.append((label, x, y, w, h))

    def arrow(points):
        for a, b in zip(points[:-2], points[1:-1]):
            ax.plot([a[0], b[0]], [a[1], b[1]], color="black", lw=0.75, zorder=1)
        ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle="-|>",
                                    mutation_scale=7, lw=0.75, color="black",
                                    shrinkA=0, shrinkB=1.5, zorder=1))

    box(12, 309, 322, 41, "Archived telemetry", [
        "Antarex (5 s) / Westermo systems 1-3 (30 s)"])
    box(12, 234, 322, 56, "Causal preparation", [
        "Past-only alignment and rates; preserve gaps",
        "70% / 15% / 15% chronological split",
        "Training-only feature selection and scaling"])
    box(12, 141, 162, 69, "Forecast models", [
        "Persistence; linear trend",
        "Restricted ARIMA; LSTM",
        "History: 60 observations",
        "Horizon: 60 s / 300 s"])
    box(208, 171, 126, 39, "Observed growth", [
        "Last 12 memory readings", "Slope in pp/min"])
    box(208, 91, 126, 59, "Warning rules", [
        "Trend only or",
        "ARIMA / LSTM + trend",
        "Validation thresholds;",
        "3 consecutive readings"])
    box(12, 53, 162, 53, "Forecast evaluation", [
        "Future actuals vs. forecasts",
        "MAE / RMSE (pp of RAM)",
        "All four recordings"])
    box(208, 33, 126, 42, "Warning evaluation", [
        "Antarex labels only", "Point / event measures"])
    box(12, 0.5, 322, 19.5, "Local dashboard: archived replay and saved-model inference")

    arrow([(173, 309), (173, 290)])
    ax.plot([173, 173], [234, 222], color="black", lw=0.75)
    arrow([(173, 222), (93, 222), (93, 210)])
    arrow([(173, 222), (271, 222), (271, 210)])
    arrow([(271, 171), (271, 150)])
    arrow([(174, 157), (191, 157), (191, 130), (208, 130)])
    arrow([(93, 141), (93, 106)])
    arrow([(271, 91), (271, 75)])
    ax.plot([93, 93, 271, 271], [53, 26, 26, 33], color="black", lw=0.75)
    arrow([(173, 26), (173, 20)])

    fig.canvas.draw()
    for label, x, y, w, h in labels:
        bb = label.get_window_extent().transformed(ax.transData.inverted())
        assert bb.x0 >= x + 4 and bb.x1 <= x + w - 4, label.get_text()
        assert bb.y0 >= y + 2 and bb.y1 <= y + h - 2, label.get_text()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT / "architecture.pdf", metadata={"Creator": "", "Producer": "", "CreationDate": None})
    fig.savefig(OUTPUT / "architecture.svg")
    svg = OUTPUT / "architecture.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    fig.savefig(OUTPUT / "architecture.png", dpi=250)
    plt.close(fig)
    print("Architecture figure written as vector PDF/SVG and PNG preview.")


if __name__ == "__main__":
    main()
