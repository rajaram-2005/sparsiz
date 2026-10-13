"""
Sparsiz V2 — Unified Omni Runtime
v2.0.0 — Version 2: One entry point for every tier, every skill, every engine

V2 unifies everything shipped in v1.0.0 (omni skills), v1.1.0 (phone AGI),
v1.2.0 (data-center AGI) and the v2.0 50-year roadmap behind a single
orchestrator with automatic device-tier detection and routing:

    NANO_IOT (0.5MB) -> SMALL_PHONE (5MB) -> PHONE -> EDGE -> WORKSTATION
        -> DATACENTER (1TB) -> HYPERSCALE (100TB, 100T MoE)

Usage:
    from sparsiz.v2 import OmniV2
    v2 = OmniV2()                      # auto-detect tier
    result = v2.run("diagnose motor fault from vibration telemetry")
"""

from .omni_v2 import (
    OmniV2,
    DeviceTier,
    TierSpecs,
    TierRouter,
    V2Result,
    detect_tier,
)
from .release import (
    V2Release,
    VERSION,
    VERSION_HISTORY,
    compatible,
)

__all__ = [
    "OmniV2",
    "DeviceTier",
    "TierSpecs",
    "TierRouter",
    "V2Result",
    "detect_tier",
    "V2Release",
    "VERSION",
    "VERSION_HISTORY",
    "compatible",
]
