"""Generate a professional diagram and PDF explaining loop engineering."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "visuals"
OUT.mkdir(exist_ok=True)


def main() -> None:
    labels = ["DEFINE", "BUILD", "MEASURE", "REVIEW", "ITERATE"]
    colors = ["#2563EB", "#0EA5E9", "#10B981", "#F59E0B", "#8B5CF6"]
    fig, ax = plt.subplots(figsize=(14, 6), constrained_layout=True)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")
    ax.axis("off")
    ax.text(
        0.5, 0.92, "Loop Engineering for Scientific AI",
        ha="center", va="center", fontsize=22, fontweight="bold", color="#0F172A",
    )
    ax.text(
        0.5, 0.82,
        "Turn every research run into an observable, reviewable, improvable cycle",
        ha="center", va="center", fontsize=11, color="#475569",
    )
    x_positions = [0.10, 0.30, 0.50, 0.70, 0.90]
    for index, (label, color, x) in enumerate(zip(labels, colors, x_positions)):
        ax.text(
            x, 0.52, label, ha="center", va="center", fontsize=12,
            fontweight="bold", color="white",
            bbox={"boxstyle": "round,pad=0.9", "facecolor": color, "edgecolor": color},
        )
        if index < len(labels) - 1:
            ax.annotate("", xy=(x_positions[index + 1] - 0.07, 0.52), xytext=(x + 0.07, 0.52),
                        arrowprops={"arrowstyle": "->", "lw": 2, "color": "#64748B"})
    ax.annotate("", xy=(0.10, 0.37), xytext=(0.90, 0.37),
                arrowprops={"arrowstyle": "->", "lw": 1.8, "color": "#8B5CF6",
                            "connectionstyle": "arc3,rad=-0.25"})
    ax.text(
        0.5, 0.16,
        "Benefits: faster learning  |  lower wasted compute  |  measurable quality  |  safer decisions  |  reproducible evidence",
        ha="center", va="center", fontsize=10, color="#334155",
        bbox={"boxstyle": "round,pad=0.55", "facecolor": "#E2E8F0", "edgecolor": "#CBD5E1"},
    )
    image_path = OUT / "loop_engineering_workflow.png"
    pdf_path = OUT / "loop_engineering_benefits.pdf"
    fig.savefig(image_path, dpi=240, bbox_inches="tight")
    with PdfPages(pdf_path) as pdf:
        pdf.savefig(fig, dpi=240, bbox_inches="tight")
    plt.close(fig)
    print(f"Created {image_path}")
    print(f"Created {pdf_path}")


if __name__ == "__main__":
    main()
