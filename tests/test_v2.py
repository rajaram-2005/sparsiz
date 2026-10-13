"""Tests for sparsiz.v2 — Version 2 unified omni runtime."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sparsiz.v2 import (
    OmniV2, DeviceTier, TierRouter, V2Result, detect_tier,
    V2Release, VERSION, VERSION_HISTORY, compatible,
)
from sparsiz.v2.omni_v2 import TIER_TABLE


def test_version_is_2():
    assert VERSION == "2.0.0"
    assert VERSION_HISTORY[-1]["version"] == "2.0.0"


def test_package_version_matches():
    import sparsiz
    assert sparsiz.__version__ == VERSION


def test_release_manifest_hash_stable():
    r = V2Release()
    assert r.release_hash == V2Release().release_hash
    m = r.manifest()
    assert m["version"] == "2.0.0"
    assert set(m["components"]) >= {"skills", "mobile", "datacenter", "v2_runtime"}


def test_compatibility_rules():
    assert compatible("1.0.0")
    assert compatible("1.2.0")
    assert compatible("2.0.0")
    assert not compatible("0.6.0")      # v0.x must migrate through v1
    assert not compatible("3.0.0")      # future major not compatible


def test_detect_tier_ladder():
    assert detect_tier(0.4) == DeviceTier.NANO_IOT
    assert detect_tier(5) == DeviceTier.SMALL_PHONE
    assert detect_tier(512) == DeviceTier.PHONE
    assert detect_tier(8_192) == DeviceTier.EDGE
    assert detect_tier(98_304) == DeviceTier.WORKSTATION
    assert detect_tier(1_048_576) == DeviceTier.DATACENTER
    assert detect_tier(104_857_600) == DeviceTier.HYPERSCALE
    assert detect_tier() in DeviceTier  # host auto-detect never crashes


def test_tier_table_covers_all_tiers():
    assert set(TIER_TABLE) == set(DeviceTier)
    assert TIER_TABLE[DeviceTier.NANO_IOT].max_memory_mb == 0.5
    assert TIER_TABLE[DeviceTier.HYPERSCALE].max_params == 100_000_000_000_000


def test_router_resolves_every_tier():
    router = TierRouter()
    for tier in DeviceTier:
        resolved = router.resolve(tier)
        assert router.available(resolved)


def test_run_all_tiers_released_and_audited():
    v2 = OmniV2()
    for tier in DeviceTier:
        result = v2.run("diagnose motor fault", tier=tier)
        assert isinstance(result, V2Result)
        assert 0.0 <= result.gate_score <= 1.0
        assert result.audit_hash and len(result.audit_hash) == 16
        assert result.latency_ms >= 0
    status = v2.status()
    assert status["runs"] == len(DeviceTier)
    assert status["version"] == "2.0.0"


def test_failure_memory_forever():
    v2 = OmniV2()
    before = len(v2.failure_memory)
    # Force a failure by scoring an error output through the gate
    score = v2._gate({"error": "injected"})
    assert score < OmniV2.GATE_THRESHOLD
    # Normal run should not shrink memory (E_{t+1} = E_t ∪ F_t)
    v2.run("normal task")
    assert len(v2.failure_memory) >= before
