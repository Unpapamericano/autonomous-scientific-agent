#!/usr/bin/env python3
"""Generate clear, scientific visuals for the project.

These visuals explain the recommended methods and the project architecture in an
accessible way for students, researchers, and technical stakeholders.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parent.parent
VISUALS_DIR = ROOT / "visuals"
VISUALS_DIR.mkdir(exist_ok=True)


def build_method_frame() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "method": [
                "Evidence-grounded scientific RAG",
                "Tool-using scientific agents",
                "Active learning & Bayesian optimization",
                "Multi-agent reasoning",
                "Surrogate models + simulation",
                "Claim-aware observability",
            ],
            "fit": [9.3, 9.1, 8.9, 8.6, 8.4, 8.1],
            "adoption": [8.7, 8.8, 8.5, 7.9, 8.1, 7.8],
            "practicality": [9.0, 8.9, 8.7, 7.8, 8.2, 8.4],
        }
    )


def plot_method_ranking(df: pl.DataFrame, output_path: Path) -> None:
    scores = df.with_columns(
        (pl.col("fit") * 0.45 + pl.col("adoption") * 0.25 + pl.col("practicality") * 0.30).alias("overall")
    ).sort("overall", descending=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    methods = scores["method"].to_list()
    values = scores["overall"].to_list()
    colors = ["#2563eb", "#0ea5e9", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"]

    bars = ax.barh(methods, values, color=colors, edgecolor="black", linewidth=0.8)
    ax.invert_yaxis()
    ax.set_title("Recommended research methods ranked by practical scientific value", fontsize=15, fontweight="bold")
    ax.set_xlabel("Overall score (0-10)")
    ax.set_xlim(0, 10)
    ax.grid(axis="x", linestyle="--", alpha=0.35)

    for bar, value in zip(bars, values):
        ax.text(value + 0.12, bar.get_y() + bar.get_height() / 2, f"{value:.1f}", va="center", fontsize=10)

    plt.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def plot_architecture_flow(output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    boxes = {
        "Question": (12, 74, 16, 12),
        "Literature search": (32, 74, 24, 12),
        "Evidence extraction": (58, 74, 22, 12),
        "Analysis & ranking": (34, 50, 26, 12),
        "Simulation / tools": (62, 50, 24, 12),
        "Dashboard & reports": (48, 26, 26, 12),
    }

    colors = {
        "Question": "#dbeafe",
        "Literature search": "#bfdbfe",
        "Evidence extraction": "#c7d2fe",
        "Analysis & ranking": "#bbf7d0",
        "Simulation / tools": "#fef3c7",
        "Dashboard & reports": "#fee2e2",
    }

    for label, (x, y, w, h) in boxes.items():
        rect = plt.Rectangle((x, y), w, h, facecolor=colors[label], edgecolor="#1f2937", linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=11, fontweight="bold")

    arrows = [
        ((28, 80), (32, 80)),
        ((56, 80), (58, 80)),
        ((47, 68), (47, 62)),
        ((60, 56), (62, 56)),
        ((52, 44), (52, 38)),
    ]
    for start, end in arrows:
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            arrowprops=dict(arrowstyle="-|>", lw=1.8, color="#374151"),
        )

    ax.text(10, 92, "Scientific workflow", fontsize=18, fontweight="bold")
    ax.text(30, 16, "Evidence-backed decision-making and reproducible outputs", fontsize=12, color="#374151")

    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_domain_fit_heatmap(output_path: Path) -> None:
    methods = [
        "Evidence-grounded scientific RAG",
        "Tool-using scientific agents",
        "Active learning & Bayesian optimization",
        "Multi-agent reasoning",
        "Surrogate models + simulation",
        "Claim-aware observability",
    ]
    domains = [
        "Materials",
        "Biomedicine",
        "Climate",
        "Physics",
        "Chemistry",
        "Education",
    ]
    matrix = np.array(
        [
            [9, 7, 6, 8, 8, 6],
            [7, 9, 6, 6, 7, 8],
            [6, 6, 9, 7, 7, 6],
            [8, 6, 7, 9, 8, 5],
            [7, 7, 7, 8, 9, 6],
            [6, 8, 6, 5, 6, 9],
        ]
    )

    fig, ax = plt.subplots(figsize=(11, 7))
    im = ax.imshow(matrix, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(domains)))
    ax.set_yticks(range(len(methods)))
    ax.set_xticklabels(domains)
    ax.set_yticklabels(methods)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    plt.setp(ax.get_yticklabels(), fontsize=9)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i, j]}", ha="center", va="center", color="white" if matrix[i, j] < 7 else "black", fontsize=9)

    ax.set_title("Best-fit method by research domain", fontsize=15, fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def main() -> None:
    method_df = build_method_frame()
    fig1 = VISUALS_DIR / "method_ranking.png"
    fig2 = VISUALS_DIR / "workflow_overview.png"
    fig3 = VISUALS_DIR / "domain_fit_heatmap.png"

    plot_method_ranking(method_df, fig1)
    plot_architecture_flow(fig2)
    plot_domain_fit_heatmap(fig3)

    print(f"Created visuals in {VISUALS_DIR}")
    for path in [fig1, fig2, fig3]:
        print(f" - {path.name}")


if __name__ == "__main__":
    main()
