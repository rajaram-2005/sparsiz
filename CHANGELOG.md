# Changelog — The Last Dance (Sparsiz)

All notable changes to this project. Every release is forever-use:
versioned, hashed, auditable. E_{t+1} = E_t ∪ F_t.

## v2.0.0 — omni-v2 (2026-10-13) — VERSION 2

**Version 2: the unified omni runtime.** One entry point over everything
shipped in v1.0.0–v1.2.0 plus the 50-year roadmap tiers.

### Added
- `sparsiz.v2` package — the Version 2 unified runtime:
  - `OmniV2` — single entry point: `OmniV2().run(task)` with automatic
    device-tier detection and PREMSOTH-style release gating.
  - `DeviceTier` ladder — NANO_IOT (1M params, 0.5MB) → SMALL_PHONE (10M, 5MB)
    → PHONE (1B INT4, 0.5GB) → EDGE (7B) → WORKSTATION (70B BF16)
    → DATACENTER (1T MoE FP8, 1TB) → HYPERSCALE (100T MoE, 100TB).
  - `TierRouter` — routes each tier to the right engine (PhoneAGI,
    AGICore + OmniSkills, DataCenterAGI) with graceful downgrade when an
    engine is unavailable on the host.
  - `detect_tier()` — auto-detects tier from host memory (`/proc/meminfo`).
  - `V2Result` — hashed, audited, forever-use result records.
  - Failure memory forever: every gated-out result is stored permanently
    (E_{t+1} = E_t ∪ F_t).
  - `V2Release` / `VERSION_HISTORY` / `compatible()` — formal release
    registry with stable release hashes and compatibility rules
    (v1.x interoperates with V2; v0.x must migrate through v1).
- `examples/v2_omni_demo.py` — runnable end-to-end Version 2 demo.
- `tests/test_v2.py` — full test coverage for the V2 runtime.
- This `CHANGELOG.md`.

### Changed
- Version aligned to **2.0.0** everywhere: `setup.py`, `sparsiz/__init__.py`,
  workspace metadata, README, ROADMAP release plan.
  (Previously `setup.py` said 0.6.0 while the package said
  `2.0-agi-50-year-roadmap`.)

## v2.0-agi-50-year-roadmap (2026-09-28)
- 50-year feature roadmap (2026–2076), 12 backlogs beyond
  OpenAI/Claude/Gemini/Llama, 1M 0.5MB nano-IoT → 100T MoE 100TB,
  formal verification 14 → 1000+, bare-metal own stack,
  failure memory forever. Docs: `docs/` Documents A–J, drawings Fig 61–70.

## v1.2.0 — agi-datacenter-omni
- Data-center AGI: 7B–1T MoE, BF16/FP8, H100 x8–x64, data-center HAL,
  scaling + quantization engines, data-center local AI registry/router.

## v1.1.0 — agi-phone-omni
- Phone AGI: 10M–1B INT4 GGUF, 5MB–0.5GB, phone CPU/NPU HAL,
  execution modes AIR_GAPPED → DISTRIBUTED_HYBRID, distillation +
  quantization engines, all skills runnable on phone.

## v1.0.0 — agi-omni-skills
- 100+ field skills, forever-use skill registry (versioned, hashed,
  audited), skill engine, omni-skills orchestrator.

## v0.6.0 — V1 prototype end-to-end
- Full V1 research prototype: SARAM → FAISANTH → agents → PREMSOTH →
  RAJAM core with MAKESH observation.

## v0.1.0 – v0.5.0 — Phases 0–5
- Compute-grid simulator, SARAM, FAISANTH, multi-agent + PREMSOTH,
  MAKESH + eBPF (see ROADMAP.md phases).
