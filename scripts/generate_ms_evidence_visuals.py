from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
VISUALS = ROOT / "visuals"
VISUALS.mkdir(exist_ok=True)

RISK_FACTORS = [
    ("Genetic susceptibility", 8.8, "HLA risk and family history"),
    ("Immune dysregulation", 9.6, "Autoreactive T/B-cell activity"),
    ("EBV exposure", 9.2, "Strongest environmental signal"),
    ("Smoking", 8.7, "Higher risk and disease activity"),
    ("Vitamin D / UV", 8.5, "Lower exposure linked to higher risk"),
    ("Obesity / BMI", 7.4, "Metabolic risk contribution"),
    ("Gut microbiome", 6.8, "Emerging but not definitive"),
]

THERAPIES = [
    ("Standard DMTs", 9.1, 8.5, "Established; reduces relapses"),
    ("HSCT", 6.2, 8.3, "Selected severe cases; remission potential"),
    ("CAR T-cell", 3.1, 8.7, "Experimental; immune reset approach"),
    ("MSC therapy", 4.1, 5.5, "Investigational; mixed evidence"),
]

POTENTIAL_SOLUTION_PATHS = [
    ("Immune dysregulation", "Standard DMTs", 9.0, "Strongest current therapeutic leverage"),
    ("Immune dysregulation", "HSCT", 8.4, "Most aggressive reset strategy for selected severe cases"),
    ("Immune dysregulation", "CAR T-cell", 8.8, "Experimental immune reprogramming"),
    ("EBV exposure", "EBV-focused research", 7.6, "Prevention and immune surveillance research"),
    ("Smoking", "Lifestyle intervention", 8.2, "Risk reduction and disease activity moderation"),
    ("Vitamin D / UV", "Lifestyle intervention", 7.9, "Modifiable environmental risk factor"),
    ("Obesity / BMI", "Lifestyle intervention", 7.2, "Metabolic risk modulation"),
    ("Genetic susceptibility", "Precision monitoring", 6.9, "Personalized risk and surveillance"),
]


