"""Generate a visual overview of the enterprise-inspired delivery lifecycle."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "visuals"
OUT.mkdir(exist_ok=True)


def main() -> None:
    stages = ["DISCOVER", "DESIGN", "BUILD", "VALIDATE", "RELEASE", "OPERATE", "EVOLVE"]
    colors = ["#1D4ED8", "#2563EB", "#0284C7", "#0F766E", "#15803D", "#B45309", "#7C3AED"]
    fig, ax = plt.subplots(figsize=(15, 7), constrained_layout=True)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")
    ax.axis("off")
    ax.text(0.5, 0.93, "Enterprise Software + AI Delivery Lifecycle",
            ha="center", va="center", fontsize=21, fontweight="bold", color="#0F172A")
    ax.text(0.5, 0.85, "A gated path from business value to safe operation and continuous evolution",
            ha="center", va="center", fontsize=11, color="#475569")
    xs = [0.08 + index * 0.14 for index in range(len(stages))]
    for index, (stage, color, x) in enumerate(zip(stages, colors, xs)):
        ax.text(x, 0.55, stage, ha="center", va="center", fontsize=10,
                fontweight="bold", color="white",
                bbox={"boxstyle": "round,pad=0.75", "facecolor": color, "edgecolor": color})
        if index < len(stages) - 1:
            ax.annotate("", xy=(xs[index + 1] - 0.055, 0.55), xytext=(x + 0.055, 0.55),
                        arrowprops={"arrowstyle": "->", "lw": 1.8, "color": "#64748B"})
    ax.annotate("", xy=(xs[0], 0.39), xytext=(xs[-1], 0.39),
                arrowprops={"arrowstyle": "->", "lw": 1.6, "color": "#7C3AED",
                            "connectionstyle": "arc3,rad=-0.22"})
    ax.text(0.5, 0.18,
            "Gates: value • architecture • tests • evidence • safety • release • monitoring • feedback",
            ha="center", va="center", fontsize=10, color="#334155",
            bbox={"boxstyle": "round,pad=0.6", "facecolor": "#E2E8F0", "edgecolor": "#CBD5E1"})
    image_path = OUT / "enterprise_ai_delivery_workflow.png"
    pdf_path = OUT / "enterprise_ai_delivery_benefits.pdf"
    fig.savefig(image_path, dpi=240, bbox_inches="tight")
    with PdfPages(pdf_path) as pdf:
        pdf.savefig(fig, dpi=240, bbox_inches="tight")
    plt.close(fig)
    print(f"Created {image_path}")
    print(f"Created {pdf_path}")


if __name__ == "__main__":
    main()
