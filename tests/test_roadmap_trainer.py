"""Tests for the 50-year roadmap training runner — software only."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sparsiz.v2.roadmap_trainer import (
    FiftyYearTrainingRunner, FIFTY_YEAR_ERAS, HARDWARE_PHASES_SKIPPED,
)


def test_five_eras_2026_to_2076():
    assert len(FIFTY_YEAR_ERAS) == 5
    assert FIFTY_YEAR_ERAS[0].years == "2026"
    assert FIFTY_YEAR_ERAS[-1].years == "2050-2076"
    assert FIFTY_YEAR_ERAS[-1].version == "v5.0-agi-50-year"


def test_software_only_enforced():
    with pytest.raises(ValueError):
        FiftyYearTrainingRunner(software_only=False)


def test_full_run_all_phases_no_hardware(capsys):
    runner = FiftyYearTrainingRunner(software_only=True)
    summary = runner.run_all()
    assert summary["eras_completed"] == 5
    assert summary["training_phases_per_era"] == 9
    assert summary["hardware_phases_skipped"] == HARDWARE_PHASES_SKIPPED
    # every era ran every training phase and skipped hardware
    for era_report in summary["eras"]:
        assert set(era_report["phases"]) == set(FiftyYearTrainingRunner.TRAINING_PHASES)
        assert era_report["hardware"] == "SKIPPED — software-only run"
        assert 0.0 <= era_report["eval_score"] <= 1.0
    out = capsys.readouterr().out
    assert "SOFTWARE ONLY" in out
    assert "skipped — hardware" in out


def test_failure_memory_grows_across_eras_forever():
    runner = FiftyYearTrainingRunner(software_only=True)
    summary = runner.run_all()
    totals = [r["phases"]["FAILURE_MEMORY"]["total_forever"] for r in summary["eras"]]
    # E_{t+1} = E_t ∪ F_t — strictly non-decreasing across all 50 years
    assert totals == sorted(totals)
    assert totals[-1] == summary["failure_memory_forever"]["total"]
    assert totals[-1] >= 15  # 3 failures per era x 5 eras
