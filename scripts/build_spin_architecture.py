"""Redraw the supplied workflow at the LLNCS manuscript's printed column width.

Wording and connections match architecture_uploaded.png. Line wrapping, box
proportions, spacing and typography change to fit a standard portrait page.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "paper/spin2027_no_disclosure/figures"
WIDTH, HEIGHT = 346, 456
NAVY, BODY, MUTED, EDGE = "#192e4e", "#354353", "#57697e", "#66798d"


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42,
                         "ps.fonttype": 42, "svg.fonttype": "none"})
    fig = plt.figure(figsize=(WIDTH / 72, HEIGHT / 72))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, WIDTH), ylim=(0, HEIGHT))
    ax.axis("off")
    labels, wording = [], []

    def text(x, y, value, size=8.0, weight="normal", color=BODY,
             bounds=None, rotation=0):
        artist = ax.text(x, y, value, ha="center", va="center", fontsize=size,
                         fontweight=weight, color=color, rotation=rotation,
                         linespacing=1.25, zorder=3)
        if bounds:
            labels.append((artist, bounds))
        return artist

    def box(x, y, width, height, title, title_y, lines, fill, border, dark=False):
        ax.add_patch(FancyBboxPatch((x, y), width, height,
                     boxstyle="round,pad=0,rounding_size=4", facecolor=fill,
                     edgecolor=border, linewidth=0.75, zorder=2))
        bounds = (x, y, width, height)
        text(x + width / 2, title_y, title, 9.0, "bold",
             "white" if dark else NAVY, bounds)
        wording.append(title)
        for value, line_y, size in lines:
            text(x + width / 2, line_y, value, size,
                 color="white" if dark else BODY, bounds=bounds)
            wording.append(value.replace("\n", " "))

    def line(points):
        ax.plot([p[0] for p in points], [p[1] for p in points],
                color=EDGE, lw=0.85, zorder=1)

    def arrow(points):
        if len(points) > 2:
            line(points[:-1])
        ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle="-|>",
                    mutation_scale=7, lw=0.85, color=EDGE,
                    shrinkA=0, shrinkB=1, zorder=1))

    title = "Telemetry forecasting and warning workflow"
    text(173, 444, title, 10.3, "bold", NAVY, (0, 433, WIDTH, 23))
    wording.append(title)
    box(4, 376, 338, 52, "Archived telemetry", 415, [
        ("Antarex: 5-second intervals · Westermo", 400, 8.2),
        ("systems 1–3: 30-second intervals", 388, 8.2),
    ], "#edf6fe", "#9bbfe0")
    box(4, 294, 338, 68, "Causal data preparation", 348, [
        ("Align observations and calculate rates using past data only;", 333, 8.0),
        ("retain gaps", 322, 8.0),
        ("Chronological split: 70% training · 15% validation · 15% test", 302, 8.0),
    ], "#f2effd", "#b5a5e1")
    box(4, 166, 158, 105, "Forecast models", 257, [
        ("Persistence and linear-trend", 242, 8.0),
        ("baselines", 231, 8.0),
        ("Restricted ARIMA and LSTM", 217, 8.0),
        ("History: 60 observations ·", 202, 8.0),
        ("Forecast durations:", 191, 8.0),
        ("60 s and 300 s", 180, 8.0),
    ], "#edf8f2", "#97c5af")
    box(184, 203, 158, 68, "Observed growth", 257, [
        ("Slope from the latest 12", 242, 8.0),
        ("memory readings", 231, 8.0),
        ("Measured in percentage points", 219, 7.5),
        ("of RAM per minute", 210.5, 7.5),
    ], "#edf8f2", "#97c5af")
    box(184, 111, 158, 81, "Warning rules", 178, [
        ("Trend-only rule or ARIMA/LSTM", 163, 8.0),
        ("forecast plus trend", 152, 8.0),
        ("Require three consecutive", 137, 8.0),
        ("readings", 126, 8.0),
    ], "#fff8e8", "#dfc682")
    box(4, 73, 158, 79, "Forecast evaluation", 138, [
        ("Compare forecasts with", 123, 8.0),
        ("future observations", 112, 8.0),
        ("MAE and RMSE in percentage", 100, 8.0),
        ("points of RAM", 89, 8.0),
        ("Evaluate all four recordings", 80.5, 7.5),
    ], "#f3f6fc", "#b5c2d2")
    box(184, 39, 158, 58, "Warning evaluation", 84, [
        ("Antarex labels only", 69, 8.0),
        ("Point-level and event-level", 56, 8.0),
        ("measures", 46.5, 8.0),
    ], "#f3f6fc", "#b5c2d2")
    box(4, 1, 338, 28, "Local dashboard", 20, [
        ("Archived-data replay and inference with saved models", 8.5, 8.0),
    ], NAVY, NAVY, dark=True)

    arrow([(173, 376), (173, 362)])
    line([(173, 294), (173, 283)])
    arrow([(173, 283), (83, 283), (83, 271)])
    arrow([(173, 283), (263, 283), (263, 271)])
    arrow([(263, 203), (263, 192)])
    arrow([(162, 214), (172, 214), (172, 158), (184, 158)])
    text(177.5, 186, "forecast input", 7.5, color=MUTED, rotation=270,
         bounds=(172.7, 158, 10, 56))
    wording.append("forecast input")
    arrow([(83, 166), (83, 152)])
    arrow([(263, 111), (263, 97)])
    line([(83, 73), (83, 35), (263, 35), (263, 39)])
    arrow([(173, 35), (173, 29)])

    fig.canvas.draw()
    for artist, (x, y, width, height) in labels:
        bb = artist.get_window_extent().transformed(ax.transData.inverted())
        assert bb.x0 >= x + 1 and bb.x1 <= x + width - 1, artist.get_text()
        assert bb.y0 >= y + 0.5 and bb.y1 <= y + height - 0.5, artist.get_text()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT / "architecture.pdf", metadata={
        "Title": title, "Creator": "", "Producer": "", "CreationDate": None})
    fig.savefig(OUTPUT / "architecture.svg")
    svg = OUTPUT / "architecture.svg"
    svg.write_text("\n".join(line.rstrip() for line in
                   svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    fig.savefig(OUTPUT / "architecture.png", dpi=250)
    plt.close(fig)
    print(json.dumps({"figure_width_pt": WIDTH, "figure_height_pt": HEIGHT,
                      "minimum_font_pt": 7.5, "label_bounds_checked": len(labels),
                      "wording": wording}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
