"""
V2 Omni Demo — Version 2 unified runtime end-to-end
v2.0.0 — one entry point: nano-IoT 0.5MB -> hyperscale 100TB

Run: python examples/v2_omni_demo.py
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sparsiz.v2 import OmniV2, DeviceTier, detect_tier, V2Release, VERSION, compatible


def main():
    print("=" * 70)
    print(f"Sparsiz VERSION 2 — Unified Omni Runtime v{VERSION}")
    print("=" * 70)

    # 1. Release manifest — versioned, hashed, forever-use
    release = V2Release()
    manifest = release.manifest()
    print(f"\n[release] v{manifest['version']} ({manifest['codename']}) hash={manifest['hash']}")
    for comp, ver in manifest["components"].items():
        print(f"  component {comp:<14} v{ver}  compatible={compatible(ver)}")

    # 2. Tier auto-detection
    tier = detect_tier()
    print(f"\n[tier] auto-detected: {tier.value}")

    v2 = OmniV2()
    status = v2.status()
    print(f"[engines] {status['engines_available']}")

    # 3. Run the same task on every tier of the ladder
    task = "diagnose motor fault from vibration telemetry"
    print(f"\n[task] {task!r} across the full V2 ladder:")
    for t in DeviceTier:
        result = v2.run(task, tier=t)
        print(f"  {t.value:<12} -> engine={result.engine:<10} "
              f"gate={result.gate_score:.2f} released={result.released} "
              f"latency={result.latency_ms:.2f}ms audit={result.audit_hash}")

    # 4. Final status — audit log + failure memory E_{t+1} = E_t ∪ F_t
    status = v2.status()
    print(f"\n[status] runs={status['runs']} "
          f"failures_remembered={status['failures_remembered']}")
    print("\n[tier table]")
    print(json.dumps(status["tier_table"], indent=2))
    print("\nVERSION 2 OK")


if __name__ == "__main__":
    main()
