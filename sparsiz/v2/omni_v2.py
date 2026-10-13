"""
OmniV2 — Unified Omni Runtime (Version 2)
v2.0.0 — One entry point, every tier, every engine, every skill

V2 unifies the entire stack behind a single orchestrator:

    TASK -> detect_tier() -> TierRouter -> engine
        NANO_IOT / SMALL_PHONE / PHONE  -> PhoneAGI   (10M-1B INT4, 5MB-0.5GB)
        EDGE / WORKSTATION              -> AGICore + OmniSkills (local fabric)
        DATACENTER / HYPERSCALE         -> DataCenterAGI (7B-100T MoE, BF16/FP8)

Design rules carried over from V1:
- PREMSOTH-style gate before any result is released (score threshold)
- Failure memory E_{t+1} = E_t ∪ F_t — every failure stored forever
- Forever-use: every run is hashed and auditable
- Graceful degradation: if a bigger engine is unavailable, route down a tier
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import time

# Engines from previous waves — all optional, V2 degrades gracefully.
try:
    from ..mobile.phone_agi import PhoneAGI, PhoneSpecs
except ImportError:  # pragma: no cover
    PhoneAGI = PhoneSpecs = None

try:
    from ..datacenter.datacenter_agi import DataCenterAGI, DataCenterSpecs
except ImportError:  # pragma: no cover
    DataCenterAGI = DataCenterSpecs = None

try:
    from ..agi.agi_core import AGICore
except ImportError:  # pragma: no cover
    AGICore = None

try:
    from ..skills.omni_skills import OmniSkills
except ImportError:  # pragma: no cover
    OmniSkills = None


class DeviceTier(Enum):
    """The full V2 device ladder — 0.5MB nano IoT to 100TB hyperscale."""
    NANO_IOT = "NANO_IOT"            # 1M params, 0.5MB — sensors, MCUs
    SMALL_PHONE = "SMALL_PHONE"      # 10M params, 5MB — entry phones
    PHONE = "PHONE"                  # 100M-1B INT4, 0.5GB — flagship phones
    EDGE = "EDGE"                    # 1B-7B, edge boxes / Raspberry Pi class
    WORKSTATION = "WORKSTATION"      # 7B-70B, single GPU workstation
    DATACENTER = "DATACENTER"        # 70B-1T MoE, 1TB — H100 x8-x64
    HYPERSCALE = "HYPERSCALE"        # 1T-100T MoE, 100TB — 50-year roadmap tier


@dataclass
class TierSpecs:
    tier: DeviceTier
    max_params: int                  # parameter budget
    max_memory_mb: float             # memory budget
    engine: str                      # which engine serves this tier
    quantization: str

    @property
    def model_size_mb(self) -> float:
        # INT4 = 0.5 bytes/param for small tiers, BF16 = 2 bytes/param above EDGE
        bytes_per_param = 0.5 if self.quantization == "INT4" else 2.0
        return self.max_params * bytes_per_param / 1e6


TIER_TABLE: Dict[DeviceTier, TierSpecs] = {
    DeviceTier.NANO_IOT:    TierSpecs(DeviceTier.NANO_IOT,    1_000_000,           0.5,        "phone",      "INT4"),
    DeviceTier.SMALL_PHONE: TierSpecs(DeviceTier.SMALL_PHONE, 10_000_000,          5.0,        "phone",      "INT4"),
    DeviceTier.PHONE:       TierSpecs(DeviceTier.PHONE,       1_000_000_000,       512.0,      "phone",      "INT4"),
    DeviceTier.EDGE:        TierSpecs(DeviceTier.EDGE,        7_000_000_000,       8_192.0,    "local",      "INT4"),
    DeviceTier.WORKSTATION: TierSpecs(DeviceTier.WORKSTATION, 70_000_000_000,      98_304.0,   "local",      "BF16"),
    DeviceTier.DATACENTER:  TierSpecs(DeviceTier.DATACENTER,  1_000_000_000_000,   1_048_576.0, "datacenter", "FP8"),
    DeviceTier.HYPERSCALE:  TierSpecs(DeviceTier.HYPERSCALE,  100_000_000_000_000, 104_857_600.0, "datacenter", "FP8"),
}


def detect_tier(available_memory_mb: Optional[float] = None) -> DeviceTier:
    """Auto-detect the best tier for this host from available memory.

    If memory can't be probed, default to EDGE (safe local fabric).
    """
    if available_memory_mb is None:
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        available_memory_mb = int(line.split()[1]) / 1024.0
                        break
        except (OSError, ValueError):  # pragma: no cover
            return DeviceTier.EDGE
    if available_memory_mb is None:
        return DeviceTier.EDGE
    if available_memory_mb < 1:
        return DeviceTier.NANO_IOT
    if available_memory_mb < 64:
        return DeviceTier.SMALL_PHONE
    if available_memory_mb < 2_048:
        return DeviceTier.PHONE
    if available_memory_mb < 32_768:
        return DeviceTier.EDGE
    if available_memory_mb < 262_144:
        return DeviceTier.WORKSTATION
    if available_memory_mb < 10_485_760:
        return DeviceTier.DATACENTER
    return DeviceTier.HYPERSCALE


@dataclass
class V2Result:
    """Audited, hashed, forever-use result record."""
    task: str
    tier: DeviceTier
    engine: str
    output: Dict[str, Any]
    gate_score: float
    released: bool
    latency_ms: float
    timestamp: float = field(default_factory=time.time)

    @property
    def audit_hash(self) -> str:
        payload = f"{self.task}|{self.tier.value}|{self.engine}|{self.released}|{self.timestamp}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "tier": self.tier.value,
            "engine": self.engine,
            "output": self.output,
            "gate_score": round(self.gate_score, 4),
            "released": self.released,
            "latency_ms": round(self.latency_ms, 3),
            "audit_hash": self.audit_hash,
        }


class TierRouter:
    """Routes a task to the right engine for a tier, degrading gracefully."""

    # Downgrade ladder when an engine is unavailable on this host.
    FALLBACK: Dict[DeviceTier, DeviceTier] = {
        DeviceTier.HYPERSCALE: DeviceTier.DATACENTER,
        DeviceTier.DATACENTER: DeviceTier.WORKSTATION,
        DeviceTier.WORKSTATION: DeviceTier.EDGE,
        DeviceTier.EDGE: DeviceTier.PHONE,
        DeviceTier.PHONE: DeviceTier.SMALL_PHONE,
        DeviceTier.SMALL_PHONE: DeviceTier.NANO_IOT,
    }

    def __init__(self):
        self.phone = PhoneAGI() if PhoneAGI else None
        self.datacenter = DataCenterAGI() if DataCenterAGI else None
        self.agi_core = AGICore() if AGICore else None
        self.skills = OmniSkills() if OmniSkills else None

    def engine_for(self, tier: DeviceTier) -> str:
        return TIER_TABLE[tier].engine

    def available(self, tier: DeviceTier) -> bool:
        engine = self.engine_for(tier)
        if engine == "phone":
            return self.phone is not None
        if engine == "datacenter":
            return self.datacenter is not None
        return self.agi_core is not None or self.skills is not None

    def resolve(self, tier: DeviceTier) -> DeviceTier:
        """Walk down the ladder until an available tier is found."""
        current = tier
        seen = set()
        while not self.available(current):
            if current in seen or current not in self.FALLBACK:
                raise RuntimeError("No V2 engine available on this host")
            seen.add(current)
            current = self.FALLBACK[current]
        return current

    def dispatch(self, task: str, tier: DeviceTier, context: Dict[str, Any]) -> Dict[str, Any]:
        engine = self.engine_for(tier)
        if engine == "phone" and self.phone:
            mode = context.get("mode", "AIR_GAPPED")
            return self.phone.run(task, mode=mode, context=context)
        if engine == "datacenter" and self.datacenter:
            mode = context.get("mode", "SINGLE_NODE")
            return self.datacenter.run(task, mode=mode, context=context)
        if self.agi_core:
            return self.agi_core.run({"task": task, **context})
        if self.skills:
            results = self.skills.execute_query(task, context)
            return {"skill_results": results, "count": len(results)}
        raise RuntimeError("No V2 engine available on this host")


class OmniV2:
    """Version 2 — the unified omni runtime.

    Single entry point over every engine from v1.0.0-v1.2.0 plus the 50-year
    roadmap tiers. Auto-detects the device tier, routes to the right engine,
    gates every result PREMSOTH-style, and keeps failure memory forever:
    E_{t+1} = E_t ∪ F_t.
    """

    GATE_THRESHOLD = 0.5

    def __init__(self, tier: Optional[DeviceTier] = None):
        self.tier = tier or detect_tier()
        self.router = TierRouter()
        self.failure_memory: List[Dict[str, Any]] = []   # E_t — forever
        self.audit_log: List[Dict[str, Any]] = []        # forever-use audit

    @property
    def specs(self) -> TierSpecs:
        return TIER_TABLE[self.tier]

    def _gate(self, output: Dict[str, Any]) -> float:
        """PREMSOTH-style release gate: score the engine output."""
        score = 0.5
        for key in ("confidence", "gate_score", "score"):
            if isinstance(output.get(key), (int, float)):
                score = float(output[key])
                break
        else:
            # Structural heuristic: non-empty structured output passes.
            if output and not output.get("error"):
                score = 0.9
            elif output.get("error"):
                score = 0.1
        return max(0.0, min(1.0, score))

    def run(self, task: str, context: Optional[Dict[str, Any]] = None,
            tier: Optional[DeviceTier] = None) -> V2Result:
        context = dict(context or {})
        requested = tier or self.tier
        t0 = time.perf_counter()
        resolved = self.router.resolve(requested)
        try:
            output = self.router.dispatch(task, resolved, context)
        except Exception as exc:  # failure becomes permanent memory
            output = {"error": str(exc)}
        latency_ms = (time.perf_counter() - t0) * 1000.0

        score = self._gate(output)
        released = score >= self.GATE_THRESHOLD
        result = V2Result(
            task=task, tier=resolved, engine=self.router.engine_for(resolved),
            output=output, gate_score=score, released=released,
            latency_ms=latency_ms,
        )
        self.audit_log.append(result.to_dict())
        if not released:
            # E_{t+1} = E_t ∪ F_t
            self.failure_memory.append({
                "task": task, "tier": resolved.value,
                "score": score, "output": output, "ts": result.timestamp,
            })
        return result

    def status(self) -> Dict[str, Any]:
        return {
            "version": "2.0.0",
            "tier": self.tier.value,
            "engine": self.router.engine_for(self.tier),
            "tier_table": {t.value: {
                "max_params": s.max_params,
                "max_memory_mb": s.max_memory_mb,
                "engine": s.engine,
                "quantization": s.quantization,
            } for t, s in TIER_TABLE.items()},
            "engines_available": {
                "phone": self.router.phone is not None,
                "datacenter": self.router.datacenter is not None,
                "agi_core": self.router.agi_core is not None,
                "skills": self.router.skills is not None,
            },
            "runs": len(self.audit_log),
            "failures_remembered": len(self.failure_memory),
        }
