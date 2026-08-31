#!/usr/bin/env python3
"""Generate polished, publication-style scientific visuals and a PDF summary.

These visuals explain the recommended methods and the project architecture in a
clear, professional format for stakeholder reviews, portfolio presentations, and
technical reports.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parent.parent
VISUALS_DIR = ROOT / "visuals"
VISUALS_DIR.mkdir(exist_ok=True)

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
        "axes.titlesize": 16,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.facecolor": "#F8FAFC",
        "axes.facecolor": "#FFFFFF",
        "savefig.facecolor": "#F8FAFC",
    }
)


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
        (
            pl.col("fit") * 0.45
            + pl.col("adoption") * 0.25
            + pl.col("practicality") * 0.30
        ).alias("overall")
    ).sort("overall", descending=True)

    fig, ax = plt.subplots(figsize=(13, 7), constrained_layout=True)
    fig.patch.set_facecolor("#F8FAFC")

    methods = scores["method"].to_list()
    values = scores["overall"].to_list()
    colors = ["#1D4ED8", "#0EA5E9", "#10B981", "#F59E0B", "#8B5CF6", "#EF4444"]

    bars = ax.barh(methods, values, color=colors, edgecolor="#0F172A", linewidth=1.0)
    ax.invert_yaxis()
    ax.set_title("Recommended research methods ranked by practical scientific value", pad=16)
    ax.set_xlabel("Overall score (0-10)")
    ax.set_xlim(0, 10)
    ax.grid(axis="x", linestyle="--", linewidth=0.8, alpha=0.35)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color("#1E293B")
    ax.spines["bottom"].set_color("#1E293B")

    for bar, value in zip(bars, values):
        ax.text(value + 0.12, bar.get_y() + bar.get_height() / 2, f"{value:.1f}", va="center", fontsize=10, fontweight="bold")

    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_architecture_flow(output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 8), constrained_layout=True)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    boxes = {
        "Question": (9, 74, 18, 12),
        "Literature search": (31, 74, 24, 12),
        "Evidence extraction": (58, 74, 22, 12),
        "Analysis & ranking": (29, 48, 28, 12),
        "Simulation / tools": (61, 48, 24, 12),
        "Dashboard & reports": (45, 22, 28, 12),
    }

    colors = {
        "Question": "#DBEAFE",
        "Literature search": "#BFDBFE",
        "Evidence extraction": "#DDD6FE",
        "Analysis & ranking": "#BBF7D0",
        "Simulation / tools": "#FDE68A",
        "Dashboard & reports": "#FBCFE8",
    }

    for label, (x, y, w, h) in boxes.items():
        rect = plt.Rectangle((x, y), w, h, facecolor=colors[label], edgecolor="#0F172A", linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=12, fontweight="bold")

    arrows = [
        ((27, 80), (31, 80)),
        ((55, 80), (58, 80)),
        ((43, 68), (43, 60)),
        ((57, 60), (61, 60)),
        ((43, 42), (43, 34)),
        ((57, 42), (57, 34)),
    ]
    for start, end in arrows:
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            arrowprops=dict(arrowstyle="-|>", lw=1.7, color="#334155"),
        )

    ax.text(10, 92, "Scientific workflow", fontsize=22, fontweight="bold", color="#0F172A")
    ax.text(31, 11, "Evidence-backed decision-making and reproducible outputs", fontsize=12, color="#334155", style="italic")

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
    domains = ["Materials", "Biomedicine", "Climate", "Physics", "Chemistry", "Education"]
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

    fig, ax = plt.subplots(figsize=(12, 8), constrained_layout=True)
    fig.patch.set_facecolor("#F8FAFC")
    im = ax.imshow(matrix, cmap="viridis", aspect="auto", vmin=5, vmax=9)
    ax.set_xticks(range(len(domains)))
    ax.set_yticks(range(len(methods)))
    ax.set_xticklabels(domains)
    ax.set_yticklabels(methods)
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    plt.setp(ax.get_yticklabels(), fontsize=10)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(
                j,
                i,
                f"{matrix[i, j]}",
                ha="center",
                va="center",
                color="white" if matrix[i, j] < 7.5 else "black",
                fontsize=10,
                fontweight="bold",
            )

    ax.set_title("Best-fit method by research domain", pad=16)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Fit score (0-10)", rotation=270, labelpad=18)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def create_professional_pdf(output_path: Path) -> None:
    with PdfPages(output_path) as pdf:
        title_fig = plt.figure(figsize=(11.69, 8.27))
        title_fig.patch.set_facecolor("#F8FAFC")
        ax = title_fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        ax.text(
            0.5,
            0.78,
            "Autonomous Scientific Research Platform",
            ha="center",
            va="center",
            fontsize=28,
            fontweight="bold",
            color="#0F172A",
        )
        ax.text(
            0.5,
            0.66,
            "Professional overview of the strongest research methods and workflow design",
            ha="center",
            va="center",
            fontsize=15,
            color="#334155",
        )
        ax.text(
            0.5,
            0.52,
            "Evidence-backed AI • Active learning • Scientific agents • Observability • Reproducibility",
            ha="center",
            va="center",
            fontsize=12,
            color="#475569",
        )
        ax.text(
            0.5,
            0.14,
            "Prepared for strategic review, portfolio presentation, and technical communication.",
            ha="center",
            va="center",
            fontsize=11,
            color="#64748B",
        )
        pdf.savefig(title_fig, dpi=220)
        plt.close(title_fig)

        fig1 = plt.figure(figsize=(13.5, 7.5))
        fig1.patch.set_facecolor("#F8FAFC")
        method_df = build_method_frame()
        scores = method_df.with_columns(
            (
                pl.col("fit") * 0.45
                + pl.col("adoption") * 0.25
                + pl.col("practicality") * 0.30
            ).alias("overall")
        ).sort("overall", descending=True)
        ax1 = fig1.add_subplot(111)
        methods = scores["method"].to_list()
        values = scores["overall"].to_list()
        colors = ["#1D4ED8", "#0EA5E9", "#10B981", "#F59E0B", "#8B5CF6", "#EF4444"]
        bars = ax1.barh(methods, values, color=colors, edgecolor="#0F172A", linewidth=1.0)
        ax1.invert_yaxis()
        ax1.set_title("Recommended research methods ranked by practical scientific value", pad=16)
        ax1.set_xlabel("Overall score (0-10)")
        ax1.set_xlim(0, 10)
        ax1.grid(axis="x", linestyle="--", linewidth=0.8, alpha=0.35)
        for side in ["top", "right"]:
            ax1.spines[side].set_visible(False)
        ax1.spines["left"].set_color("#1E293B")
        ax1.spines["bottom"].set_color("#1E293B")
        for bar, value in zip(bars, values):
            ax1.text(value + 0.12, bar.get_y() + bar.get_height() / 2, f"{value:.1f}", va="center", fontsize=10, fontweight="bold")
        pdf.savefig(fig1, dpi=220)
        plt.close(fig1)

        flow_fig = plt.figure(figsize=(14, 8))
        flow_fig.patch.set_facecolor("#F8FAFC")
        flow_ax = flow_fig.add_subplot(111)
        flow_ax.set_xlim(0, 100)
        flow_ax.set_ylim(0, 100)
        flow_ax.axis("off")
        boxes = {
            "Question": (9, 74, 18, 12),
            "Literature search": (31, 74, 24, 12),
            "Evidence extraction": (58, 74, 22, 12),
            "Analysis & ranking": (29, 48, 28, 12),
            "Simulation / tools": (61, 48, 24, 12),
            "Dashboard & reports": (45, 22, 28, 12),
        }
        colors = {
            "Question": "#DBEAFE",
            "Literature search": "#BFDBFE",
            "Evidence extraction": "#DDD6FE",
            "Analysis & ranking": "#BBF7D0",
            "Simulation / tools": "#FDE68A",
            "Dashboard & reports": "#FBCFE8",
        }
        for label, (x, y, w, h) in boxes.items():
            flow_ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=colors[label], edgecolor="#0F172A", linewidth=1.5))
            flow_ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=12, fontweight="bold")
        for start, end in [
            ((27, 80), (31, 80)),
            ((55, 80), (58, 80)),
            ((43, 68), (43, 60)),
            ((57, 60), (61, 60)),
            ((43, 42), (43, 34)),
            ((57, 42), (57, 34)),
        ]:
            flow_ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="-|>", lw=1.7, color="#334155"))
        flow_ax.text(10, 92, "Scientific workflow", fontsize=22, fontweight="bold", color="#0F172A")
        flow_ax.text(31, 11, "Evidence-backed decision-making and reproducible outputs", fontsize=12, color="#334155", style="italic")
        pdf.savefig(flow_fig, dpi=220)
        plt.close(flow_fig)

        heatmap_fig = plt.figure(figsize=(12, 8))
        heatmap_fig.patch.set_facecolor("#F8FAFC")
        heatmap_ax = heatmap_fig.add_subplot(111)
        methods = [
            "Evidence-grounded scientific RAG",
            "Tool-using scientific agents",
            "Active learning & Bayesian optimization",
            "Multi-agent reasoning",
            "Surrogate models + simulation",
            "Claim-aware observability",
        ]
        domains = ["Materials", "Biomedicine", "Climate", "Physics", "Chemistry", "Education"]
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
        im = heatmap_ax.imshow(matrix, cmap="viridis", aspect="auto", vmin=5, vmax=9)
        heatmap_ax.set_xticks(range(len(domains)))
        heatmap_ax.set_yticks(range(len(methods)))
        heatmap_ax.set_xticklabels(domains)
        heatmap_ax.set_yticklabels(methods)
        plt.setp(heatmap_ax.get_xticklabels(), rotation=35, ha="right")
        plt.setp(heatmap_ax.get_yticklabels(), fontsize=10)
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                heatmap_ax.text(
                    j,
                    i,
                    f"{matrix[i, j]}",
                    ha="center",
                    va="center",
                    color="white" if matrix[i, j] < 7.5 else "black",
                    fontsize=10,
                    fontweight="bold",
                )
        heatmap_ax.set_title("Best-fit method by research domain", pad=16)
        cbar = heatmap_fig.colorbar(im, ax=heatmap_ax, fraction=0.046, pad=0.04)
        cbar.set_label("Fit score (0-10)", rotation=270, labelpad=18)
        pdf.savefig(heatmap_fig, dpi=220)
        plt.close(heatmap_fig)


def main() -> None:
    method_df = build_method_frame()
    fig1 = VISUALS_DIR / "method_ranking.png"
    fig2 = VISUALS_DIR / "workflow_overview.png"
    fig3 = VISUALS_DIR / "domain_fit_heatmap.png"
    pdf_path = VISUALS_DIR / "scientific_summary_report.pdf"

    plot_method_ranking(method_df, fig1)
    plot_architecture_flow(fig2)
    plot_domain_fit_heatmap(fig3)
    create_professional_pdf(pdf_path)

    print(f"Created visuals in {VISUALS_DIR}")
    for path in [fig1, fig2, fig3, pdf_path]:
        print(f" - {path.name}")


if __name__ == "__main__":
    main()
