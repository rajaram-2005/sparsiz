"""
Sparsiz V2 Release Registry
v2.0.0 — Version 2: formal release metadata, version history, compatibility

Every release is permanent (forever-use): versioned, hashed, auditable.
E_{t+1} = E_t ∪ F_t — every validated failure of a previous release becomes
a permanent evaluation signal for the next one.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import hashlib
import time

VERSION = "2.0.0"
CODENAME = "omni-v2"

# Full release line — v0.x prototype phases, v1.x omni waves, v2.0.0 unified.
VERSION_HISTORY: List[Dict[str, str]] = [
    {"version": "0.1.0", "name": "phase-0-simulator", "summary": "Compute grid simulator, Y-Bus, thermal, routing baselines"},
    {"version": "0.2.0", "name": "saram", "summary": "SARAM encoder/decoder with physics-informed loss"},
    {"version": "0.3.0", "name": "faisanth", "summary": "FAISANTH cost-optimized routing vs baselines"},
    {"version": "0.4.0", "name": "multi-agent-premsoth", "summary": "Multi-agent system + PREMSOTH BFT verification"},
    {"version": "0.5.0", "name": "makesh-ebpf", "summary": "MAKESH telemetry + eBPF monitoring prototype"},
    {"version": "0.6.0", "name": "v1-prototype", "summary": "V1 end-to-end research prototype"},
    {"version": "1.0.0", "name": "agi-omni-skills", "summary": "100+ field skills, forever-use registry"},
    {"version": "1.1.0", "name": "agi-phone-omni", "summary": "Phone AGI 10M-1B INT4, 5MB-0.5GB, offline+online"},
    {"version": "1.2.0", "name": "agi-datacenter-omni", "summary": "Data-center AGI 7B-1T MoE, BF16/FP8, H100 x8-x64"},
    {"version": "2.0.0", "name": "omni-v2", "summary": "Version 2: unified omni runtime, tier auto-routing nano-IoT 0.5MB to hyperscale 100TB, single entry point, 50-year roadmap integrated"},
]


@dataclass
class V2Release:
    """Immutable release record — versioned, hashed, audited, forever-use."""
    version: str = VERSION
    codename: str = CODENAME
    released_at: float = field(default_factory=time.time)
    components: Dict[str, str] = field(default_factory=lambda: {
        "skills": "1.0.0",
        "mobile": "1.1.0",
        "datacenter": "1.2.0",
        "roadmap_50yr": "2.0",
        "v2_runtime": VERSION,
    })

    @property
    def release_hash(self) -> str:
        payload = f"{self.version}|{self.codename}|" + "|".join(
            f"{k}={v}" for k, v in sorted(self.components.items())
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def manifest(self) -> Dict[str, object]:
        return {
            "version": self.version,
            "codename": self.codename,
            "hash": self.release_hash,
            "components": dict(self.components),
            "history": VERSION_HISTORY,
        }


def _parse(version: str) -> Tuple[int, ...]:
    parts = []
    for p in version.split("-")[0].split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def compatible(other_version: str, minimum: str = "1.0.0") -> bool:
    """True if `other_version` can interoperate with the V2 runtime.

    Rule: anything >= `minimum` (default 1.0.0, first omni wave) and with a
    major version <= current major is compatible. v0.x prototypes must be
    migrated through v1 first.
    """
    v, lo, cur = _parse(other_version), _parse(minimum), _parse(VERSION)
    return lo <= v and v[0] <= cur[0]
