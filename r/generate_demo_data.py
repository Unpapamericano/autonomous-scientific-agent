#!/usr/bin/env python3
"""Generate sample scientific benchmark datasets for the R/Shiny dashboard."""

from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

math_df = pl.DataFrame(
    [
        {"study_id": "M-001", "topic": "algebra", "question_id": "algebra_1", "absolute_error": 0.28, "passed": True, "difficulty": "medium", "score": 96},
        {"study_id": "M-002", "topic": "algebra", "question_id": "algebra_2", "absolute_error": 0.31, "passed": True, "difficulty": "hard", "score": 92},
        {"study_id": "M-003", "topic": "geometry", "question_id": "geometry_1", "absolute_error": 0.44, "passed": False, "difficulty": "medium", "score": 77},
        {"study_id": "M-004", "topic": "geometry", "question_id": "geometry_2", "absolute_error": 0.19, "passed": True, "difficulty": "easy", "score": 98},
        {"study_id": "M-005", "topic": "calculus", "question_id": "calculus_1", "absolute_error": 0.25, "passed": True, "difficulty": "hard", "score": 90},
        {"study_id": "M-006", "topic": "calculus", "question_id": "calculus_2", "absolute_error": 0.68, "passed": False, "difficulty": "hard", "score": 64},
        {"study_id": "M-007", "topic": "statistics", "question_id": "statistics_1", "absolute_error": 0.18, "passed": True, "difficulty": "easy", "score": 99},
        {"study_id": "M-008", "topic": "statistics", "question_id": "statistics_2", "absolute_error": 0.52, "passed": False, "difficulty": "medium", "score": 71},
        {"study_id": "M-009", "topic": "probability", "question_id": "probability_1", "absolute_error": 0.35, "passed": True, "difficulty": "medium", "score": 88},
        {"study_id": "M-010", "topic": "probability", "question_id": "probability_2", "absolute_error": 0.59, "passed": False, "difficulty": "hard", "score": 67},
    ]
)
math_df.write_csv(DATA_DIR / "math_results.csv", include_header=True)

quantum_df = pl.DataFrame(
    [
        {"study_id": "Q-001", "timestamp": "2024-01-05T08:00:00Z", "run_id": "run_01", "coherence": 0.93, "fidelity": 0.96, "noise": 0.04, "drift_index": 0.08, "calibration_score": 0.97, "cost": 18.5, "quality": 96.2},
        {"study_id": "Q-002", "timestamp": "2024-01-07T10:00:00Z", "run_id": "run_02", "coherence": 0.88, "fidelity": 0.91, "noise": 0.09, "drift_index": 0.12, "calibration_score": 0.92, "cost": 16.1, "quality": 92.4},
        {"study_id": "Q-003", "timestamp": "2024-01-09T12:00:00Z", "run_id": "run_03", "coherence": 0.84, "fidelity": 0.89, "noise": 0.11, "drift_index": 0.15, "calibration_score": 0.89, "cost": 15.3, "quality": 88.5},
        {"study_id": "Q-004", "timestamp": "2024-01-12T09:30:00Z", "run_id": "run_04", "coherence": 0.90, "fidelity": 0.94, "noise": 0.06, "drift_index": 0.09, "calibration_score": 0.95, "cost": 17.6, "quality": 94.8},
        {"study_id": "Q-005", "timestamp": "2024-01-14T15:15:00Z", "run_id": "run_05", "coherence": 0.79, "fidelity": 0.82, "noise": 0.18, "drift_index": 0.24, "calibration_score": 0.81, "cost": 12.7, "quality": 81.6},
        {"study_id": "Q-006", "timestamp": "2024-01-15T16:45:00Z", "run_id": "run_06", "coherence": 0.95, "fidelity": 0.97, "noise": 0.03, "drift_index": 0.05, "calibration_score": 0.98, "cost": 20.8, "quality": 97.4},
        {"study_id": "Q-007", "timestamp": "2024-01-18T11:05:00Z", "run_id": "run_07", "coherence": 0.86, "fidelity": 0.90, "noise": 0.10, "drift_index": 0.13, "calibration_score": 0.91, "cost": 14.9, "quality": 89.9},
        {"study_id": "Q-008", "timestamp": "2024-01-22T13:40:00Z", "run_id": "run_08", "coherence": 0.92, "fidelity": 0.95, "noise": 0.05, "drift_index": 0.07, "calibration_score": 0.96, "cost": 18.9, "quality": 95.8},
    ]
)
quantum_df.write_csv(DATA_DIR / "quantum_results.csv", include_header=True)

print(f"Generated {len(math_df)} math results and {len(quantum_df)} quantum records in {DATA_DIR}")
