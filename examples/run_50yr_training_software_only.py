"""
Run the 50-Year Roadmap — TRAINING PHASES ONLY — SOFTWARE ONLY (no hardware)

Executes all 5 eras of docs/roadmap/50_year_features.md (2026 → 2076)
through the real Training Fabric:

    DATAFORGE → SYNTHFORGE → CURRICULUM → NEURAL FOUNDRY → RL
    → EVOLUTION → DISTILLATION → FAILURE MEMORY E_{t+1}=E_t∪F_t
    → EVALUATION FABRIC + RED TEAM

All hardware phases (quantum/neuromorphic chips, BCI, SCADA, robotics,
HAL, bare-metal, space tier) are SKIPPED.

Run: python examples/run_50yr_training_software_only.py
Saves full JSON report to training_runs/50yr_training_report.json (gitignored).
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sparsiz.v2.roadmap_trainer import FiftyYearTrainingRunner


def main():
    runner = FiftyYearTrainingRunner(software_only=True)
    summary = runner.run_all()

    out_dir = os.path.join(os.path.dirname(__file__), "..", "training_runs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.abspath(os.path.join(out_dir, "50yr_training_report.json"))
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[report] full JSON report saved: {out_path}")


if __name__ == "__main__":
    main()