def save_summary_json() -> None:
    payload = {
        "project": "Multiple Sclerosis evidence summary",
        "educational_note": "This is a qualitative evidence summary, not medical advice.",
        "cause_model": {
            "genetic_risk": "High",
            "environmental_triggers": ["EBV", "low vitamin D", "smoking", "obesity"],
            "core_mechanism": "Autoimmune inflammation and demyelination of the central nervous system",
        },
        "risk_factors": [
            {"name": name, "score": score, "note": note}
            for name, score, note in [(x[0], x[1], x[2]) for x in RISK_FACTORS]
        ],
        "therapies": [
            {
                "name": name,
                "evidence_maturity": evidence,
                "potential_benefit": benefit,
                "summary": description,
            }
            for name, evidence, benefit, description in THERAPIES
        ],
    }
    (ROOT / "data" / "ms_evidence_summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def plot_risk_factors() -> Path:
    labels = [item[0] for item in RISK_FACTORS]
    values = [item[1] for item in RISK_FACTORS]
    fig, ax = plt.subplots(figsize=(11, 7), constrained_layout=True)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")
    colors = ["#2563EB", "#0EA5E9", "#8B5CF6", "#10B981", "#F59E0B", "#EC4899", "#475569"]
    bars = ax.barh(labels, values, color=colors, edgecolor="#0F172A", linewidth=0.8)
    ax.invert_yaxis()
    ax.set_title("MS risk-factor evidence strength (qualitative synthesis)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Evidence strength (0-10)")
    ax.set_xlim(0, 10)
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    for bar, value in zip(bars, values):
        ax.text(value + 0.15, bar.get_y() + bar.get_height() / 2, f"{value:.1f}", va="center", fontsize=9, fontweight="bold")
    out = VISUALS / "ms_risk_factors.png"
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_therapy_landscape() -> Path:
    labels = [item[0] for item in THERAPIES]
    evidence = [item[1] for item in THERAPIES]
    benefit = [item[2] for item in THERAPIES]
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 7), constrained_layout=True)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")
    ax.bar(x - width / 2, evidence, width, label="Evidence maturity", color="#2563EB")
    ax.bar(x + width / 2, benefit, width, label="Potential benefit", color="#10B981")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=18, ha="right")
    ax.set_title("MS therapy landscape: evidence maturity vs potential benefit", fontsize=14, fontweight="bold")
    ax.set_ylabel("Score (0-10)")
    ax.set_ylim(0, 10)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend()
    out = VISUALS / "ms_therapy_landscape.png"
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_cure_status() -> Path:
    categories = ["Established cure", "Cure-like remission", "Exploratory", "Early investigational"]
    values = [0, 2, 3, 5]
    fig, ax = plt.subplots(figsize=(9, 6), constrained_layout=True)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")
    colors = ["#D1D5DB", "#60A5FA", "#F59E0B", "#EF4444"]
    bars = ax.bar(categories, values, color=colors)
    ax.set_title("Cure status in MS: current evidence level", fontsize=14, fontweight="bold")
    ax.set_ylabel("Relative maturity")
    ax.set_ylim(0, 6)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.15, str(v), ha="center", va="bottom", fontsize=10, fontweight="bold")
    out = VISUALS / "ms_cure_status.png"
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_solution_paths() -> Path:
    risk_names = [item[0] for item in RISK_FACTORS]
    intervention_names = list(dict.fromkeys([item[1] for item in POTENTIAL_SOLUTION_PATHS]))
    matrix = np.zeros((len(risk_names), len(intervention_names)), dtype=float)
    for risk_name, intervention_name, score, _ in POTENTIAL_SOLUTION_PATHS:
        row = risk_names.index(risk_name)
        col = intervention_names.index(intervention_name)
        matrix[row, col] = score

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")
    heatmap = ax.imshow(matrix, cmap="viridis", aspect="auto", vmin=0, vmax=10)
    ax.set_xticks(np.arange(len(intervention_names)))
    ax.set_xticklabels(intervention_names, rotation=24, ha="right")
    ax.set_yticks(np.arange(len(risk_names)))
    ax.set_yticklabels(risk_names)
    ax.set_title("Evidence-to-solution relevance matrix for MS", fontsize=14, fontweight="bold")
    ax.set_xlabel("Potential solution direction")
    ax.set_ylabel("Risk factor / disease driver")

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if matrix[i, j] > 0:
                ax.text(j, i, f"{matrix[i, j]:.1f}", ha="center", va="center", color="white", fontsize=8, fontweight="bold")

    fig.colorbar(heatmap, ax=ax, fraction=0.046, pad=0.04)
    out = VISUALS / "ms_solution_matrix.png"
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_solution_pipeline() -> Path:
    labels = ["Risk genes", "Immune trigger", "EBV / lifestyle", "Disease-modifying therapy", "HSCT / CAR T / MSC"]
    values = [8.8, 9.6, 8.7, 8.5, 7.9]
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")
    ax.plot(range(len(labels)), values, color="#2563EB", marker="o", linewidth=2.5, markersize=7)
    ax.fill_between(range(len(labels)), values, alpha=0.18, color="#60A5FA")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=18, ha="right")
    ax.set_ylim(0, 10)
    ax.set_title("Possible solution path: from cause model to intervention strategy", fontsize=14, fontweight="bold")
    ax.set_ylabel("Evidence / intervention relevance (0-10)")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    out = VISUALS / "ms_solution_pipeline.png"
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    save_summary_json()
    plot_risk_factors()
    plot_therapy_landscape()
    plot_cure_status()
    plot_solution_paths()
    plot_solution_pipeline()
    print("Created MS visuals in:", VISUALS)
    for name in [
        "ms_risk_factors.png",
        "ms_therapy_landscape.png",
        "ms_cure_status.png",
        "ms_solution_matrix.png",
        "ms_solution_pipeline.png",
    ]:
        print(" -", name)


if __name__ == "__main__":
    main()
