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


def main() -> None:
    save_summary_json()
    plot_risk_factors()
    plot_therapy_landscape()
    plot_cure_status()
    print("Created MS visuals in:", VISUALS)
    for name in [
        "ms_risk_factors.png",
        "ms_therapy_landscape.png",
        "ms_cure_status.png",
    ]:
        print(" -", name)


if __name__ == "__main__":
    main()
